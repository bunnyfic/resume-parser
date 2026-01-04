import re
from typing import Optional


def extract_phone(text: str) -> Optional[str]:
    """
    Extracts a phone number from cleaned resume text.

    Supports:
    - International numbers (+91, +1, etc.)
    - Spaces, dashes, brackets
    - Returns digits-only string
    """

    if not text:
        return None

    # Common phone number pattern
    phone_pattern = re.compile(
        r"""
        (?:(?:\+?\d{1,3})[\s\-\.]?)?      # country code
        (?:\(?\d{2,4}\)?[\s\-\.]?)?       # area code
        \d{3,4}[\s\-\.]?\d{3,4}            # main number
        """,
        re.VERBOSE
    )

    matches = phone_pattern.findall(text)

    for match in matches:
        # Remove all non-digits
        digits = re.sub(r"\D", "", match)

        # Accept reasonable phone lengths
        if 10 <= len(digits) <= 13:
            return digits

    return None
