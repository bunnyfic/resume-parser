import re
from typing import Optional


COMMON_DOMAINS = [
    "gmail", "yahoo", "outlook", "hotmail", "icloud",
    "protonmail", "rediffmail", "live", "aol", "zoho"
]

LABEL_PATTERN = re.compile(r"e[-\s]?mail\s*[:\-]?\s*", re.IGNORECASE)

EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)


def extract_email(text: str) -> Optional[str]:
    """
    Extracts the most likely email address from resume text.

    Handles:
    - Normal emails
    - OCR noise like spaces around @ and .
    - OCR missing dot in common domains (gmailcom -> gmail.com)
    - Prefers a match that follows an explicit "Email:" label, if present
    """

    if not text:
        return None

    # Step 1: Fix spacing around @ and .
    cleaned = re.sub(r"\s*@\s*", "@", text)
    cleaned = re.sub(r"\s*\.\s*", ".", cleaned)

    # Step 2: Fix missing dot in common domains (gmailcom -> gmail.com)
    for domain in COMMON_DOMAINS:
        cleaned = re.sub(
            rf"{domain}com\b",
            f"{domain}.com",
            cleaned,
            flags=re.IGNORECASE
        )

    # Step 3: Prefer a match right after an "Email:" label
    label_match = LABEL_PATTERN.search(cleaned)
    if label_match:
        window = cleaned[label_match.end():label_match.end() + 60]
        label_matches = EMAIL_PATTERN.findall(window)
        if label_matches:
            return label_matches[0].lower()

    # Step 4: Otherwise take the first email-looking match anywhere
    matches = EMAIL_PATTERN.findall(cleaned)
    if not matches:
        return None

    return matches[0].lower()
