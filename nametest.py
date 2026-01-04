import os
from src.extraction.name_extractor import extract_name_from_pdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(BASE_DIR, "data", "raw", "sample1.pdf")

name = extract_name_from_pdf(pdf_path)

print("Extracted Name:", name)
