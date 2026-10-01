"""
MUSNAD AI - FastAPI Application Entry Point
مُسنَد | AI Evidence & Verification Engine for Islamic Digital Content
"""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import configure_logging, get_logger
from app.api.v1 import api_router

# Configure logging first
configure_logging()
logger = get_logger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info(
        "musnad_startup",
        version=settings.APP_VERSION,
        env=settings.APP_ENV,
        kb_version=settings.KB_VERSION,
        demo_mode=settings.DEMO_MODE,
    )
    # Initialize database (enable pgvector extension)
    try:
        await init_db()
        logger.info("database_ready")
    except Exception as e:
        logger.error("database_init_failed", error=str(e))

    yield

    logger.info("musnad_shutdown")


# Create FastAPI app
app = FastAPI(
    title="MUSNAD AI",
    description=(
        "مُسنَد | AI Evidence & Verification Engine for Islamic Digital Content\n\n"
        "محرك ذكي للتحقق من المحتوى الإسلامي وتتبّع الأدلة والمصادر\n\n"
        "Core principle: CLAIM → EVIDENCE → SOURCE → VERIFICATION STATUS → EXPLANATION → ABSTENTION WHEN NECESSARY"
    ),
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)



# =========================================================================
# Middleware — Request logging
# =========================================================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", "")

    response = await call_next(request)

    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        request_id=request_id,
    )

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response


# =========================================================================
# Exception Handlers
# =========================================================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": exc.errors(),
            }
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred. Please try again.",
            }
        }
    )


# =========================================================================
# Include Routers
# =========================================================================
app.include_router(api_router)


# Root
@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "MUSNAD AI",
        "arabic": "مُسنَد",
        "description": "AI Evidence & Verification Engine for Islamic Digital Content",
        "version": settings.APP_VERSION,
        "kb_version": settings.KB_VERSION,
        "docs": "/docs" if settings.APP_DEBUG else "disabled_in_production",
    }