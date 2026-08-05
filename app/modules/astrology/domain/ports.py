import uuid
from datetime import datetime
from typing import Protocol

from app.modules.astrology.domain.entities import (
    BirthProfile,
    NewNatalChart,
    StoredNatalChart,
)
from app.modules.astrology.domain.natal_chart import CalculationConfig, NatalChartPreview


class EphemerisCalculator(Protocol):
    def get_calculation_config(self, *, house_system: str) -> CalculationConfig: ...

    def calculate_natal_chart(
        self,
        *,
        utc_datetime: datetime,
        latitude: float,
        longitude: float,
        house_system: str,
    ) -> NatalChartPreview: ...


class AstrologyRepository(Protocol):
    async def add_birth_profile(self, profile: BirthProfile) -> BirthProfile: ...

    async def get_birth_profile(self, profile_id: uuid.UUID) -> BirthProfile | None: ...

    async def get_chart(
        self, profile_id: uuid.UUID, input_hash: str
    ) -> StoredNatalChart | None: ...

    async def insert_chart_if_absent(self, chart: NewNatalChart) -> uuid.UUID | None: ...
