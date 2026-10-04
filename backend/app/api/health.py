"""Health and Readiness Check Endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_db
from app.schemas.common import HealthResponse, ReadyResponse

router = APIRouter(tags=["Health & Status"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Returns simple server health status.",
)
async def health_check():
    return HealthResponse(status="ok", app=settings.APP_NAME, version=settings.APP_VERSION)


@router.get(
    "/ready",
    response_model=ReadyResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Reports connectivity to database, storage, and AI router status without revealing secrets.",
)
async def readiness_check(session: AsyncSession = Depends(get_db)):
    # Check DB connectivity
    db_status = "connected"
    try:
        await session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check Storage
    storage_status = "ready" if settings.upload_path.exists() else "not_found"

    # LLM Router status
    llm_mode = "mock" if settings.should_use_mock_llm() else "active_providers"
    active_providers = ["mock"] if settings.should_use_mock_llm() else settings.active_llm_providers

    overall = "ready" if db_status == "connected" and storage_status == "ready" else "degraded"

    return ReadyResponse(
        status=overall,
        database=db_status,
        storage=storage_status,
        llm_mode=llm_mode,
        active_providers=active_providers,
    )
