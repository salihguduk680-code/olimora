import pytest
from pydantic import ValidationError

from app.api.v1.schemas.auth import CredentialsRequest, RegistrationRequest


def test_registration_requires_stronger_password() -> None:
    with pytest.raises(ValidationError):
        RegistrationRequest(email="user@example.com", password="password")


def test_registration_accepts_letter_and_number_password() -> None:
    request = RegistrationRequest(email=" USER@EXAMPLE.COM ", password="Password123")
    assert request.email == "user@example.com"


def test_existing_login_schema_keeps_eight_character_compatibility() -> None:
    request = CredentialsRequest(email="user@example.com", password="pass1234")
    assert request.password == "pass1234"
