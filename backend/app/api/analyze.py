"""Analyze API Route."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze Communication Text",
    description=(
        "Ingests messy human communication (chat messages, email thread, notes), "
        "discovers explicit and implied commitments, plans expected evidence requirements, "
        "and persists the extracted commitments."
    ),
)
async def analyze_communication(
    request: AnalyzeRequest,
    session: AsyncSession = Depends(get_db),
):
    service = AnalysisService(session)
    return await service.analyze_text(
        text=request.text,
        source=request.source,
        user_id=request.user_id,
    )
