"""API router registry."""

from fastapi import APIRouter
from .health import router as health_router
from .analyze import router as analyze_router
from .commitments import router as commitments_router
from .evidence import router as evidence_router
from .verification import router as verification_router
from .followups import router as followups_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(analyze_router)
api_router.include_router(commitments_router)
api_router.include_router(evidence_router)
api_router.include_router(verification_router)
api_router.include_router(followups_router)

__all__ = ["api_router"]
