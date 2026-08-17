import asyncio
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings


def mail_configured() -> bool:
    settings = get_settings()
    return bool(settings.smtp_host and settings.smtp_from_email)


async def send_account_email(to_email: str, subject: str, body: str) -> bool:
    settings = get_settings()
    smtp_host = settings.smtp_host
    smtp_from_email = settings.smtp_from_email
    if not smtp_host or not smtp_from_email:
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

    await asyncio.to_thread(_send)
    return True
