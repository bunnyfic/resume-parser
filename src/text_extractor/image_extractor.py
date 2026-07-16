import logging
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)


def is_ocr_available() -> bool:
    """
    Checks whether the Tesseract OCR binary is actually installed and
    reachable (not just the pytesseract Python wrapper).

    On Streamlit Cloud this returns False unless a `packages.txt` file
    containing `tesseract-ocr` exists at the repo root.
    """
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def extract_text_from_image(file_path: str) -> str:
    """
    Extracts text from an image resume using Tesseract OCR.

    Args:
        file_path (str): Path to the image file (jpg, png)

    Returns:
        str: Extracted text (empty string if OCR is unavailable or fails)
    """
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip()

    except pytesseract.TesseractNotFoundError:
        logger.error(
            "Tesseract OCR binary not found. If this is deployed on "
            "Streamlit Cloud, add a `packages.txt` file at the repo root "
            "containing the line `tesseract-ocr` and redeploy."
        )
        return ""

    except Exception as e:
        logger.error(f"[IMAGE ERROR] Failed to extract text from {file_path}: {e}")
        return ""
