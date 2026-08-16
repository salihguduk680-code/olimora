import re
import unicodedata

from fastapi import HTTPException, status

_BLOCKED_PATTERNS = (
    re.compile(r"\b(?:seni|onu|hepinizi)\s+(?:oldur|gebert|vuracagim|vurucam)\b"),
    re.compile(r"\b(?:kendini\s+oldur|intihar\s+et)\b"),
    re.compile(r"\b(?:cocuk|cocuga|resit\s*olmayan)\b.{0,24}\b(?:cinsel|porno|nude)\b"),
)
_URL_PATTERN = re.compile(r"https?://|www\.", re.IGNORECASE)


def ensure_allowed_user_content(value: str) -> str:
    """Reject a narrow set of high-risk content without sending text to a third party."""

    cleaned = " ".join(value.split())
    normalized = unicodedata.normalize("NFKD", cleaned).encode("ascii", "ignore").decode().lower()
    if any(pattern.search(normalized) for pattern in _BLOCKED_PATTERNS):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Bu içerik Olimora topluluk kurallarına uygun görünmüyor.",
        )
    if len(_URL_PATTERN.findall(cleaned)) > 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Bir mesajda en fazla iki bağlantı paylaşabilirsin.",
        )
    return cleaned
