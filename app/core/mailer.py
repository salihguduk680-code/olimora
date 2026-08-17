import asyncio
import logging
import re
import smtplib
from email.message import EmailMessage

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_EMAIL_PATTERN = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)


def _safe_brevo_error(response: httpx.Response) -> tuple[str, str]:
    """Return a bounded Brevo error code/message without personal data."""
    error_code = "unknown"
    error_message = "no details"
    try:
        payload = response.json()
        if isinstance(payload, dict):
            error_code = str(payload.get("code") or error_code)[:80]
            error_message = str(payload.get("message") or error_message)
    except (TypeError, ValueError):
        pass
    error_message = _EMAIL_PATTERN.sub("[email-redacted]", error_message)[:300]
    return error_code, error_message


def missing_mail_settings() -> tuple[str, ...]:
    """Return missing SMTP setting names without exposing their values."""
    settings = get_settings()
    brevo_api_key = (settings.brevo_api_key or "").strip()
    if brevo_api_key:
        missing: list[str] = []
    else:
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
    brevo_api_key = (settings.brevo_api_key or "").strip()
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

    if brevo_api_key:
        logger.info("Account email HTTPS delivery started")
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    "https://api.brevo.com/v3/smtp/email",
                    headers={
                        "accept": "application/json",
                        "api-key": brevo_api_key,
                        "content-type": "application/json",
                    },
                    json={
                        "sender": {"email": smtp_from_email, "name": "Olimora"},
                        "to": [{"email": to_email}],
                        "subject": subject,
                        "textContent": body,
                    },
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            error_code, error_message = _safe_brevo_error(exc.response)
            logger.error(
                "Account email HTTPS delivery rejected (status=%s, code=%s, message=%s)",
                exc.response.status_code,
                error_code,
                error_message,
            )
            return False
        except Exception as exc:
            # Some HTTP client errors include request headers in their message.
            # Never log the exception text or traceback because those headers may
            # contain the Brevo API key.
            logger.error(
                "Account email HTTPS delivery failed (%s)",
                type(exc).__name__,
            )
            return False
        logger.info("Account email HTTPS delivery completed")
        return True

    def _send() -> None:
        with smtplib.SMTP(smtp_host, settings.smtp_port, timeout=15) as client:
            if settings.smtp_starttls:
                client.starttls()
            if settings.smtp_username and settings.smtp_password:
                client.login(settings.smtp_username, settings.smtp_password)
            client.send_message(message)

    logger.info("Account email SMTP delivery started")
    try:
        await asyncio.to_thread(_send)
    except Exception:
        logger.exception("Account email SMTP delivery failed")
        return False
    logger.info("Account email SMTP delivery completed")
    return True
