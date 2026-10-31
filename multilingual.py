"""Voice + language layer. The agent itself always works in English, so the deterministic
triage rules keep working. Pipeline:
  voice/text (any language) -> English -> agent -> native language -> text + voice."""
import os
import re
import tempfile
from functools import lru_cache

from config import WHISPER_MODEL, NLLB_MODEL, EMERGENCY_NUMBER

# English + 6 Indian languages.  name: (Whisper/ISO code, NLLB-200 code, gTTS code)
# To add a language, add one line here (and its disclaimer below).
LANGS = {
    "English":   ("en", "eng_Latn", "en"),
    "Hindi":     ("hi", "hin_Deva", "hi"),
    "Telugu":    ("te", "tel_Telu", "te"),
    "Tamil":     ("ta", "tam_Taml", "ta"),
    "Kannada":   ("kn", "kan_Knda", "kn"),
    "Malayalam": ("ml", "mal_Mlym", "ml"),
    "Bengali":   ("bn", "ben_Beng", "bn"),
}
BY_CODE = {v[0]: k for k, v in LANGS.items()}

# Fixed, pre-written disclaimers (never depend on machine translation). {num} = EMERGENCY_NUMBER.
# NOTE: have a native speaker review these before real use.
_DISCLAIMER_TEMPLATES = {
    "en": "Not a substitute for professional medical advice. This is general information only. In an emergency, call {num}.",
    "hi": "यह पेशेवर चिकित्सा सलाह का विकल्प नहीं है। यह केवल सामान्य जानकारी है। आपातकाल में {num} पर कॉल करें।",
    "te": "ఇది వృత్తిపరమైన వైద్య సలహాకు ప్రత్యామ్నాయం కాదు. ఇది సాధారణ సమాచారం మాత్రమే. అత్యవసర పరిస్థితిలో {num} కు కాల్ చేయండి.",
    "ta": "இது தொழில்முறை மருத்துவ ஆலோசனைக்கு மாற்று அல்ல. இது பொதுவான தகவல் மட்டுமே. அவசர நிலையில் {num} ஐ அழைக்கவும்.",
    "kn": "ಇದು ವೃತ್ತಿಪರ ವೈದ್ಯಕೀಯ ಸಲಹೆಗೆ ಪರ್ಯಾಯವಲ್ಲ. ಇದು ಸಾಮಾನ್ಯ ಮಾಹಿತಿ ಮಾತ್ರ. ತುರ್ತು ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ {num} ಗೆ ಕರೆ ಮಾಡಿ.",
    "ml": "ഇത് പ്രൊഫഷണൽ വൈദ്യോപദേശത്തിന് പകരമല്ല. ഇത് പൊതുവായ വിവരങ്ങൾ മാത്രമാണ്. അടിയന്തര ഘട്ടത്തിൽ {num} എന്ന നമ്പറിൽ വിളിക്കുക.",
    "bn": "এটি পেশাদার চিকিৎসা পরামর্শের বিকল্প নয়। এটি শুধুমাত্র সাধারণ তথ্য। জরুরি অবস্থায় {num} নম্বরে কল করুন।",
}
DISCLAIMERS = {k: v.format(num=EMERGENCY_NUMBER) for k, v in _DISCLAIMER_TEMPLATES.items()}

_MAX_TTS_CHARS = 3000


# ---------- Language detection for typed text ----------
# Each supported language has its own script, so counting characters is exact and needs no model.
_SCRIPTS = {
    "te": r"[\u0C00-\u0C7F]", "kn": r"[\u0C80-\u0CFF]", "ta": r"[\u0B80-\u0BFF]",
    "ml": r"[\u0D00-\u0D7F]", "bn": r"[\u0980-\u09FF]", "hi": r"[\u0900-\u097F]",
}


def detect_language(text: str) -> str:
    """Majority script wins; Latin / unknown text is treated as English."""
    counts = {code: len(re.findall(pat, text)) for code, pat in _SCRIPTS.items()}
    code, n = max(counts.items(), key=lambda kv: kv[1])
    return code if n >= 2 else "en"


# ---------- Speech to text (Whisper, 99 languages, auto-detects language) ----------
@lru_cache(maxsize=1)
def _whisper():
    from faster_whisper import WhisperModel
    device = "cuda" if _has_cuda() else "cpu"
    compute = "float16" if device == "cuda" else "int8"
    return WhisperModel(os.getenv("WHISPER_MODEL", WHISPER_MODEL), device=device, compute_type=compute)


def _has_cuda() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


def speech_to_text(audio_path: str, language: str | None = None):
    """Returns (text, detected_language_code)."""
    model = _whisper()
    if language is None:
        # Whisper may guess a language we do not support (e.g. Urdu for Hindi speech).
        # Take the most likely SUPPORTED language and force it.
        _, _, probs = model.detect_language(audio_path)
        ranked = sorted(((p, l) for l, p in probs if l in BY_CODE), reverse=True)
        language = ranked[0][1] if ranked else "en"
    segments, info = model.transcribe(audio_path, language=language, vad_filter=True, beam_size=5)
    text = " ".join(s.text.strip() for s in segments).strip()
    return text, language


# ---------- Translation (NLLB-200, runs locally) ----------
@lru_cache(maxsize=1)
def _translator():
    from transformers import pipeline
    device = 0 if _has_cuda() else -1
    return pipeline("translation", model=os.getenv("NLLB_MODEL", NLLB_MODEL), device=device)


def strip_markdown(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)          # [label](url) -> label
    text = re.sub(r"[*_`#>|]+", "", text)
    text = re.sub(r"^\s*-{3,}\s*$", "", text, flags=re.M)
    text = re.sub(r"^\s*(?:[-•]|\d+[.)])\s+", "", text, flags=re.M)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


@lru_cache(maxsize=256)
def _translate_sentence_batch(parts: tuple, src: str, tgt: str) -> tuple:
    tr = _translator()
    out = tr(list(parts), src_lang=src, tgt_lang=tgt, max_length=400, batch_size=8)
    return tuple(r["translation_text"] for r in out)


def translate(text: str, src: str, tgt: str) -> str:
    """src / tgt are NLLB codes, e.g. 'kan_Knda' -> 'eng_Latn'. Sentence by sentence for accuracy."""
    if src == tgt or not text.strip():
        return text
    lines_out = []
    for line in text.split("\n"):
        if not line.strip():
            lines_out.append("")
            continue
        parts = tuple(p for p in re.split(r"(?<=[.!?।])\s+", line) if p.strip())
        lines_out.append(" ".join(_translate_sentence_batch(parts, src, tgt)))
    return "\n".join(lines_out)


# ---------- Text to speech (gTTS needs internet) ----------
def _split_for_tts(text: str, limit: int = 450) -> list[str]:
    chunks, cur = [], ""
    for s in re.split(r"(?<=[.!?।])\s+", text):
        if len(cur) + len(s) + 1 > limit and cur:
            chunks.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        chunks.append(cur)
    return chunks


def text_to_speech(text: str, lang_code: str):
    """Returns an mp3 path, or None if speech could not be generated."""
    text = strip_markdown(text)[:_MAX_TTS_CHARS]
    if not text:
        return None
    try:
        from gtts import gTTS
        gtts_code = LANGS[BY_CODE.get(lang_code, "English")][2]
        path = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
        with open(path, "wb") as f:  # chunked so long answers never hit gTTS limits
            for chunk in _split_for_tts(text):
                gTTS(text=chunk, lang=gtts_code).write_to_fp(f)
        return path
    except Exception as e:
        print("TTS failed (needs internet):", e)
        return None


if __name__ == "__main__":
    for s in ["मुझे तीन दिन से बुखार है", "నాకు మూడు రోజులుగా జ్వరం ఉంది", "எனக்கு காய்ச்சல்", "I have a fever"]:
        print(detect_language(s), "<-", s)
    print(translate("मुझे तीन दिन से बुखार है", "hin_Deva", "eng_Latn"))
    print(text_to_speech("आपको डॉक्टर से मिलना चाहिए", "hi"))
    print(speech_to_text("sample.wav"))
