"""Verification API Routes."""

from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.verification import (
    VerificationRequest,
    VerificationResponse,
    VerificationReviewRequest,
)
from app.services.verification_service import VerificationService

router = APIRouter(prefix="/verify", tags=["Verification"])


@router.post(
    "/{commitment_id}",
    response_model=VerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Run Verification for Commitment",
    description="Evaluates all uploaded candidate evidence against the commitment, assigns a verifiable status, and generates a structured explanation.",
)
async def verify_commitment(
    commitment_id: str,
    body: Optional[VerificationRequest] = None,
    session: AsyncSession = Depends(get_db),
):
    notes = body.notes if body else None
    service = VerificationService(session)
    return await service.verify_commitment(commitment_id=commitment_id, notes=notes)


@router.post(
    "/{commitment_id}/review",
    response_model=VerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Human Review / Override Verification",
    description="Allows human reviewer to confirm or override verification outcome with notes.",
)
async def review_verification(
    commitment_id: str,
    review: VerificationReviewRequest,
    session: AsyncSession = Depends(get_db),
):
    service = VerificationService(session)
    return await service.review_verification(commitment_id=commitment_id, review=review)
