from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_dependencies import get_current_user
from app.api.v1.schemas.auth import AuthResponse, CredentialsRequest, UserResponse
from app.core.database import get_database_session
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.astrology.infrastructure.models import UserModel

router = APIRouter(prefix="/auth")


def _response(user: UserModel) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(user.id),
        user=UserResponse(id=user.id, email=user.email, created_at=user.created_at),
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    request: CredentialsRequest,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> AuthResponse:
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
    return _response(user)


@router.post("/login", response_model=AuthResponse)
async def login(
    request: CredentialsRequest,
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> AuthResponse:
    email = str(request.email).strip().lower()
    user = (
        await session.execute(select(UserModel).where(UserModel.email == email))
    ).scalar_one_or_none()
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="E-posta veya şifre hatalı."
        )
    return _response(user)


@router.get("/me", response_model=UserResponse)
async def me(user: Annotated[UserModel, Depends(get_current_user)]) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, created_at=user.created_at)


@router.delete("/me", status_code=204)
async def delete_me(
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> None:
    await session.delete(user)
    await session.commit()
