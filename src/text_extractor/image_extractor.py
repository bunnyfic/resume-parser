from PIL import Image
import pytesseract


def extract_text_from_image(file_path: str) -> str:
    """
    Extracts text from an image resume using Tesseract OCR.

    Args:
        file_path (str): Path to the image file (jpg, png)

    Returns:
        str: Extracted text
    """
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip()

    except Exception as e:
        print(f"[IMAGE ERROR] Failed to extract text from {file_path}: {e}")
        return ""
