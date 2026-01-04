import re
from typing import Optional


COMMON_DOMAINS = [
    "gmail", "yahoo", "outlook", "hotmail", "icloud"
]


def extract_email(text: str) -> Optional[str]:
    """
    Extracts the most likely email address from resume text.

    Handles:
    - Normal emails
    - OCR noise like spaces around @ and .
    - OCR missing dot in common domains (gmailcom → gmail.com)
    """

    if not text:
        return None

    # Step 1: Fix spacing around @ and .
    cleaned = re.sub(r"\s*@\s*", "@", text)
    cleaned = re.sub(r"\s*\.\s*", ".", cleaned)

    # Step 2: Fix missing dot in common domains (gmailcom → gmail.com)
    for domain in COMMON_DOMAINS:
        cleaned = re.sub(
            rf"{domain}com\b",
            f"{domain}.com",
            cleaned,
            flags=re.IGNORECASE
        )

    # Step 3: Email regex
    email_pattern = re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    )

    matches = email_pattern.findall(cleaned)

    if not matches:
        return None

    return matches[0].lower()
