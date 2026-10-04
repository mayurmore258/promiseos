"""Followup API Routes."""

from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.followup import (
    FollowupApproveRequest,
    FollowupGenerateRequest,
    FollowupResponse,
)
from app.services.followup_service import FollowupService

router = APIRouter(prefix="/followup", tags=["Follow-ups"])


@router.post(
    "/{commitment_id}",
    response_model=FollowupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Follow-up Message Draft",
    description="Drafts a polite, non-accusatory message based on current verification status. Draft requires human approval and is never sent autonomously.",
)
async def generate_followup(
    commitment_id: str,
    request: Optional[FollowupGenerateRequest] = None,
    session: AsyncSession = Depends(get_db),
):
    tone = request.tone if request else "polite"
    custom_inst = request.custom_instruction if request else None
    service = FollowupService(session)
    return await service.generate_followup(
        commitment_id=commitment_id,
        tone=tone,
        custom_instruction=custom_inst,
    )


@router.post(
    "/{followup_id}/approve",
    response_model=FollowupResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve Follow-up Draft",
    description="Records human approval for a drafted follow-up message, optionally modifying draft text beforehand.",
)
async def approve_followup(
    followup_id: str,
    approval: FollowupApproveRequest,
    session: AsyncSession = Depends(get_db),
):
    service = FollowupService(session)
    return await service.approve_followup(followup_id=followup_id, approval=approval)
