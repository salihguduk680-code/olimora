import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_dependencies import get_current_user
from app.api.v1.endpoints.social import _accepted_friendship, _social_user
from app.api.v1.schemas.compatibility import (
    CompatibilityAspectResponse,
    CompatibilityResponse,
)
from app.core.database import get_database_session
from app.modules.astrology.infrastructure.models import (
    BirthProfileModel,
    NatalChartModel,
    UserModel,
)

router = APIRouter(prefix="/social/compatibility")

_ASPECTS = (
    ("conjunction", 0.0, 8.0, 8),
    ("sextile", 60.0, 5.0, 5),
    ("square", 90.0, 6.0, -6),
    ("trine", 120.0, 6.0, 7),
    ("opposition", 180.0, 7.0, -5),
)
_CATEGORY_PAIRS = {
    "communication": {"sun", "moon", "mercury"},
    "emotional": {"moon", "venus"},
    "attraction": {"venus", "mars"},
    "stability": {"sun", "moon", "jupiter", "saturn"},
}


@router.get("/{friend_user_id}", response_model=CompatibilityResponse)
async def compare_friend_charts(
    friend_user_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> CompatibilityResponse:
    await _accepted_friendship(session, user.id, friend_user_id)
    own_chart = await _latest_chart(session, user.id)
    friend_chart = await _latest_chart(session, friend_user_id)
    if own_chart is None or friend_chart is None:
        raise HTTPException(
            status_code=409,
            detail="Karşılaştırma için iki kişinin de doğum haritası hazır olmalı.",
        )

    own_positions = _positions(own_chart.result_json)
    friend_positions = _positions(friend_chart.result_json)
    scores = {key: 50 for key in _CATEGORY_PAIRS}
    aspects: list[CompatibilityAspectResponse] = []
    for own in own_positions:
        for friend_position in friend_positions:
            aspect = _aspect_between(own["longitude"], friend_position["longitude"])
            if aspect is None:
                continue
            aspect_type, orb, weight = aspect
            for category, bodies in _CATEGORY_PAIRS.items():
                if own["name"] in bodies and friend_position["name"] in bodies:
                    scores[category] += weight
            if own["name"] in {"sun", "moon", "mercury", "venus", "mars", "saturn"} and (
                friend_position["name"] in {"sun", "moon", "mercury", "venus", "mars", "saturn"}
            ):
                aspects.append(
                    CompatibilityAspectResponse(
                        person_a_body=own["name"],
                        person_b_body=friend_position["name"],
                        aspect_type=aspect_type,
                        orb=round(orb, 2),
                        tone="supportive" if weight > 0 else "challenging",
                    )
                )

    friend = await _social_user(session, friend_user_id)
    return CompatibilityResponse(
        friend_name=friend.display_name,
        communication=_bounded(scores["communication"]),
        emotional=_bounded(scores["emotional"]),
        attraction=_bounded(scores["attraction"]),
        stability=_bounded(scores["stability"]),
        highlights=sorted(aspects, key=lambda item: item.orb)[:8],
        disclaimer=(
            "Sinastri sonuçları eğlence ve öz farkındalık amaçlıdır; ilişki kararı değildir."
        ),
    )


async def _latest_chart(session: AsyncSession, user_id: uuid.UUID) -> NatalChartModel | None:
    return (
        await session.execute(
            select(NatalChartModel)
            .join(BirthProfileModel, BirthProfileModel.id == NatalChartModel.birth_profile_id)
            .where(BirthProfileModel.user_id == user_id)
            .order_by(NatalChartModel.calculated_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()


def _positions(result: dict[str, object]) -> list[dict[str, Any]]:
    raw = result.get("positions")
    if not isinstance(raw, list):
        return []
    positions: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        longitude = item.get("longitude")
        if isinstance(name, str) and isinstance(longitude, int | float):
            positions.append({"name": name.lower(), "longitude": float(longitude)})
    return positions


def _aspect_between(first: float, second: float) -> tuple[str, float, int] | None:
    separation = abs(first - second) % 360.0
    separation = min(separation, 360.0 - separation)
    matches = [
        (name, abs(separation - exact), weight)
        for name, exact, allowed_orb, weight in _ASPECTS
        if abs(separation - exact) <= allowed_orb
    ]
    return min(matches, key=lambda item: item[1]) if matches else None


def _bounded(value: int) -> int:
    return max(15, min(95, value))
