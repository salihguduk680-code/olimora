import pytest
from fastapi import HTTPException

from app.core.content_moderation import ensure_allowed_user_content


def test_allows_normal_message_and_normalizes_whitespace() -> None:
    assert ensure_allowed_user_content("  Bugünkü yorumun   çok güzel  ") == (
        "Bugünkü yorumun çok güzel"
    )


@pytest.mark.parametrize(
    "message",
    ["Seni öldür", "kendini öldür", "çocuk için cinsel nude içerik"],
)
def test_rejects_high_risk_content(message: str) -> None:
    with pytest.raises(HTTPException) as error:
        ensure_allowed_user_content(message)
    assert error.value.status_code == 422


def test_rejects_link_spam() -> None:
    with pytest.raises(HTTPException):
        ensure_allowed_user_content("https://a.test https://b.test https://c.test")
