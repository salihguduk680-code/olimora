import time
from collections import OrderedDict, deque
from threading import Lock


class AttemptLimiter:
    """Small bounded limiter for one-process authentication abuse protection."""

    def __init__(self, *, max_keys: int = 10_000) -> None:
        self._attempts: OrderedDict[str, deque[float]] = OrderedDict()
        self._max_keys = max_keys
        self._lock = Lock()

    def consume(self, key: str, *, limit: int, window_seconds: int) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            attempts = self._attempts.setdefault(key, deque())
            while attempts and attempts[0] < cutoff:
                attempts.popleft()
            self._attempts.move_to_end(key)
            if len(attempts) >= limit:
                return False
            attempts.append(now)
            while len(self._attempts) > self._max_keys:
                self._attempts.popitem(last=False)
        return True

    def clear(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)
