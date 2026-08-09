import uuid

from app.api.v1.endpoints.social import _ordered_pair


def test_orders_friend_pair_consistently() -> None:
    first = uuid.UUID(int=20)
    second = uuid.UUID(int=10)

    assert _ordered_pair(first, second) == (second, first)
    assert _ordered_pair(second, first) == (second, first)
