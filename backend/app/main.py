from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app import __version__
from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import logger
from app.repositories.db import close_db, init_db

settings = get_settings()


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Protects server by enforcing maximum content length on incoming requests."""

    def __init__(self, app, max_bytes: int):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > self.max_bytes:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "success": False,
                            "detail": f"Payload size exceeds allowed maximum limit ({self.max_bytes // (1024 * 1024)}MB).",
                            "code": "PAYLOAD_TOO_LARGE",
                        },
                    )
            except ValueError:
                pass
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and graceful shutdown lifecycles."""
    logger.info("Initializing AI Excel Insights application v%s...", __version__)
    logger.info("Environment: %s | Upload limit: %d MB", settings.APP_ENV, settings.MAX_UPLOAD_MB)
    try:
        init_db()
    except Exception as exc:
        logger.warning("Startup database initialization non-fatal error: %s", exc)

    yield

    logger.info("Shutting down AI Excel Insights backend...")
    close_db()


def create_application() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title="AI Excel Insights API",
        description="Production-grade automated spreadsheet intelligence, financial profiling, Recharts specs, and AI analytics.",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 1. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Payload size limiter (Max Upload MB + 2MB overhead for multipart metadata)
    app.add_middleware(
        RequestSizeLimitMiddleware,
        max_bytes=(settings.MAX_UPLOAD_MB + 2) * 1024 * 1024,
    )

    # 3. Mount API Routers
    app.include_router(api_router)

    # 4. Exception Handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "detail": exc.detail,
                "code": "HTTP_EXCEPTION",
            },
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "detail": "Request validation failed",
                "code": "VALIDATION_ERROR",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled internal server error on %s: %s", request.url.path, exc, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "detail": "An internal server error occurred.",
                "code": "INTERNAL_SERVER_ERROR",
            },
        )

    return app


app = create_application()
