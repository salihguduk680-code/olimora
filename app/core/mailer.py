import asyncio
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def missing_mail_settings() -> tuple[str, ...]:
    """Return missing SMTP setting names without exposing their values."""
    settings = get_settings()
    required = {
        "SMTP_HOST": settings.smtp_host,
        "SMTP_USERNAME": settings.smtp_username,
        "SMTP_PASSWORD": settings.smtp_password,
    }
    missing = [name for name, value in required.items() if not value]
    if not settings.smtp_from_email and not settings.smtp_username:
        missing.append("SMTP_FROM_EMAIL")
    return tuple(missing)


def mail_configured() -> bool:
    return not missing_mail_settings()


async def send_account_email(to_email: str, subject: str, body: str) -> bool:
    settings = get_settings()
    smtp_host = settings.smtp_host
    smtp_from_email = settings.smtp_from_email or settings.smtp_username
    missing = missing_mail_settings()
    if missing:
        logger.warning("Account email skipped; missing SMTP settings: %s", ", ".join(missing))
        return False

    message = EmailMessage()
    message["From"] = smtp_from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    def _send() -> None:
        with smtplib.SMTP(smtp_host, settings.smtp_port, timeout=15) as client:
            if settings.smtp_starttls:
                client.starttls()
            if settings.smtp_username and settings.smtp_password:
                client.login(settings.smtp_username, settings.smtp_password)
            client.send_message(message)

    logger.info("Account email delivery started")
    try:
        await asyncio.to_thread(_send)
    except Exception:
        logger.exception("Account email delivery failed")
        return False
    logger.info("Account email delivery completed")
    return True
