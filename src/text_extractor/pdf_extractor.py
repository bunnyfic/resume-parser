import pdfplumber
import pytesseract
from PIL import Image


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF.
    Handles:
    1. Normal typed PDFs
    2. Scanned/image-based PDFs (OCR)
    """

    all_text = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                # Try normal text extraction first
                text = page.extract_text()

                if text and text.strip():
                    all_text.append(text)
                else:
                    # OCR fallback: convert page to image
                    page_image = page.to_image(resolution=300).original

                    ocr_text = pytesseract.image_to_string(
                        page_image,
                        config="--oem 3 --psm 4"
                    )

                    all_text.append(ocr_text)

    except Exception as e:
        print(f"[PDF EXTRACTOR ERROR] {file_path}: {e}")

    return "\n".join(all_text).strip()
