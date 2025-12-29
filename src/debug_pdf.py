"""Quick script to inspect PDF text for debugging parser"""
import sys
from pathlib import Path
import PyPDF2

if len(sys.argv) < 2:
    print("Usage: python debug_pdf.py <pdf_path>")
    sys.exit(1)

pdf_path = Path(sys.argv[1])
text = ""

with open(pdf_path, 'rb') as f:
    pdf_reader = PyPDF2.PdfReader(f)
    for i, page in enumerate(pdf_reader.pages):
        print(f"\n=== PAGE {i+1} ===\n")
        page_text = page.extract_text()
        print(page_text)
        text += page_text + "\n"

print("\n=== FULL TEXT (for regex testing) ===\n")
print(repr(text[:1000]))  # First 1000 chars as repr to see special chars
