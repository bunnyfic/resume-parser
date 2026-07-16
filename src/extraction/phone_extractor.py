import re
from typing import Optional

try:
    import phonenumbers
    _HAS_PHONENUMBERS = True
except ImportError:
    _HAS_PHONENUMBERS = False


LABEL_PATTERN = re.compile(
    r"(?:phone|mobile|contact|tel|cell|whatsapp)\s*[:\-]?\s*"
    r"([+\d][\d\s\-\.\(\)]{8,18}\d)",
    re.IGNORECASE
)

GENERIC_PATTERN = re.compile(
    r"""
    (?:(?:\+?\d{1,3})[\s\-\.]?)?      # country code
    (?:\(?\d{2,4}\)?[\s\-\.]?)?       # area code
    \d{3,4}[\s\-\.]?\d{3,4}            # main number
    """,
    re.VERBOSE
)


def _valid_length(digits: str) -> bool:
    return 10 <= len(digits) <= 13


def extract_phone(text: str, default_region: str = "IN") -> Optional[str]:
    """
    Extracts a phone number from cleaned resume text.

    Priority (most to least reliable):
    1. A number sitting right after an explicit label
       (Phone / Mobile / Contact / Tel / Cell / WhatsApp)
    2. Candidates validated by the `phonenumbers` library — filters out
       stray digit runs (dates, zip codes, IDs) that aren't real numbers
    3. A generic digit-pattern match, as a last resort

    Args:
        text: cleaned resume text
        default_region: ISO country code used by `phonenumbers` when a
            candidate number has no explicit country code. Adjust this if
            most of your resumes come from a different region.
    """
    if not text:
        return None

    # 1) Prefer numbers explicitly labeled as a phone number
    label_match = LABEL_PATTERN.search(text)
    if label_match:
        digits = re.sub(r"\D", "", label_match.group(1))
        if _valid_length(digits):
            return digits

    # 2) Validate candidates with phonenumbers if available
    if _HAS_PHONENUMBERS:
        try:
            for match in phonenumbers.PhoneNumberMatcher(text, default_region):
                if phonenumbers.is_valid_number(match.number):
                    return str(match.number.national_number)
        except Exception:
            pass  # fall through to the generic regex below

    # 3) Generic fallback regex
    for match in GENERIC_PATTERN.findall(text):
        digits = re.sub(r"\D", "", match)
        if _valid_length(digits):
            return digits

    return None
