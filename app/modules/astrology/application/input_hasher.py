import hashlib
import json
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation


def _canonical_decimal(value: float) -> str:
    try:
        decimal = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError("Coordinate must be a finite decimal value.") from error
    if not decimal.is_finite():
        raise ValueError("Coordinate must be a finite decimal value.")
    if decimal == 0:
        return "0"
    return format(decimal.normalize(), "f")


def create_natal_chart_input_hash(
    *,
    resolved_utc_datetime: datetime,
    latitude: float,
    longitude: float,
    house_system: str,
    requested_bodies: tuple[str, ...],
    calculator_name: str,
    engine_version: str,
    wrapper_version: str,
    calculation_flags: int,
    zodiac_type: str = "tropical",
    house_placement_method: str = "ecliptic_longitude_cusp_interval",
    schema_version: str = "1.0",
) -> str:
    if resolved_utc_datetime.tzinfo is None or resolved_utc_datetime.utcoffset() != UTC.utcoffset(
        resolved_utc_datetime
    ):
        raise ValueError("resolved_utc_datetime must be timezone-aware UTC.")

    payload = {
        "calculation_flags": calculation_flags,
        "calculator_name": calculator_name,
        "engine_version": engine_version,
        "house_placement_method": house_placement_method,
        "house_system": house_system,
        "latitude": _canonical_decimal(latitude),
        "longitude": _canonical_decimal(longitude),
        "requested_bodies": sorted(set(requested_bodies)),
        "resolved_utc_datetime": resolved_utc_datetime.astimezone(UTC)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z"),
        "schema_version": schema_version,
        "wrapper_version": wrapper_version,
        "zodiac_type": zodiac_type,
    }
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical_json.encode("ascii")).hexdigest()
