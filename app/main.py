from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app.api.health import router as health_router
from app.api.v1.router import router as api_v1_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    production = settings.app_env.lower() == "production"
    app = FastAPI(
        title="Olimora API",
        version="0.1.0",
        description="Deterministic astrology services for Olimora.",
        docs_url=None if production else "/docs",
        redoc_url=None if production else "/redoc",
        openapi_url=None if production else "/openapi.json",
    )

    @app.middleware("http")
    async def security_middleware(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                too_large = int(content_length) > 64 * 1024
            except ValueError:
                too_large = True
            if too_large:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "İstek gövdesi çok büyük."},
                )
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        if production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    app.include_router(api_v1_router, prefix="/api/v1")
    app.include_router(health_router)

    return app


app = create_app()
