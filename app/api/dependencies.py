from functools import lru_cache

from app.core.config import get_settings
from app.modules.astrology.domain.ports import EphemerisCalculator
from app.modules.astrology.infrastructure.swisseph_calculator import calculator
from app.modules.interpretation.service import AthenaInterpretationService


def get_ephemeris_calculator() -> EphemerisCalculator:
    return calculator


@lru_cache
def get_athena_interpretation_service() -> AthenaInterpretationService:
    return AthenaInterpretationService(get_settings())
