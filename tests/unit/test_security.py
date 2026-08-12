import base64
import json
import uuid

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_round_trip_and_wrong_password() -> None:
    encoded = hash_password("correct horse battery staple")

    assert "correct horse battery staple" not in encoded
    assert verify_password("correct horse battery staple", encoded)
    assert not verify_password("wrong password", encoded)


def test_access_token_round_trip_and_tamper_rejection() -> None:
    user_id = uuid.uuid4()
    token = create_access_token(user_id)

    assert decode_access_token(token) == user_id
    assert decode_access_token(token + "tampered") is None


def test_access_token_rejects_unexpected_algorithm_header() -> None:
    token = create_access_token(uuid.uuid4())
    _, payload, signature = token.split(".")
    header = base64.urlsafe_b64encode(
        json.dumps({"alg": "none", "typ": "JWT"}).encode()
    ).rstrip(b"=").decode()

    assert decode_access_token(f"{header}.{payload}.{signature}") is None
