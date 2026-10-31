"""Tools shared by the local agent (agent.py) and the MCP server (mcp_server.py).
The triage and specialist logic is plain deterministic Python: no LLM involved."""
from langchain_core.tools import tool

LEVELS = ["self-care", "see a doctor", "urgent"]  # ordered by severity

# Rule 1: any red flag => urgent (checked first)
RED_FLAGS = [
    "chest pain", "chest tightness", "difficulty breathing", "shortness of breath",
    "can't breathe", "cannot breathe", "unconscious", "fainted", "seizure",
    "face drooping", "slurred speech", "sudden weakness", "severe bleeding",
    "vomiting blood", "coughing blood", "suicidal", "overdose", "poisoning",
    "swollen tongue", "swelling of the face", "anaphylaxis", "worst headache",
    "stiff neck", "confusion", "blue lips", "sudden vision loss", "left arm pain",
]

# Rule 2: keyword -> (base level, max self-care days, specialty)
CONDITIONS = {
    "headache":        ("self-care", 3, "General physician (Neurology if recurrent)"),
    "migraine":        ("see a doctor", 0, "Neurology"),
    "common cold":     ("self-care", 7, "General physician"),
    "runny nose":      ("self-care", 7, "General physician (ENT if persistent)"),
    "sore throat":     ("self-care", 5, "ENT specialist"),
    "cough":           ("self-care", 14, "General physician (Pulmonology if persistent)"),
    "mild fever":      ("self-care", 3, "General physician"),
    "high fever":      ("see a doctor", 0, "General physician"),
    "fever":           ("self-care", 3, "General physician"),
    "nausea":          ("self-care", 2, "General physician (Gastroenterology if persistent)"),
    "diarrhea":        ("self-care", 3, "Gastroenterology"),
    "constipation":    ("self-care", 7, "Gastroenterology"),
    "heartburn":       ("self-care", 14, "Gastroenterology"),
    "back pain":       ("self-care", 7, "Orthopedics"),
    "muscle strain":   ("self-care", 7, "Orthopedics / Physiotherapy"),
    "minor cut":       ("self-care", 3, "General physician"),
    "insect bite":     ("self-care", 3, "General physician (Dermatology if spreading)"),
    "rash":            ("self-care", 5, "Dermatology"),
    "ear pain":        ("see a doctor", 0, "ENT specialist"),
    "red eye":         ("see a doctor", 0, "Ophthalmology"),
    "toothache":       ("see a doctor", 0, "Dentist"),
    "urinary burning": ("see a doctor", 0, "General physician (Urology if recurrent)"),
    "abdominal pain":  ("see a doctor", 0, "Gastroenterology"),
    "stomach pain":    ("see a doctor", 0, "Gastroenterology"),
    "joint pain":      ("see a doctor", 0, "Orthopedics / Rheumatology"),
    "dizziness":       ("see a doctor", 0, "General physician (Neurology / ENT)"),
    "palpitations":    ("see a doctor", 0, "Cardiology"),
    "anxiety":         ("see a doctor", 0, "Psychiatry / Psychology"),
    "insomnia":        ("self-care", 14, "General physician (Psychiatry if persistent)"),
    "blood in stool":  ("see a doctor", 0, "Gastroenterology"),
    "blood in urine":  ("see a doctor", 0, "Urology"),
    "swollen leg":     ("see a doctor", 0, "Cardiology / Vascular surgery"),
    "wheezing":        ("see a doctor", 0, "Pulmonology"),
    "excessive thirst": ("see a doctor", 0, "Endocrinology"),
    "frequent urination": ("see a doctor", 0, "General physician (Endocrinology / Urology)"),
    "yellow eyes":     ("see a doctor", 0, "Gastroenterology / Hepatology"),
    "jaundice":        ("see a doctor", 0, "Gastroenterology / Hepatology"),
    "night sweats":    ("see a doctor", 0, "General physician (Pulmonology)"),
    "weight loss":     ("see a doctor", 0, "General physician"),
    "chills":          ("see a doctor", 0, "General physician"),
    "fatigue":         ("self-care", 7, "General physician (Endocrinology / Hematology if persistent)"),
    "low mood":        ("see a doctor", 0, "Psychiatry / Psychology"),
    "depressed":       ("see a doctor", 0, "Psychiatry / Psychology"),
    "joint swelling":  ("see a doctor", 0, "Orthopedics / Rheumatology"),
    "blurred vision":  ("see a doctor", 0, "Ophthalmology"),
    "sneezing":        ("self-care", 7, "General physician (ENT / Allergy)"),
    "itchy eyes":      ("self-care", 7, "Ophthalmology / Allergy"),
}

SPECIALISTS = {
    "chest": "Cardiology", "palpitation": "Cardiology", "heart": "Cardiology",
    "swollen leg": "Cardiology / Vascular surgery",
    "breath": "Pulmonology", "cough": "Pulmonology", "asthma": "Pulmonology",
    "stroke": "Neurology", "seizure": "Neurology", "headache": "Neurology",
    "migraine": "Neurology", "face drooping": "Neurology", "slurred": "Neurology",
    "stomach": "Gastroenterology", "abdominal": "Gastroenterology",
    "diarrhea": "Gastroenterology", "vomit": "Gastroenterology",
    "stool": "Gastroenterology", "heartburn": "Gastroenterology",
    "urin": "Urology", "kidney": "Nephrology / Urology",
    "rash": "Dermatology", "skin": "Dermatology", "bite": "Dermatology",
    "ear": "ENT specialist", "throat": "ENT specialist", "nose": "ENT specialist",
    "eye": "Ophthalmology", "tooth": "Dentist",
    "joint": "Orthopedics / Rheumatology", "back pain": "Orthopedics", "bone": "Orthopedics",
    "anxiety": "Psychiatry", "depress": "Psychiatry", "suicid": "Psychiatry (emergency)",
    "pregnan": "Obstetrics & Gynecology", "period": "Obstetrics & Gynecology",
    "diabetes": "Endocrinology", "thyroid": "Endocrinology",
    "overdose": "Emergency medicine / Poison control",
    "poison": "Emergency medicine / Poison control",
    "bleeding": "Emergency medicine",
    "wheez": "Pulmonology", "thirst": "Endocrinology",
    "jaundice": "Gastroenterology / Hepatology", "yellow eyes": "Gastroenterology / Hepatology",
    "weight loss": "General physician", "night sweats": "General physician (Pulmonology)",
    "low mood": "Psychiatry", "depressed": "Psychiatry",
    "vision": "Ophthalmology", "sneez": "ENT specialist / Allergy",
}


def _bump(level: str) -> str:
    return LEVELS[min(LEVELS.index(level) + 1, len(LEVELS) - 1)]


def triage_logic(symptom: str, duration_days: int = 0, severity: str = "mild") -> dict:
    text = symptom.lower().strip()

    for flag in RED_FLAGS:  # Rule 1
        if flag in text:
            return {"level": "urgent", "matched": flag,
                    "reason": f"Red-flag symptom '{flag}' needs immediate medical attention."}

    for key in sorted(CONDITIONS, key=len, reverse=True):  # Rule 2: longest match wins
        if key in text:
            base, max_days, _ = CONDITIONS[key]
            level, reasons = base, [f"'{key}' is rated '{base}' in the rule table."]
            if level == "self-care" and duration_days > max_days:  # Rule 3
                level = "see a doctor"
                reasons.append(f"Lasting {duration_days} days exceeds the {max_days}-day self-care limit.")
            if severity.lower() == "severe":  # Rule 4
                level = _bump(level)
                reasons.append("Severity reported as severe, so escalated one level.")
            return {"level": level, "matched": key, "reason": " ".join(reasons)}

    return {"level": "see a doctor", "matched": None,  # Rule 5: safe default
            "reason": "Symptom not in the rule table; defaulting to the safe option."}


def specialist_logic(condition: str, triage_level: str = "see a doctor") -> dict:
    level = triage_level.lower().strip()
    if level == "self-care":
        return {"specialist": "None needed now",
                "note": "See a General physician or pharmacist if symptoms persist or worsen."}

    dept = "General physician / Primary care"
    for key in sorted(SPECIALISTS, key=len, reverse=True):
        if key in condition.lower():
            dept = SPECIALISTS[key]
            break

    if level == "urgent":
        return {"specialist": f"Emergency department now ({dept} follow-up)",
                "note": "Go to the nearest emergency department or call your local emergency number."}
    return {"specialist": dept, "note": "Book an appointment soon."}


@tool
def search_reference(query: str) -> str:
    """
    Searches the medical reference documents (drug leaflets and symptom guidelines).

    Input Parameters:
    query (str) - A symptom, condition or medication name, e.g. "paracetamol dose",
        "sore throat", "ibuprofen side effects". Use a short topic, not a full sentence.

    Returns:
    Reference excerpts with source file and page number. Use ONLY this text for facts.

    Example: search_reference(query="paracetamol maximum daily dose")
    """
    from rag import get_retriever  # imported here so the MCP server stays lightweight

    docs = get_retriever().invoke(query)
    if not docs:
        return "No relevant reference found."
    return "\n\n".join(
        f"[{str(d.metadata.get('source', '?')).replace(chr(92), '/').split('/')[-1]} "
        f"p.{d.metadata.get('page', '?')}]\n{d.page_content}" for d in docs)


@tool
def triage_symptom(symptom: str, duration_days: int = 0, severity: str = "mild") -> dict:
    """
    Gets the triage level for a patient's SYMPTOM using fixed rules (not AI judgment).
    Use for any symptom the user describes. Do NOT use for pure medication questions.

    Input Parameters:
    symptom (str) - The symptom in plain words, e.g. "sore throat", "chest pain".
    duration_days (int) - How many days it has lasted. Use 0 if the user did not say.
    severity (str) - "mild", "moderate" or "severe". Use "mild" if not stated.

    Returns:
    A dict with level ("self-care", "see a doctor" or "urgent"), matched keyword and reason.
    Report the level exactly as returned. Never change it.

    Example: triage_symptom(symptom="headache", duration_days=5, severity="mild")
    """
    return triage_logic(symptom, duration_days, severity)


@tool
def specialist_finder(condition: str, triage_level: str) -> dict:
    """
    Finds which type of doctor or department the patient should see.
    Call ONLY after triage_symptom returned "see a doctor" or "urgent".

    Input Parameters:
    condition (str) - The same symptom text passed to triage_symptom.
    triage_level (str) - EXACTLY the level returned by triage_symptom.

    Returns:
    A dict with specialist (department name) and a short note.

    Example: specialist_finder(condition="chest pain", triage_level="urgent")
    """
    return specialist_logic(condition, triage_level)


if __name__ == "__main__":
    print(triage_symptom.invoke({"symptom": "sore throat", "duration_days": 6}))
    print(triage_symptom.invoke({"symptom": "persistent chest pain"}))
    print(specialist_finder.invoke({"condition": "chest pain", "triage_level": "urgent"}))
    # print(search_reference.invoke({"query": "paracetamol dose"}))  # needs ingest_data() first

    print(f"\nTool Name: {triage_symptom.name}")
    print(f"Tool Arguments: {triage_symptom.args}")
