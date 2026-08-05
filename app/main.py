from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.v1.router import router as api_v1_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Olimora API",
        version="0.1.0",
        description="Deterministic astrology services for Olimora.",
    )
    app.include_router(api_v1_router, prefix="/api/v1")
    app.include_router(health_router)

    return app


app = create_app()
