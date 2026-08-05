import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.astrology.domain.entities import (
    BirthProfile,
    NewNatalChart,
    StoredNatalChart,
)
from app.modules.astrology.infrastructure.models import BirthProfileModel, NatalChartModel


class AstrologyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_birth_profile(self, profile: BirthProfile) -> BirthProfile:
        model = BirthProfileModel(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            local_birth_datetime_naive=profile.local_birth_datetime_naive,
            timezone_name=profile.timezone_name,
            resolved_utc_datetime=profile.resolved_utc_datetime,
            fold=profile.fold,
            utc_offset_minutes=profile.utc_offset_minutes,
            latitude=profile.latitude,
            longitude=profile.longitude,
            place_name=profile.place_name,
            tzdata_version=profile.tzdata_version,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
        self._session.add(model)
        await self._session.commit()
        return profile

    async def get_birth_profile(self, profile_id: uuid.UUID) -> BirthProfile | None:
        model = await self._session.get(BirthProfileModel, profile_id)
        return None if model is None else _birth_profile_entity(model)

    async def get_chart(self, profile_id: uuid.UUID, input_hash: str) -> StoredNatalChart | None:
        statement = select(NatalChartModel).where(
            NatalChartModel.birth_profile_id == profile_id,
            NatalChartModel.input_hash == input_hash,
        )
        model = (await self._session.execute(statement)).scalar_one_or_none()
        if model is None:
            return None
        return StoredNatalChart(
            id=model.id,
            birth_profile_id=model.birth_profile_id,
            input_hash=model.input_hash,
            result_json=model.result_json,
        )

    async def insert_chart_if_absent(self, chart: NewNatalChart) -> uuid.UUID | None:
        statement = (
            insert(NatalChartModel)
            .values(
                id=chart.id,
                birth_profile_id=chart.birth_profile_id,
                calculator=chart.calculator,
                calculator_version=chart.calculator_version,
                wrapper_version=chart.wrapper_version,
                house_system=chart.house_system,
                house_placement_method=chart.house_placement_method,
                zodiac_type=chart.zodiac_type,
                calculation_flags=chart.calculation_flags,
                input_hash=chart.input_hash,
                result_json=chart.result_json,
                calculated_at=chart.calculated_at,
            )
            .on_conflict_do_nothing(
                constraint="uq_natal_chart_profile_input_hash",
            )
            .returning(NatalChartModel.id)
        )
        chart_id = (await self._session.execute(statement)).scalar_one_or_none()
        await self._session.commit()
        return chart_id


def _birth_profile_entity(model: BirthProfileModel) -> BirthProfile:
    return BirthProfile(
        id=model.id,
        user_id=model.user_id,
        name=model.name,
        local_birth_datetime_naive=model.local_birth_datetime_naive,
        timezone_name=model.timezone_name,
        resolved_utc_datetime=model.resolved_utc_datetime,
        fold=model.fold or 0,
        utc_offset_minutes=model.utc_offset_minutes,
        latitude=model.latitude,
        longitude=model.longitude,
        place_name=model.place_name,
        tzdata_version=model.tzdata_version,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
