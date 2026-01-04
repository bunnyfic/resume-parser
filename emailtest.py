from src.text_extractor.pdf_extractor import extract_text_from_pdf
from src.preprocessing.text_cleaner import clean_text
from src.extraction.email_extractor import extract_email
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "data", "raw", "sample_resume.pdf")

raw_text = extract_text_from_pdf(file_path)
cleaned_text = clean_text(raw_text)

email = extract_email(cleaned_text)

print("Extracted Email:", email)
