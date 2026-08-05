from datetime import UTC, datetime

import pytest

from app.modules.astrology.application.timezone_resolver import resolve_local_datetime
from app.modules.astrology.domain.exceptions import (
    AmbiguousTimeError,
    InvalidLocalDateTimeError,
    NonExistentTimeError,
)


def test_istanbul_uses_permanent_utc_plus_three() -> None:
    result = resolve_local_datetime(
        local_datetime=datetime(2023, 6, 15, 12, 0),
        timezone_name="Europe/Istanbul",
    )

    assert result.utc_datetime == datetime(2023, 6, 15, 9, 0, tzinfo=UTC)
    assert result.utc_offset_minutes == 180


def test_berlin_ambiguous_time_requires_a_choice() -> None:
    with pytest.raises(AmbiguousTimeError) as error:
        resolve_local_datetime(
            local_datetime=datetime(2023, 10, 29, 2, 30),
            timezone_name="Europe/Berlin",
        )

    assert set(error.value.valid_offsets) == {60, 120}


@pytest.mark.parametrize(
    ("fold", "expected_utc"),
    [
        (0, datetime(2023, 10, 29, 0, 30, tzinfo=UTC)),
        (1, datetime(2023, 10, 29, 1, 30, tzinfo=UTC)),
    ],
)
def test_fold_selects_the_correct_ambiguous_instant(fold: int, expected_utc: datetime) -> None:
    result = resolve_local_datetime(
        local_datetime=datetime(2023, 10, 29, 2, 30),
        timezone_name="Europe/Berlin",
        fold=fold,
    )

    assert result.utc_datetime == expected_utc
    assert result.fold == fold


def test_utc_offset_selects_the_correct_ambiguous_instant() -> None:
    result = resolve_local_datetime(
        local_datetime=datetime(2023, 10, 29, 2, 30),
        timezone_name="Europe/Berlin",
        utc_offset_minutes=60,
    )

    assert result.utc_datetime == datetime(2023, 10, 29, 1, 30, tzinfo=UTC)


def test_nonexistent_time_is_rejected() -> None:
    with pytest.raises(NonExistentTimeError):
        resolve_local_datetime(
            local_datetime=datetime(2023, 3, 26, 2, 30),
            timezone_name="Europe/Berlin",
        )


def test_aware_local_datetime_is_rejected() -> None:
    with pytest.raises(InvalidLocalDateTimeError):
        resolve_local_datetime(
            local_datetime=datetime(2023, 1, 1, tzinfo=UTC),
            timezone_name="Europe/Istanbul",
        )


def test_unknown_timezone_is_rejected() -> None:
    with pytest.raises(InvalidLocalDateTimeError):
        resolve_local_datetime(
            local_datetime=datetime(2023, 1, 1),
            timezone_name="Not/A_Timezone",
        )
