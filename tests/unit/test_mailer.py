from types import SimpleNamespace

from app.core import mailer


def test_missing_mail_settings_lists_names_without_values(monkeypatch) -> None:
    settings = SimpleNamespace(
        smtp_host="smtp.example.com",
        smtp_from_email="noreply@example.com",
        smtp_username=None,
        smtp_password=None,
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
    )
    monkeypatch.setattr(mailer, "get_settings", lambda: settings)

    assert mailer.missing_mail_settings() == ()
    assert mailer.mail_configured() is True
