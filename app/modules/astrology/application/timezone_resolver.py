from dataclasses import dataclass
from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.modules.astrology.domain.exceptions import (
    AmbiguousTimeError,
    InvalidLocalDateTimeError,
    NonExistentTimeError,
)


@dataclass(frozen=True, slots=True)
class ResolvedLocalDateTime:
    utc_datetime: datetime
    fold: int
    utc_offset_minutes: int


def _offset_minutes(candidate: datetime) -> int:
    offset = candidate.utcoffset()
    if offset is None:
        raise InvalidLocalDateTimeError("UTC offset could not be determined.")
    return int(offset.total_seconds() // 60)


def _is_valid_round_trip(local_datetime: datetime, candidate: datetime, zone: ZoneInfo) -> bool:
    returned = candidate.astimezone(UTC).astimezone(zone)
    return returned.replace(tzinfo=None) == local_datetime and returned.fold == candidate.fold


def resolve_local_datetime(
    *,
    local_datetime: datetime,
    timezone_name: str,
    fold: int | None = None,
    utc_offset_minutes: int | None = None,
) -> ResolvedLocalDateTime:
    if local_datetime.tzinfo is not None:
        raise InvalidLocalDateTimeError("local_datetime must not contain a UTC offset.")
    if fold not in (None, 0, 1):
        raise InvalidLocalDateTimeError("fold must be 0, 1, or null.")

    try:
        zone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError) as error:
        raise InvalidLocalDateTimeError("Unknown IANA timezone.") from error

    candidates = [local_datetime.replace(tzinfo=zone, fold=value) for value in (0, 1)]
    valid = [
        candidate
        for candidate in candidates
        if _is_valid_round_trip(local_datetime, candidate, zone)
    ]

    if not valid:
        raise NonExistentTimeError("Local time did not occur in this timezone.")

    unique = {candidate.astimezone(UTC): candidate for candidate in valid}
    valid = list(unique.values())

    if len(valid) == 1:
        selected = valid[0]
        if fold is not None and fold != selected.fold:
            raise InvalidLocalDateTimeError("fold does not match this local time.")
        if utc_offset_minutes is not None and utc_offset_minutes != _offset_minutes(selected):
            raise InvalidLocalDateTimeError("UTC offset does not match this local time.")
    else:
        offsets = tuple(_offset_minutes(candidate) for candidate in valid)
        selected_candidates = valid
        if fold is not None:
            selected_candidates = [
                candidate for candidate in selected_candidates if candidate.fold == fold
            ]
        if utc_offset_minutes is not None:
            selected_candidates = [
                candidate
                for candidate in selected_candidates
                if _offset_minutes(candidate) == utc_offset_minutes
            ]
        if not selected_candidates:
            raise InvalidLocalDateTimeError("fold and UTC offset do not select a valid instant.")
        if fold is None and utc_offset_minutes is None:
            raise AmbiguousTimeError((offsets[0], offsets[1]))
        selected = selected_candidates[0]

    return ResolvedLocalDateTime(
        utc_datetime=selected.astimezone(UTC),
        fold=selected.fold,
        utc_offset_minutes=_offset_minutes(selected),
    )
