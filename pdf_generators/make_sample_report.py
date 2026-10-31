from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

NAVY = colors.HexColor("#1F3A5F")
LIGHT = colors.HexColor("#EAF0F7")
ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["Normal"], fontSize=9.5, leading=13)
h = ParagraphStyle("h", parent=ss["Heading2"], fontSize=11.5, textColor=NAVY, spaceBefore=10, spaceAfter=4)
title = ParagraphStyle("t", parent=ss["Title"], fontSize=18, textColor=NAVY, spaceAfter=2)
small = ParagraphStyle("s", parent=body, fontSize=8, textColor=colors.grey, leading=10)

def kv_table(rows, widths):
    t = Table([[Paragraph(f"<b>{a}</b>", body), Paragraph(b, body), Paragraph(f"<b>{c}</b>", body), Paragraph(d, body)] for a, b, c, d in rows],
              colWidths=widths)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("GRID", (0, 0), (-1, -1), 0.4, colors.white),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t

def grid_table(data, widths):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 9),
                           ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t

def footer(c, d):
    c.saveState()
    c.setFont("Helvetica", 7.5); c.setFillColor(colors.grey)
    c.drawString(18*mm, 10*mm, "SAMPLE DOCUMENT - fictional patient and data, for demonstration only. Not for clinical use.")
    c.drawRightString(A4[0]-18*mm, 10*mm, f"Page {d.page}")
    c.restoreState()

doc = SimpleDocTemplate("../sample_medical_report.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                        topMargin=15*mm, bottomMargin=18*mm, title="Sample Medical Report", author="Sample General Hospital")
s = []
s += [Paragraph("SAMPLE GENERAL HOSPITAL", title),
      Paragraph("Outpatient Medical Report &nbsp;|&nbsp; Department of Internal Medicine", ParagraphStyle("c", parent=body, alignment=1, textColor=NAVY)),
      Spacer(1, 8)]

s.append(kv_table([
    ("Patient", "Rahul Verma (fictional)", "Report No.", "MR-2026-004217"),
    ("Age / Sex", "42 years / Male", "Date of visit", "28 October 2026"),
    ("Patient ID", "P-100482", "Consultant", "Dr. A. Sharma, MD (Internal Medicine)"),
    ("Blood group", "B positive", "Visit type", "Outpatient follow-up"),
], [28*mm, 52*mm, 28*mm, 66*mm]))

s += [Paragraph("1. Presenting Complaint", h),
      Paragraph("Burning sensation in the upper abdomen after meals for the past 3 weeks, worse at night and when lying flat. "
                "Occasional sour taste in the mouth. No vomiting, no black stools, no weight loss, no chest pain or breathlessness.", body)]

s += [Paragraph("2. Medical and Personal History", h),
      Paragraph("<b>Past history:</b> Mild hypertension (diagnosed 2024). No diabetes. No previous surgeries.<br/>"
                "<b>Medications:</b> Amlodipine 5 mg once daily.<br/>"
                "<b>Allergies:</b> No known drug allergies.<br/>"
                "<b>Lifestyle:</b> Non-smoker. Occasional alcohol. Irregular meal timings, frequent spicy and late-night meals.<br/>"
                "<b>Family history:</b> Father has hypertension.", body)]

s += [Paragraph("3. Vital Signs", h),
      grid_table([["Parameter", "Result", "Reference range"],
                  ["Blood pressure", "132 / 84 mmHg", "Below 120 / 80 (ideal)"],
                  ["Pulse", "76 beats/min", "60 - 100"],
                  ["Temperature", "36.8 C", "36.1 - 37.2"],
                  ["Respiratory rate", "16 / min", "12 - 20"],
                  ["SpO2", "98 %", "95 - 100"],
                  ["Weight / Height", "74 kg / 172 cm", "-"],
                  ["BMI", "25.0 kg/m2", "18.5 - 24.9"]],
                 [55*mm, 50*mm, 69*mm])]

s += [Paragraph("4. Examination Findings", h),
      Paragraph("General: alert, comfortable, no pallor or jaundice. Cardiovascular and respiratory systems: normal. "
                "Abdomen: soft, mild tenderness in the epigastric region, no guarding, no organomegaly.", body)]

s += [Paragraph("5. Laboratory Results", h),
      grid_table([["Test", "Result", "Reference range", "Flag"],
                  ["Hemoglobin", "14.2 g/dL", "13.0 - 17.0", "Normal"],
                  ["WBC count", "7,400 /uL", "4,000 - 11,000", "Normal"],
                  ["Platelets", "2.6 lakh /uL", "1.5 - 4.5 lakh", "Normal"],
                  ["Fasting glucose", "92 mg/dL", "70 - 99", "Normal"],
                  ["Total cholesterol", "212 mg/dL", "Below 200", "High"],
                  ["LDL cholesterol", "138 mg/dL", "Below 100", "High"],
                  ["Creatinine", "0.9 mg/dL", "0.7 - 1.3", "Normal"],
                  ["ALT (SGPT)", "28 U/L", "7 - 56", "Normal"],
                  ["H. pylori stool antigen", "Negative", "Negative", "Normal"]],
                 [55*mm, 35*mm, 45*mm, 39*mm])]

s += [Paragraph("6. Assessment", h),
      Paragraph("Symptoms and examination are consistent with <b>gastro-esophageal reflux disease (GERD)</b>, mild. "
                "Borderline raised cholesterol and stage 1 blood pressure noted. No alarm features present.", body)]

s += [Paragraph("7. Plan and Advice", h),
      Paragraph("<b>Medication:</b> Pantoprazole 40 mg once daily, 30 minutes before breakfast, for 4 weeks. Continue amlodipine 5 mg.<br/>"
                "<b>Diet and lifestyle:</b> Smaller, regular meals; avoid spicy and fried food; no food 3 hours before sleep; "
                "raise the head of the bed; reduce alcohol; walk 30 minutes daily; reduce salt.<br/>"
                "<b>Follow-up:</b> Review in 4 weeks with repeat lipid profile and blood pressure check.<br/>"
                "<b>Seek urgent care if:</b> black or bloody stools, repeated vomiting, difficulty swallowing, chest pain, "
                "breathlessness or unexplained weight loss.", body)]

s += [Spacer(1, 14),
      Paragraph("_______________________________<br/><b>Dr. A. Sharma, MD</b><br/>Consultant, Internal Medicine<br/>Reg. No. SAMPLE-00000", body),
      Spacer(1, 8),
      Paragraph("This is a fictional sample created for demonstration. All names, numbers and findings are invented and do not describe a real person.", small)]

doc.build(s, onFirstPage=footer, onLaterPages=footer)
