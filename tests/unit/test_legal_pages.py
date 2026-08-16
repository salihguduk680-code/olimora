from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.legal import router


def test_public_legal_pages_are_available() -> None:
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    for path in ("/privacy", "/terms", "/account-deletion"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert "OLIMORA" in response.text
