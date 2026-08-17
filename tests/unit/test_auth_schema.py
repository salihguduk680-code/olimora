import pytest
from pydantic import ValidationError

from app.api.v1.schemas.auth import CredentialsRequest, PasswordChangeRequest, RegistrationRequest


def test_registration_requires_stronger_password() -> None:
    with pytest.raises(ValidationError):
        RegistrationRequest(email="user@example.com", password="password")


def test_registration_accepts_letter_and_number_password() -> None:
    request = RegistrationRequest(email=" USER@EXAMPLE.COM ", password="Password123")
    assert request.email == "user@example.com"


def test_existing_login_schema_keeps_eight_character_compatibility() -> None:
    request = CredentialsRequest(email="user@example.com", password="pass1234")
    assert request.password == "pass1234"


def test_password_change_requires_strong_new_password() -> None:
    with pytest.raises(ValidationError):
        PasswordChangeRequest(current_password="pass1234", new_password="onlyletters")


def test_password_change_accepts_letter_and_number() -> None:
    request = PasswordChangeRequest(
        current_password="pass1234",
        new_password="NewPassword123",
    )
    assert request.new_password == "NewPassword123"
