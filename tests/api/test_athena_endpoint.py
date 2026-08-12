import uuid
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.auth_dependencies import get_current_user
from app.api.dependencies import get_athena_interpretation_service
from app.core.database import get_database_session
from app.main import app
from app.modules.interpretation.service import InterpretationResult

client = TestClient(app)


class FakeAthenaService:
    async def interpret(self, **_: object) -> InterpretationResult:
        return InterpretationResult(
            text=(
                "Haritandaki üç ana gösterge, sezgiyle dengeyi birlikte "
                "kurabileceğini düşündürüyor."
            ),
            model="test-model",
        )


class FakeScalarResult:
    def scalar_one_or_none(self):
        return None


class FakeSession:
    async def execute(self, *_: object, **__: object) -> FakeScalarResult:
        return FakeScalarResult()

    def add(self, _: object) -> None:
        pass

    async def commit(self) -> None:
        pass


def test_athena_interpretation_endpoint() -> None:
    app.dependency_overrides[get_athena_interpretation_service] = lambda: FakeAthenaService()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=uuid.uuid4())
    app.dependency_overrides[get_database_session] = lambda: FakeSession()
    try:
        response = client.post(
            "/api/v1/athena/natal-chart/interpret",
            json={
                "name": "Deniz",
                "local_datetime": "1990-07-15T14:30:00",
                "timezone_name": "America/Chicago",
                "latitude": 41.8796,
                "longitude": -87.6237,
                "place_name": "Art Institute of Chicago",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "interpretation": (
            "Haritandaki üç ana gösterge, sezgiyle dengeyi birlikte kurabileceğini düşündürüyor."
        ),
        "source": "openai",
        "model": "test-model",
        "cached": False,
    }
