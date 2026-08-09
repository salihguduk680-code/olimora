from datetime import UTC, datetime, timedelta

from app.api.v1.endpoints.birth_profiles import _remaining_profile_cooldown_hours


def test_allows_first_profile_edit() -> None:
    now = datetime.now(UTC)

    assert _remaining_profile_cooldown_hours(None, now=now) is None


def test_reports_rounded_remaining_cooldown() -> None:
    now = datetime.now(UTC)

    assert _remaining_profile_cooldown_hours(now - timedelta(hours=2), now=now) == 22
    assert _remaining_profile_cooldown_hours(now - timedelta(hours=25), now=now) is None
