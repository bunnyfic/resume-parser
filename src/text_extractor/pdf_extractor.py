import logging
import pdfplumber
import pytesseract

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF.
    Handles:
    1. Normal typed PDFs
    2. Scanned pages / pages where the resume content is an embedded image
       (falls back to OCR on a per-page basis)
    """

    all_text = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text()
                except Exception as e:
                    logger.warning(
                        f"[PDF EXTRACTOR] Layout extraction failed on page {i} "
                        f"of {file_path}: {e}"
                    )
                    text = None

                if text and text.strip():
                    all_text.append(text)
                    continue

                # No selectable text on this page -> OCR fallback.
                # Isolated per-page so one bad/scanned page can't wipe out
                # text already recovered from other pages.
                try:
                    page_image = page.to_image(resolution=300).original
                    ocr_text = pytesseract.image_to_string(
                        page_image,
                        config="--oem 3 --psm 4"
                    )
                    all_text.append(ocr_text)

                except pytesseract.TesseractNotFoundError:
                    logger.error(
                        "Tesseract OCR binary not found — image-based content on "
                        f"page {i} of {file_path} could not be read. If this is "
                        "deployed on Streamlit Cloud, add a `packages.txt` file "
                        "at the repo root containing `tesseract-ocr` and redeploy."
                    )
                    # Don't keep retrying OCR for remaining pages if the binary
                    # simply isn't installed at all.
                    break

                except Exception as e:
                    logger.warning(
                        f"[PDF EXTRACTOR] OCR failed on page {i} of {file_path}: {e}"
                    )

    except Exception as e:
        logger.error(f"[PDF EXTRACTOR ERROR] {file_path}: {e}")

    return "\n".join(all_text).strip()
