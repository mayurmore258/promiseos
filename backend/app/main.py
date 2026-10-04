"""PromiseOS FastAPI Backend Application.

Central integration layer for discovering commitments, evidence retrieval,
verification, and human-supervised follow-up generation.
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import api_router
from app.core.config import settings
from app.core.exceptions import PromiseOSError
from app.core.logging import logger, request_id_var
from app.db.session import init_db
from app.utils.ids import generate_uuid


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize database tables and directories on startup."""
    logger.info("Initializing PromiseOS Backend...", extra={"operation": "startup"})
    # Ensure upload directory exists
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    # Initialize DB schema
    await init_db()
    logger.info(
        f"PromiseOS Backend running. Mode: {'MOCK_LLM' if settings.should_use_mock_llm() else 'EXTERNAL_PROVIDERS'}",
        extra={"operation": "startup"},
    )
    yield
    logger.info("PromiseOS Backend shutting down.", extra={"operation": "shutdown"})


app = FastAPI(
    title="PromiseOS Backend",
    version=settings.APP_VERSION,
    description=(
        "PromiseOS is an agentic AI system that discovers commitments from messy human communication, "
        "determines what evidence would prove fulfillment, searches available evidence, verifies the commitment, "
        "and prepares human-approved follow-ups."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request Context & Structured Logging Middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def logging_and_context_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or generate_uuid()
    request_id_var.set(req_id)

    start_time = time.time()
    logger.info(
        f"{request.method} {request.url.path} initiated",
        extra={"operation": "http_request", "endpoint": request.url.path},
    )

    try:
        response = await call_next(request)
        latency = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = req_id

        logger.info(
            f"{request.method} {request.url.path} finished {response.status_code} in {latency}ms",
            extra={
                "operation": "http_response",
                "endpoint": request.url.path,
                "status_code": response.status_code,
                "latency_ms": latency,
            },
        )
        return response
    except Exception as exc:
        latency = round((time.time() - start_time) * 1000, 2)
        logger.error(
            f"{request.method} {request.url.path} crashed after {latency}ms: {exc}",
            exc_info=True,
            extra={
                "operation": "http_error",
                "endpoint": request.url.path,
                "latency_ms": latency,
            },
        )
        raise exc


# ---------------------------------------------------------------------------
# Centralized Error Handlers
# ---------------------------------------------------------------------------
@app.exception_handler(PromiseOSError)
async def promiseos_exception_handler(request: Request, exc: PromiseOSError):
    """Handles all domain exceptions with structured error format."""
    return exc.to_response()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles FastAPI Pydantic schema validation failures."""
    details = {}
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []))
        details[field] = err.get("msg", "Invalid value")

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request body or parameters failed validation.",
                "details": details,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all error handler; masks internal errors in production responses."""
    logger.critical(f"Unhandled server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
                "details": {},
            }
        },
    )


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------
app.include_router(api_router)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs_url": "/docs",
    }
