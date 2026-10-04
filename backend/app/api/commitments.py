"""Commitments API Routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.commitment import (
    CommitmentDetailResponse,
    CommitmentResponse,
    CommitmentReviewRequest,
    CommitmentUpdate,
)
from app.services.commitment_service import CommitmentService

router = APIRouter(prefix="/commitments", tags=["Commitments"])


@router.get(
    "",
    response_model=List[CommitmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Commitments",
    description="Returns commitments with optional filtering by status and committer name.",
)
async def list_commitments(
    status: Optional[str] = Query(None, description="Filter by status (pending, fulfilled, partial, unfulfilled, unverified, contradictory)"),
    person: Optional[str] = Query(None, description="Filter by person name (case-insensitive substring)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    service = CommitmentService(session)
    return await service.list_commitments(status=status, person=person, limit=limit, offset=offset)


@router.get(
    "/{commitment_id}",
    response_model=CommitmentDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Commitment Details",
    description="Returns the full commitment view including expected evidence, uploaded evidence items, verification results, and follow-up drafts.",
)
async def get_commitment_detail(
    commitment_id: str,
    session: AsyncSession = Depends(get_db),
):
    service = CommitmentService(session)
    return await service.get_commitment_detail(commitment_id)


@router.patch(
    "/{commitment_id}",
    response_model=CommitmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Commitment",
    description="Allows manual editing of person, action, object, description, deadline, or expected evidence.",
)
async def update_commitment(
    commitment_id: str,
    update_data: CommitmentUpdate,
    session: AsyncSession = Depends(get_db),
):
    service = CommitmentService(session)
    return await service.update_commitment(commitment_id, update_data)


@router.post(
    "/{commitment_id}/review",
    response_model=CommitmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Human Review Commitment",
    description="Records human approval, override, or correction of commitment status.",
)
async def review_commitment(
    commitment_id: str,
    review: CommitmentReviewRequest,
    session: AsyncSession = Depends(get_db),
):
    service = CommitmentService(session)
    return await service.review_commitment(commitment_id, review)
