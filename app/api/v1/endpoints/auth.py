import hashlib
import logging
import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_dependencies import get_current_user
from app.api.v1.schemas.auth import (
    ActionResponse,
    AuthResponse,
    CredentialsRequest,
    EmailRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    RegistrationRequest,
    TokenRequest,
    UserResponse,
)
from app.core.config import get_settings
from app.core.database import get_database_session
from app.core.mailer import mail_configured, missing_mail_settings, send_account_email
from app.core.rate_limit import AttemptLimiter
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.astrology.infrastructure.models import AccountTokenModel, UserModel

router = APIRouter(prefix="/auth")
_auth_limiter = AttemptLimiter()
logger = logging.getLogger(__name__)


def _attempt_key(kind: str, email: str, request: Request) -> str:
    client = request.client.host if request.client else "unknown"
    return f"{kind}:{client}:{email}"


def _response(user: UserModel) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(user.id),
        user=UserResponse(
            id=user.id,
            email=user.email,
            created_at=user.created_at,
            email_verified=user.email_verified,
        ),
    )


def _token_hash(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


async def _issue_account_token(
    session: AsyncSession,
    user: UserModel,
    purpose: str,
    lifetime: timedelta,
) -> str:
    await session.execute(
        delete(AccountTokenModel).where(
            AccountTokenModel.user_id == user.id,
            AccountTokenModel.purpose == purpose,
            AccountTokenModel.used_at.is_(None),
        )
    )
    raw_token = secrets.token_urlsafe(32)
    session.add(
        AccountTokenModel(
            user_id=user.id,
            token_hash=_token_hash(raw_token),
            purpose=purpose,
            expires_at=datetime.now(UTC) + lifetime,
        )
    )
    await session.commit()
    return raw_token


def _schedule_email(
    background_tasks: BackgroundTasks,
    email: str,
    subject: str,
    path: str,
) -> bool:
    if not mail_configured():
        logger.warning(
            "Account email was not scheduled; missing SMTP settings: %s",
            ", ".join(missing_mail_settings()),
        )
        return False
    url = f"{get_settings().public_base_url.rstrip('/')}{path}"
    background_tasks.add_task(
        send_account_email,
        email,
        subject,
        (
            f"Olimora hesabın için bağlantı:\n\n{url}\n\n"
            "Bu isteği sen yapmadıysan e-postayı yok sayabilirsin."
        ),
    )
    logger.info("Account email scheduled")
    return True


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    request: RegistrationRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> AuthResponse:
    key = _attempt_key("register", request.email, http_request)
    if not _auth_limiter.consume(key, limit=5, window_seconds=60 * 60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Çok fazla kayıt denemesi yapıldı. Daha sonra tekrar dene.",
        )
    user = UserModel(
        email=str(request.email).strip().lower(), password_hash=hash_password(request.password)
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Bu e-posta zaten kayıtlı."
        ) from error
    await session.refresh(user)
    verification_token = await _issue_account_token(
        session, user, "verify_email", timedelta(hours=24)
    )
    _schedule_email(
        background_tasks,
        user.email,
        "Olimora e-posta doğrulama",
        f"/verify-email?token={verification_token}",
    )
    return _response(user)


@router.post("/login", response_model=AuthResponse)
async def login(
    request: CredentialsRequest,
    http_request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> AuthResponse:
    email = str(request.email).strip().lower()
    key = _attempt_key("login", email, http_request)
    if not _auth_limiter.consume(key, limit=10, window_seconds=15 * 60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Çok fazla giriş denemesi yapıldı. 15 dakika sonra tekrar dene.",
        )
    user = (
        await session.execute(select(UserModel).where(UserModel.email == email))
    ).scalar_one_or_none()
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="E-posta veya şifre hatalı."
        )
    _auth_limiter.clear(key)
    return _response(user)


@router.get("/me", response_model=UserResponse)
async def me(user: Annotated[UserModel, Depends(get_current_user)]) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
        email_verified=user.email_verified,
    )


@router.post("/request-password-reset", response_model=ActionResponse, status_code=202)
async def request_password_reset(
    request: EmailRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> ActionResponse:
    key = _attempt_key("password-reset", request.email, http_request)
    if not _auth_limiter.consume(key, limit=5, window_seconds=60 * 60):
        return ActionResponse(status="accepted")
    normalized_email = request.email.strip().lower()
    user = (
        await session.execute(select(UserModel).where(UserModel.email == normalized_email))
    ).scalar_one_or_none()
    logger.info("Password reset account lookup completed; account_found=%s", user is not None)
    if user is not None:
        raw_token = await _issue_account_token(
            session, user, "reset_password", timedelta(minutes=30)
        )
        scheduled = _schedule_email(
            background_tasks,
            user.email,
            "Olimora şifre yenileme",
            f"/reset-password?token={raw_token}",
        )
        logger.info("Password reset email scheduling completed; scheduled=%s", scheduled)
    return ActionResponse(status="accepted")


@router.post("/reset-password", response_model=ActionResponse)
async def reset_password(
    request: PasswordResetRequest,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> ActionResponse:
    account_token = (
        await session.execute(
            select(AccountTokenModel).where(
                AccountTokenModel.token_hash == _token_hash(request.token),
                AccountTokenModel.purpose == "reset_password",
                AccountTokenModel.used_at.is_(None),
                AccountTokenModel.expires_at > datetime.now(UTC),
            )
        )
    ).scalar_one_or_none()
    if account_token is None:
        raise HTTPException(status_code=422, detail="Bağlantı geçersiz veya süresi dolmuş.")
    user = await session.get(UserModel, account_token.user_id)
    if user is None:
        raise HTTPException(status_code=422, detail="Bağlantı geçersiz veya süresi dolmuş.")
    user.password_hash = hash_password(request.new_password)
    account_token.used_at = datetime.now(UTC)
    await session.commit()
    return ActionResponse(status="password_updated")


@router.post("/request-email-verification", response_model=ActionResponse, status_code=202)
async def request_email_verification(
    background_tasks: BackgroundTasks,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> ActionResponse:
    if user.email_verified:
        return ActionResponse(status="already_verified")
    if not mail_configured():
        raise HTTPException(status_code=503, detail="E-posta hizmeti henüz etkin değil.")
    raw_token = await _issue_account_token(session, user, "verify_email", timedelta(hours=24))
    _schedule_email(
        background_tasks,
        user.email,
        "Olimora e-posta doğrulama",
        f"/verify-email?token={raw_token}",
    )
    return ActionResponse(status="sent")


@router.post("/verify-email", response_model=ActionResponse)
async def verify_email(
    request: TokenRequest,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> ActionResponse:
    account_token = (
        await session.execute(
            select(AccountTokenModel).where(
                AccountTokenModel.token_hash == _token_hash(request.token),
                AccountTokenModel.purpose == "verify_email",
                AccountTokenModel.used_at.is_(None),
                AccountTokenModel.expires_at > datetime.now(UTC),
            )
        )
    ).scalar_one_or_none()
    if account_token is None:
        raise HTTPException(status_code=422, detail="Bağlantı geçersiz veya süresi dolmuş.")
    user = await session.get(UserModel, account_token.user_id)
    if user is None:
        raise HTTPException(status_code=422, detail="Bağlantı geçersiz veya süresi dolmuş.")
    user.email_verified = True
    account_token.used_at = datetime.now(UTC)
    await session.commit()
    return ActionResponse(status="verified")


@router.post("/change-password", status_code=204)
async def change_password(
    request: PasswordChangeRequest,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> None:
    if not verify_password(request.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mevcut şifren hatalı.",
        )
    if verify_password(request.new_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Yeni şifren mevcut şifrenden farklı olmalı.",
        )
    user.password_hash = hash_password(request.new_password)
    await session.commit()


@router.delete("/me", status_code=204)
async def delete_me(
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> None:
    await session.delete(user)
    await session.commit()


@router.post("/delete-account", status_code=204)
async def delete_account_with_credentials(
    request: CredentialsRequest,
    http_request: Request,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> None:
    email = str(request.email).strip().lower()
    key = _attempt_key("delete", email, http_request)
    if not _auth_limiter.consume(key, limit=5, window_seconds=60 * 60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Çok fazla silme denemesi yapıldı. Daha sonra tekrar dene.",
        )
    user = (
        await session.execute(select(UserModel).where(UserModel.email == email))
    ).scalar_one_or_none()
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta veya şifre hatalı.",
        )
    await session.delete(user)
    await session.commit()
    _auth_limiter.clear(key)
