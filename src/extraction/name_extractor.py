from typing import Optional
import pdfplumber
import pytesseract
import re


BLACKLIST = {
    "summary", "insight", "skills", "experience", "education",
    "engineering", "software", "data", "developer",
    "platform", "springboard", "infosys",
    "san", "jose", "california", "india",
    "profile", "objective", "contact", "director"
}


def looks_like_name(text: str) -> bool:
    if not text:
        return False

    words = text.strip().split()

    if not (2 <= len(words) <= 3):
        return False

    if text.isupper():
        # OCR often outputs uppercase — allow but be strict
        pass

    for i, w in enumerate(words):
        if not w.isalpha():
            return False

        if w.lower() in BLACKLIST:
            return False

        if i == 0:
            if not w[0].isupper():
                return False
        else:
            # allow full word or initial
            if len(w) == 1:
                if not w.isupper():
                    return False
            else:
                if not w[0].isupper():
                    return False

    return True


def extract_name_from_image_pdf(pdf_path: str) -> Optional[str]:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            image = page.to_image(resolution=300).original

            text = pytesseract.image_to_string(image)
            lines = [l.strip() for l in text.splitlines() if l.strip()]

            # Only top part of resume
            lines = lines[:15]

            # 1️⃣ Try single lines
            for line in lines:
                clean = re.sub(r"[^A-Za-z\s]", "", line)
                clean = re.sub(r"\s+", " ", clean).strip()
                if looks_like_name(clean):
                    return clean.title()

            # 2️⃣ Try combining adjacent lines (RENATA + VOSS)
            for i in range(len(lines) - 1):
                combined = f"{lines[i]} {lines[i + 1]}"
                clean = re.sub(r"[^A-Za-z\s]", "", combined)
                clean = re.sub(r"\s+", " ", clean).strip()
                if looks_like_name(clean):
                    return clean.title()

        return None

    except Exception:
        return None


def extract_name_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Final hybrid extractor:
    - Layout text (if available)
    - OCR with line merging
    """

    # Try layout-based first
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
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
    except Exception:
        pass

    # Fallback to OCR
    return extract_name_from_image_pdf(pdf_path)
