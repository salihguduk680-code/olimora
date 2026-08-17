from types import SimpleNamespace

import pytest

from app.core import mailer


def test_missing_mail_settings_lists_names_without_values(monkeypatch) -> None:
    settings = SimpleNamespace(
        smtp_host="smtp.example.com",
        smtp_from_email="noreply@example.com",
        smtp_username=None,
        smtp_password=None,
        brevo_api_key=None,
    )
    monkeypatch.setattr(mailer, "get_settings", lambda: settings)

    assert mailer.missing_mail_settings() == ("SMTP_USERNAME", "SMTP_PASSWORD")
    assert mailer.mail_configured() is False


def test_mail_configured_when_required_settings_exist(monkeypatch) -> None:
    settings = SimpleNamespace(
        smtp_host="smtp.example.com",
        smtp_from_email="noreply@example.com",
        smtp_username="account",
        smtp_password="secret",
        brevo_api_key=None,
    )
    monkeypatch.setattr(mailer, "get_settings", lambda: settings)

    assert mailer.missing_mail_settings() == ()
    assert mailer.mail_configured() is True


def test_smtp_username_can_be_used_as_sender_fallback(monkeypatch) -> None:
    settings = SimpleNamespace(
        smtp_host="smtp.example.com",
        smtp_from_email=None,
        smtp_username="verified-sender@example.com",
        smtp_password="secret",
        brevo_api_key=None,
    )
    monkeypatch.setattr(mailer, "get_settings", lambda: settings)

    assert mailer.missing_mail_settings() == ()
    assert mailer.mail_configured() is True


def test_brevo_api_key_does_not_require_smtp_connection_settings(monkeypatch) -> None:
    settings = SimpleNamespace(
        smtp_host=None,
        smtp_from_email="verified-sender@example.com",
        smtp_username=None,
        smtp_password=None,
        brevo_api_key="api-secret",
    )
    monkeypatch.setattr(mailer, "get_settings", lambda: settings)

    assert mailer.missing_mail_settings() == ()
    assert mailer.mail_configured() is True


@pytest.mark.asyncio
async def test_brevo_key_is_trimmed_and_never_logged_on_failure(monkeypatch, caplog) -> None:
    secret = "api-secret-value"
    settings = SimpleNamespace(
        smtp_host=None,
        smtp_port=587,
        smtp_starttls=True,
        smtp_from_email="verified-sender@example.com",
        smtp_username=None,
        smtp_password=None,
        brevo_api_key=f"  {secret}\n",
    )
    captured_headers: dict[str, str] = {}

    class FailingClient:
        def __init__(self, **_kwargs) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args) -> None:
            return None

        async def post(self, _url, *, headers, json):
            captured_headers.update(headers)
            raise RuntimeError(f"request failed with secret {secret}")

    monkeypatch.setattr(mailer, "get_settings", lambda: settings)
    monkeypatch.setattr(mailer.httpx, "AsyncClient", FailingClient)

    assert await mailer.send_account_email("person@example.com", "Subject", "Body") is False
    assert captured_headers["api-key"] == secret
    assert secret not in caplog.text
    assert "RuntimeError" in caplog.text
