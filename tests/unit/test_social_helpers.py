import uuid

import pytest
from pydantic import ValidationError

from app.api.v1.endpoints.social import _ordered_pair
from app.api.v1.schemas.social import FriendRequestCreate, MessageCreate


def test_orders_friend_pair_consistently() -> None:
    first = uuid.UUID(int=20)
    second = uuid.UUID(int=10)

    assert _ordered_pair(first, second) == (second, first)
    assert _ordered_pair(second, first) == (second, first)


def test_normalizes_shared_olimora_id() -> None:
    request = FriendRequestCreate(olimora_id=" @OLI_0123456789ABCDEF ")

    assert request.olimora_id == "oli_0123456789abcdef"


def test_rejects_invalid_olimora_id() -> None:
    with pytest.raises(ValidationError):
        FriendRequestCreate(olimora_id="salih")


def test_rejects_whitespace_only_message() -> None:
    with pytest.raises(ValidationError):
        MessageCreate(body="   \n\t")


def test_trims_message_body() -> None:
    assert MessageCreate(body="  merhaba  ").body == "merhaba"
