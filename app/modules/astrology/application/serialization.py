from datetime import datetime

from app.modules.astrology.application.constants import NATAL_CHART_SCHEMA_VERSION
from app.modules.astrology.domain.natal_chart import (
    Aspect,
    ChartPoint,
    HouseCusp,
    NatalChartPreview,
)


def serialize_position(point: ChartPoint) -> dict[str, object]:
    return {
        "name": point.name,
        "longitude": point.longitude,
        "latitude": point.latitude,
        "distance": point.distance,
        "sign": point.sign,
        "degree_in_sign": point.degree_in_sign,
        "speed_longitude": point.speed_longitude,
        "is_retrograde": point.is_retrograde,
        "house": point.house,
    }


def serialize_house(house: HouseCusp) -> dict[str, object]:
    return {
        "house_number": house.house_number,
        "longitude": house.longitude,
        "sign": house.sign,
        "degree_in_sign": house.degree_in_sign,
    }


def serialize_aspect(aspect: Aspect) -> dict[str, object]:
    return {
        "body_a": aspect.body_a,
        "body_b": aspect.body_b,
        "aspect_type": aspect.aspect_type,
        "exact_angle": aspect.exact_angle,
        "actual_angle": aspect.actual_angle,
        "orb": aspect.orb,
    }


def serialize_calculation(chart: NatalChartPreview) -> dict[str, object]:
    return {
        "schema_version": NATAL_CHART_SCHEMA_VERSION,
        "utc_datetime": _iso_utc(chart.utc_datetime),
        "julian_day_ut": chart.julian_day_ut,
        "latitude": chart.latitude,
        "longitude": chart.longitude,
        "house_system": chart.house_system,
        "engine": {
            "name": chart.engine.name,
            "engine_version": chart.engine.engine_version,
            "wrapper_name": chart.engine.wrapper_name,
            "wrapper_version": chart.engine.wrapper_version,
            "house_system": chart.engine.house_system,
            "house_placement_method": chart.engine.house_placement_method,
            "zodiac_type": chart.engine.zodiac_type,
            "calculation_flags": chart.engine.calculation_flags,
        },
        "sun": serialize_position(chart.sun),
        "moon": serialize_position(chart.moon),
        "ascendant": serialize_position(chart.ascendant),
        "positions": [serialize_position(point) for point in chart.positions],
        "houses": [serialize_house(house) for house in chart.houses],
        "aspects": [serialize_aspect(aspect) for aspect in chart.aspects],
    }


def _iso_utc(value: datetime) -> str:
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")
