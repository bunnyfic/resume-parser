import os
import pandas as pd

from src.text_extractor.pdf_extractor import extract_text_from_pdf
from src.text_extractor.image_extractor import extract_text_from_image
from src.preprocessing.text_cleaner import clean_text

from src.extraction.email_extractor import extract_email
from src.extraction.phone_extractor import extract_phone
from src.extraction.name_extractor import extract_name_from_pdf


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}


def process_resume(file_path: str) -> dict:
    ext = os.path.splitext(file_path)[1].lower()

    raw_text = ""
    name = None

    # --- PDF ---
    if ext in SUPPORTED_PDF_EXTENSIONS:
        raw_text = extract_text_from_pdf(file_path)
        name = extract_name_from_pdf(file_path)

    # --- IMAGE ---
    elif ext in SUPPORTED_IMAGE_EXTENSIONS:
        raw_text = extract_text_from_image(file_path)
        name = None  # Image-name extraction not implemented yet (correct)

    cleaned_text = clean_text(raw_text)

    email = extract_email(cleaned_text)
    phone = extract_phone(cleaned_text)

    return {
        "name": name,
        "email": email,
        "phone": phone
    }


def run_pipeline(input_dir: str, output_csv: str):
    results = []

    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)

        if os.path.isfile(file_path):
            print(f"Processing: {file}")
            results.append(process_resume(file_path))

    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=True)

    print("\nPipeline completed.")
    print("\nFinal Extracted Data:\n")
    print(df.to_string(index=True))


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    INPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
    OUTPUT_FILE = os.path.join(BASE_DIR, "data", "output", "resume_data.csv")

    run_pipeline(INPUT_DIR, OUTPUT_FILE)

