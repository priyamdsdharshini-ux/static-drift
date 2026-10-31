"""Run: python build_all_pdfs.py   (needs: pip install reportlab)
Creates data/medicine_reference_guide.pdf, data/disease_reference_guide.pdf and a sample patient report."""
import subprocess, sys
for script in ["make_medicine_guide.py", "make_disease_guide.py", "make_sample_report.py"]:
    subprocess.run([sys.executable, script], check=True)
    print("built via", script)
