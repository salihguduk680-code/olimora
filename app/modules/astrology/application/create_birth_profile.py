import importlib.metadata
import uuid
from datetime import UTC, datetime

from app.modules.astrology.application.timezone_resolver import resolve_local_datetime
from app.modules.astrology.domain.entities import BirthProfile
from app.modules.astrology.domain.ports import AstrologyRepository


class CreateBirthProfile:
    def __init__(self, repository: AstrologyRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        *,
        name: str,
        local_datetime: datetime,
        timezone_name: str,
        latitude: float,
        longitude: float,
        place_name: str,
        fold: int | None,
        utc_offset_minutes: int | None,
    ) -> BirthProfile:
        resolved = resolve_local_datetime(
            local_datetime=local_datetime,
            timezone_name=timezone_name,
            fold=fold,
            utc_offset_minutes=utc_offset_minutes,
        )
        now = datetime.now(UTC)
        profile = BirthProfile(
            id=uuid.uuid4(),
            user_id=None,
            name=name,
            local_birth_datetime_naive=local_datetime,
            timezone_name=timezone_name,
            resolved_utc_datetime=resolved.utc_datetime,
            fold=resolved.fold,
            utc_offset_minutes=resolved.utc_offset_minutes,
            latitude=latitude,
            longitude=longitude,
            place_name=place_name,
            tzdata_version=importlib.metadata.version("tzdata"),
            created_at=now,
            updated_at=now,
        )
        return await self._repository.add_birth_profile(profile)
