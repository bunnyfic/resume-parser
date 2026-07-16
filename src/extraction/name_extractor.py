from typing import Optional
import logging
import re

import pdfplumber
import pytesseract

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# spaCy PERSON-entity NER is the primary name-detection signal. It's loaded
# once (module-level singleton) and lazily, and everything degrades
# gracefully to the font-size + blacklist heuristic if the model isn't
# installed — this module never hard-crashes the app if spaCy is missing.
# ---------------------------------------------------------------------------
_NLP = None
_NLP_LOAD_ATTEMPTED = False


def _get_nlp():
    global _NLP, _NLP_LOAD_ATTEMPTED
    if not _NLP_LOAD_ATTEMPTED:
        _NLP_LOAD_ATTEMPTED = True
        try:
            import spacy
            _NLP = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.warning(
                f"spaCy model 'en_core_web_sm' unavailable ({e}); "
                "falling back to heuristic-only name extraction."
            )
            _NLP = None
    return _NLP


BLACKLIST = {
    "summary", "insight", "insights", "skills", "experience", "education",
    "engineering", "software", "data", "developer", "engineer", "manager",
    "platform", "springboard", "infosys", "curriculum", "vitae", "resume",
    "san", "jose", "california", "india", "street", "avenue", "road",
    "profile", "objective", "contact", "director", "linkedin", "github",
    "portfolio", "references", "certifications", "projects", "achievements"
}


def looks_like_name(text: str) -> bool:
    if not text:
        return False

    words = text.strip().split()

    if not (2 <= len(words) <= 3):
        return False

    for i, w in enumerate(words):
        if not w.isalpha():
            return False

        if w.lower() in BLACKLIST:
            return False

        if i == 0:
            if not w[0].isupper():
                return False
        else:
            if len(w) == 1:
                if not w.isupper():
                    return False
            else:
                if not w[0].isupper():
                    return False

    return True


def _name_from_spacy(text: str) -> Optional[str]:
    """Run NER on the top of the resume and return the most likely PERSON name."""
    nlp = _get_nlp()
    if nlp is None or not text:
        return None

    # The name is always near the top — no need to run NER on the whole doc.
    snippet = text[:800]
    doc = nlp(snippet)

    for ent in doc.ents:
        if ent.label_ != "PERSON":
            continue

        candidate = re.sub(r"\s+", " ", ent.text).strip()
        words = candidate.split()

        if not (2 <= len(words) <= 3):
            continue
        if any(w.lower() in BLACKLIST for w in words):
            continue
        if not all(w.replace("-", "").isalpha() for w in words):
            continue

        return candidate.title()

    return None


def extract_name_from_image_pdf(pdf_path: str) -> Optional[str]:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            image = page.to_image(resolution=300).original
            text = pytesseract.image_to_string(image)

            # 1) spaCy NER on the raw OCR text — most accurate
            name = _name_from_spacy(text)
            if name:
                return name

            # 2) Heuristic fallback: scan top lines
            lines = [l.strip() for l in text.splitlines() if l.strip()][:15]

            for line in lines:
                clean = re.sub(r"[^A-Za-z\s]", "", line)
                clean = re.sub(r"\s+", " ", clean).strip()
                if looks_like_name(clean):
                    return clean.title()

            for i in range(len(lines) - 1):
                combined = f"{lines[i]} {lines[i + 1]}"
                clean = re.sub(r"[^A-Za-z\s]", "", combined)
                clean = re.sub(r"\s+", " ", clean).strip()
                if looks_like_name(clean):
                    return clean.title()

        return None

    except pytesseract.TesseractNotFoundError:
        logger.error(
            "Tesseract OCR binary not found — cannot OCR this PDF for name "
            "detection. If deployed on Streamlit Cloud, add `tesseract-ocr` "
            "to a `packages.txt` file at the repo root."
        )
        return None
    except Exception as e:
        logger.warning(
            f"[NAME EXTRACTOR] OCR-based name extraction failed for {pdf_path}: {e}"
        )
        return None


def extract_name_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Hybrid extractor, in priority order:
    1. spaCy PERSON NER on the page's layout text — most accurate, catches
       names regardless of font size/position on the page
    2. Largest-font-size heuristic — fallback for names spaCy misses
    3. OCR — for scanned pages / embedded resume images
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            layout_text = page.extract_text() or ""

            # 1) spaCy NER first
            name = _name_from_spacy(layout_text)
            if name:
                return name

            # 2) Font-size heuristic fallback
            words = page.extract_words(extra_attrs=["size"])
            if words:
                font_groups = {}
                for w in words:
                    size = round(w["size"], 1)
                    font_groups.setdefault(size, []).append(w["text"])

                for size in sorted(font_groups.keys(), reverse=True):
                    line = " ".join(font_groups[size])
                    line = re.sub(r"[^A-Za-z\s]", "", line)
                    line = re.sub(r"\s+", " ", line).strip()
                    if looks_like_name(line):
                        return line
    except Exception as e:
        logger.warning(
            f"[NAME EXTRACTOR] Layout-based extraction failed for {pdf_path}: {e}"
        )

    # 3) OCR fallback (scanned PDFs / embedded images)
    return extract_name_from_image_pdf(pdf_path)
