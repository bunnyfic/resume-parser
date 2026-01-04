import os
from src.text_extractor.pdf_extractor import extract_text_from_pdf

# Get absolute path to project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build absolute path to the PDF
file_path = os.path.join(BASE_DIR, "data", "raw", "sample1.pdf")

print("Using file path:", file_path)

text = extract_text_from_pdf(file_path)

print("\n---- EXTRACTED TEXT PREVIEW ----")
print(text[:2000])