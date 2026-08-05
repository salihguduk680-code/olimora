import uuid
from datetime import UTC, datetime

from app.modules.astrology.application.constants import NATAL_CHART_SCHEMA_VERSION
from app.modules.astrology.application.input_hasher import create_natal_chart_input_hash
from app.modules.astrology.application.serialization import serialize_calculation
from app.modules.astrology.domain.entities import NatalChartOutcome, NewNatalChart
from app.modules.astrology.domain.ports import AstrologyRepository, EphemerisCalculator


class BirthProfileNotFoundError(Exception):
    pass


class CalculateNatalChart:
    def __init__(
        self,
        repository: AstrologyRepository,
        ephemeris: EphemerisCalculator,
    ) -> None:
        self._repository = repository
        self._ephemeris = ephemeris

    async def execute(self, *, profile_id: uuid.UUID, house_system: str) -> NatalChartOutcome:
        profile = await self._repository.get_birth_profile(profile_id)
        if profile is None:
            raise BirthProfileNotFoundError

        config = self._ephemeris.get_calculation_config(house_system=house_system)
        input_hash = create_natal_chart_input_hash(
            resolved_utc_datetime=profile.resolved_utc_datetime,
            latitude=profile.latitude,
            longitude=profile.longitude,
            house_system=house_system,
            requested_bodies=config.requested_bodies,
            calculator_name=config.calculator_name,
            engine_version=config.engine_version,
            wrapper_version=config.wrapper_version,
            calculation_flags=config.calculation_flags,
            zodiac_type=config.zodiac_type,
            house_placement_method=config.house_placement_method,
            schema_version=NATAL_CHART_SCHEMA_VERSION,
        )
        existing = await self._repository.get_chart(profile_id, input_hash)
        if existing is not None:
            return NatalChartOutcome(
                chart_id=existing.id,
                profile_id=profile_id,
                input_hash=input_hash,
                status="cached",
                result=existing.result_json,
            )

        calculation = self._ephemeris.calculate_natal_chart(
            utc_datetime=profile.resolved_utc_datetime,
            latitude=profile.latitude,
            longitude=profile.longitude,
            house_system=house_system,
        )
        result = serialize_calculation(calculation)
        new_chart = NewNatalChart(
            id=uuid.uuid4(),
            birth_profile_id=profile_id,
            calculator=config.calculator_name,
            calculator_version=config.engine_version,
            wrapper_version=config.wrapper_version,
            house_system=house_system,
            house_placement_method=config.house_placement_method,
            zodiac_type=config.zodiac_type,
            calculation_flags=config.calculation_flags,
            input_hash=input_hash,
            result_json=result,
            calculated_at=datetime.now(UTC),
        )
        inserted_id = await self._repository.insert_chart_if_absent(new_chart)
        if inserted_id is not None:
            return NatalChartOutcome(
                chart_id=inserted_id,
                profile_id=profile_id,
                input_hash=input_hash,
                status="calculated",
                result=result,
            )

        existing = await self._repository.get_chart(profile_id, input_hash)
        if existing is None:
            raise RuntimeError("Concurrent chart insert completed without a readable row.")
        return NatalChartOutcome(
            chart_id=existing.id,
            profile_id=profile_id,
            input_hash=input_hash,
            status="cached",
            result=existing.result_json,
        )
