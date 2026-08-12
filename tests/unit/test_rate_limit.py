from app.core.rate_limit import AttemptLimiter


def test_attempt_limiter_blocks_after_limit_and_can_clear() -> None:
    limiter = AttemptLimiter(max_keys=2)

    assert limiter.consume("login:user", limit=2, window_seconds=60)
    assert limiter.consume("login:user", limit=2, window_seconds=60)
    assert not limiter.consume("login:user", limit=2, window_seconds=60)

    limiter.clear("login:user")
    assert limiter.consume("login:user", limit=2, window_seconds=60)
