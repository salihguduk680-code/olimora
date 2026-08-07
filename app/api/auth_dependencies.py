from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_database_session
from app.core.security import decode_access_token
from app.modules.astrology.infrastructure.models import UserModel


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> UserModel:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Oturum gerekli.")
    user_id = decode_access_token(authorization[7:])
    user = None if user_id is None else await session.get(UserModel, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Oturum geçersiz.")
    return user
