import re
from typing import Optional


def clean_text(text: Optional[str]) -> str:
    """
    Cleans raw extracted resume text so downstream
    extractors (email, phone, name) work reliably.

    Steps:
    - Handle None safely
    - Normalize whitespace
    - Remove OCR junk characters
    - Preserve emails, numbers, and names
    """

    if not text:
        return ""

    # Ensure text is string
    text = str(text)

    # Replace multiple spaces / newlines / tabs with single space
    text = re.sub(r"\s+", " ", text)

    # Remove non-ASCII characters (common OCR noise)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    # Remove long sequences of symbols (----, ****, ___)
    text = re.sub(r"[_\-*]{2,}", " ", text)

    # Strip leading and trailing spaces
    text = text.strip()

    return text
