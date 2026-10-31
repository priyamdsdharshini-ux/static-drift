from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak

NAVY = colors.HexColor("#1F3A5F"); LIGHT = colors.HexColor("#EAF0F7"); RED = colors.HexColor("#9B1C1C")
ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["Normal"], fontSize=9.5, leading=13)
cell = ParagraphStyle("c", parent=body, fontSize=8.5, leading=11)
cellh = ParagraphStyle("ch", parent=cell, textColor=colors.white, fontName="Helvetica-Bold")
h1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=20, textColor=NAVY, spaceAfter=2)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12, textColor=NAVY, spaceBefore=10, spaceAfter=4)
ent = ParagraphStyle("e", parent=ss["Heading3"], fontSize=11.5, textColor=colors.white, leading=14)
small = ParagraphStyle("s", parent=body, fontSize=8, textColor=colors.grey, leading=10)

# problem, medicine, dose, limit, caution, self-care, see doctor
DATA = [
 ("Headache", "Paracetamol (acetaminophen) or ibuprofen",
  "Paracetamol 500-1000 mg every 4-6 hours, maximum 4 g in 24 hours (some labels cap at 3 g; follow your product label). Ibuprofen 200-400 mg every 6-8 hours with food, maximum 1200 mg/day without a doctor.",
  "3 days",
  "Do not take ibuprofen with stomach ulcers, kidney disease, NSAID-triggered asthma, blood thinners or in late pregnancy. Check cold and flu products for hidden paracetamol.",
  "Rest in a quiet room, drink water, eat regularly, limit screens and caffeine.",
  "Headache lasting more than 3 days, the worst headache of your life, stiff neck, fever with rash, confusion, weakness, or headache after a head injury (go to emergency care)."),
 ("Fever (adults)", "Paracetamol",
  "500-1000 mg every 4-6 hours, maximum 4 g in 24 hours (some labels cap at 3 g). Ibuprofen 200-400 mg every 6-8 hours with food is an alternative if suitable.",
  "3 days",
  "Avoid paracetamol in serious liver disease or regular heavy alcohol use. Do not combine with other paracetamol products.",
  "Drink plenty of fluids, rest, wear light clothing. Medicine lowers discomfort; it does not treat the cause.",
  "Temperature 39 C or higher, fever lasting more than 3 days, fever with stiff neck, rash, trouble breathing, confusion, or severe pain."),
 ("Sore throat", "Throat lozenges plus paracetamol or ibuprofen for pain",
  "Lozenges as per label, usually one every 2-3 hours. Paracetamol or ibuprofen at the doses listed under Headache.",
  "5 days",
  "Antibiotics do not help most sore throats (usually viral). They are only used when a doctor confirms a bacterial infection.",
  "Gargle warm salt water, drink warm fluids, honey in warm water, rest your voice.",
  "Sore throat longer than 5 days, trouble swallowing or breathing, drooling, swelling of the neck, high fever, or white patches on the tonsils."),
 ("Cough", "Honey in warm water; dextromethorphan for dry cough (per label)",
  "Honey 1-2 teaspoons in warm water, adults only. Dextromethorphan: follow the product label, usually 10-20 mg every 4 hours, not more than 120 mg in 24 hours.",
  "14 days",
  "Do not use dextromethorphan with MAOI antidepressants or without asking a pharmacist if you take SSRIs. Cough suppressants are not for coughs with lots of phlegm.",
  "Warm fluids, steam inhalation, avoid smoke, keep the head raised at night.",
  "Cough longer than 14 days, coughing blood, shortness of breath, wheezing, chest pain, night sweats, or weight loss."),
 ("Common cold and runny nose", "Rest and fluids; saline nasal spray; paracetamol for aches",
  "Saline spray as needed. Paracetamol at the doses listed under Headache.",
  "7 days",
  "Antibiotics do not work on colds. Decongestants such as pseudoephedrine can raise blood pressure; avoid with hypertension or heart disease unless a doctor agrees. Do not use nasal decongestant sprays for more than 3 days.",
  "Warm drinks, steam, rest, wash hands often.",
  "Symptoms beyond 7 days or getting worse, facial pain with thick discharge, ear pain, high fever, or trouble breathing."),
 ("Heartburn and acid reflux", "Antacid (calcium carbonate or aluminium-magnesium) for quick relief; omeprazole 20 mg for frequent heartburn",
  "Antacid as per label after meals and at bedtime. Omeprazole 20 mg once daily, 30 minutes before breakfast, for up to 14 days.",
  "14 days",
  "Antacids can interact with other medicines; take them 2 hours apart from other tablets. Long-term acid suppression needs a doctor's review.",
  "Smaller meals, avoid spicy and fatty food, no food 3 hours before sleep, raise the head of the bed, reduce alcohol and caffeine.",
  "Trouble or pain swallowing, black or bloody stools, vomiting blood, unexplained weight loss, chest pain, or symptoms beyond 14 days."),
 ("Diarrhea (adults)", "Oral rehydration solution (ORS); loperamide if no fever or blood",
  "ORS after each loose stool. Loperamide: 4 mg first, then 2 mg after each loose stool, maximum 8 mg/day without a doctor. Stop after 48 hours.",
  "3 days",
  "Do not use loperamide if there is fever, blood or mucus in the stool, or for children. Dehydration is the main danger.",
  "Sip fluids often, eat bland foods (rice, banana, toast), avoid alcohol and milk-heavy foods briefly.",
  "Diarrhea longer than 3 days, blood in stool, high fever, severe stomach pain, signs of dehydration (very dry mouth, little urine, dizziness)."),
 ("Constipation", "Fiber (psyllium husk) and fluids; lactulose or macrogol if needed",
  "Psyllium husk with a full glass of water as per label. Lactulose or macrogol as per label.",
  "7 days",
  "Avoid regular use of stimulant laxatives (such as senna or bisacodyl). Take fiber with plenty of water.",
  "More fruit, vegetables and whole grains, 6-8 glasses of water daily, daily walking, do not ignore the urge to go.",
  "Blood in stool, severe stomach pain or swelling, vomiting, unexplained weight loss, or constipation longer than 7 days."),
 ("Nausea", "Small sips of fluid and ginger; dimenhydrinate for motion sickness (per label)",
  "Dimenhydrinate: follow the product label. It causes drowsiness.",
  "2 days",
  "Do not drive after sedating antihistamines. Avoid alcohol with them.",
  "Small frequent sips of clear fluids, bland dry foods, rest, fresh air.",
  "Nausea beyond 2 days, unable to keep fluids down, severe stomach pain, blood in vomit, or pregnancy with severe vomiting."),
 ("Minor cut or scrape", "Clean water and a clean dressing; antiseptic cream is optional",
  "No oral medicine needed. Paracetamol at standard doses if painful.",
  "3 days",
  "Check your tetanus vaccination status.",
  "Wash hands, rinse the wound under clean running water, press with a clean cloth to stop bleeding, cover with a clean dressing and change daily.",
  "Bleeding that does not stop after 10 minutes of firm pressure, deep or gaping cuts, dirt that cannot be removed, animal or human bites, or redness, swelling, pus or fever."),
 ("Insect bite", "Hydrocortisone 1% cream; cetirizine for itching",
  "Hydrocortisone 1%: thin layer 1-2 times daily for up to 7 days. Cetirizine 10 mg once daily.",
  "3 days",
  "Do not apply hydrocortisone to broken skin or the face without advice. Cetirizine can cause drowsiness.",
  "Wash with soap and water, apply a cold compress, do not scratch.",
  "Swelling of the face, lips or tongue, trouble breathing, dizziness (emergency); spreading redness, pus, or fever."),
 ("Rash or allergic itching", "Cetirizine 10 mg or loratadine 10 mg; hydrocortisone 1% for small areas",
  "Cetirizine or loratadine: 10 mg once daily. Hydrocortisone 1%: thin layer 1-2 times daily for up to 7 days.",
  "5 days",
  "Reduce the dose or ask a doctor if you have kidney disease (cetirizine). Do not scratch or use cream on infected skin.",
  "Moisturize, wear loose cotton, avoid known triggers and harsh soaps.",
  "Rash with fever, blistering, rapidly spreading rash, mouth sores, swelling of the face or tongue, trouble breathing, or rash beyond 5 days."),
 ("Back pain or muscle strain", "Paracetamol or ibuprofen; heat; staying active",
  "Paracetamol or ibuprofen at the doses listed under Headache. Ibuprofen is taken with food.",
  "7 days",
  "Rest for no more than a day or two; gentle movement heals faster. Same ibuprofen cautions as under Headache.",
  "Warm pack for 15-20 minutes, gentle stretching, light walking, good posture.",
  "Numbness or weakness in the legs, loss of bladder or bowel control, pain after a fall or injury, fever, or pain beyond 7 days."),
]

def footer(c, d):
    c.saveState(); c.setFont("Helvetica", 7.5); c.setFillColor(colors.grey)
    c.drawString(18*mm, 10*mm, "General reference information only. Not a prescription or medical advice. Check your product label and ask a pharmacist or doctor.")
    c.drawRightString(A4[0]-18*mm, 10*mm, f"Page {d.page}"); c.restoreState()

def P(t, st=body): return Paragraph(t, st)

s = [P("Common Medicines for Everyday Problems", h1),
     P("Adult Reference Guide (self-care and triage companion)", ParagraphStyle("sub", parent=body, alignment=1, textColor=NAVY)),
     Spacer(1, 8),
     P("<b>Important:</b> This guide lists commonly used non-prescription options for adults, compiled from standard public guidance "
       "(for example NHS, MedlinePlus and WHO essential medicines information). It is general information, not a diagnosis or prescription. "
       "Doses are typical adult label doses. <b>Always follow your product label</b> and ask a pharmacist or doctor if you are pregnant, "
       "breastfeeding, have kidney, liver, stomach or heart disease, or take other medicines. Children need weight-based doses; ask a pharmacist or doctor.", body),
     P("Quick reference", h2)]

rows = [[P("Problem", cellh), P("First-line option", cellh), P("Self-care limit", cellh)]]
for d in DATA: rows.append([P(f"<b>{d[0]}</b>", cell), P(d[1], cell), P(d[3], cell)])
t = Table(rows, colWidths=[42*mm, 100*mm, 32*mm], repeatRows=1)
t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), NAVY), ("GRID", (0,0), (-1,-1), 0.4, colors.lightgrey),
                       ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT]), ("VALIGN", (0,0), (-1,-1), "TOP"),
                       ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3)]))
s += [t, Spacer(1, 8),
      P("<b>Self-care limit</b> means: if symptoms last longer than this, see a doctor.", cell),
      Spacer(1, 6)]

emerg = Table([[P("<b>Call emergency services now for:</b> chest pain or pressure, difficulty breathing, fainting, seizure, "
                  "signs of stroke (face drooping, slurred speech, sudden weakness), severe bleeding, vomiting blood, swelling of the face or tongue, "
                  "suspected overdose or poisoning, or thoughts of self-harm. Do not treat these at home.", body)]], colWidths=[174*mm])
emerg.setStyle(TableStyle([("BOX", (0,0), (-1,-1), 1, RED), ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#FDEDED")),
                           ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6), ("LEFTPADDING", (0,0), (-1,-1), 8)]))
s += [emerg, PageBreak(), P("Detailed entries", h2)]

for name, med, dose, limit, caution, selfcare, doctor in DATA:
    head = Table([[P(name, ent)]], colWidths=[174*mm])
    head.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), NAVY), ("LEFTPADDING", (0,0), (-1,-1), 8)]))
    det = Table([[P("<b>Medicine</b>", cell), P(f"{name}: {med}", cell)],
                 [P("<b>Adult dose</b>", cell), P(dose, cell)],
                 [P("<b>Cautions</b>", cell), P(caution, cell)],
                 [P("<b>Self-care</b>", cell), P(selfcare, cell)],
                 [P("<b>See a doctor if</b>", cell), P(f"{doctor} Also see a doctor if it lasts longer than {limit}.", cell)]],
                colWidths=[30*mm, 144*mm])
    det.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), LIGHT), ("LINEBELOW", (0,0), (-1,-1), 0.4, colors.white),
                             ("VALIGN", (0,0), (-1,-1), "TOP"), ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3)]))
    s += [KeepTogether([head, det, Spacer(1, 7)])]

s += [P("General medicine safety", h2),
      P("1. Read the label and use the lowest dose that works for the shortest time.<br/>"
        "2. Never take two products with the same active ingredient (for example several products containing paracetamol).<br/>"
        "3. Antibiotics are prescription medicines and do not treat colds, most sore throats or most coughs.<br/>"
        "4. Tell your pharmacist about all medicines and supplements you take, and about pregnancy, allergies and long-term conditions.<br/>"
        "5. Stop and get medical help if you develop a rash, swelling, trouble breathing, or symptoms that get worse.<br/>"
        "6. Keep medicines out of reach of children and do not use them after the expiry date.", body),
      Spacer(1, 8),
      P("Review by a qualified pharmacist or doctor is recommended before using this document in any real health service.", small)]

SimpleDocTemplate("../data/medicine_reference_guide.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=15*mm, bottomMargin=18*mm,
                  title="Common Medicines for Everyday Problems", author="Reference guide").build(s, onFirstPage=footer, onLaterPages=footer)
