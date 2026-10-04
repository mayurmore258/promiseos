"""Followup Pydantic Schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FollowupGenerateRequest(BaseModel):
    commitment_id: Optional[str] = Field(None, description="Target commitment UUID (also in URL path)")
    tone: str = Field(default="polite", description="Tone for draft: polite | professional | gentle_reminder")
    custom_instruction: Optional[str] = Field(None, description="Optional custom guidelines for draft")


class FollowupApproveRequest(BaseModel):
    approved: bool = Field(default=True, description="Human approval decision")
    edited_draft: Optional[str] = Field(None, description="Optional modified text draft edited by human before approval")


class FollowupResponse(BaseModel):
    id: str = Field(..., description="Unique UUID of follow-up")
    commitment_id: str = Field(..., description="UUID of linked commitment")
    draft: str = Field(..., description="Polite, non-accusatory draft message")
    approved: bool = Field(default=False, description="Whether human has approved this draft")
    approved_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
