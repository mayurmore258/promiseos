"""Commitment Pydantic Schemas."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

CommitmentStatus = Literal[
    "pending",
    "fulfilled",
    "partial",
    "unfulfilled",
    "unverified",
    "contradictory",
]


class CommitmentBase(BaseModel):
    person: str = Field(..., description="Who made the commitment", examples=["Rahul"])
    action: str = Field(..., description="Action to be performed", examples=["Send"])
    object: str = Field(..., description="Object or deliverable of commitment", examples=["quotation"])
    description: str = Field(..., description="Normalized human summary", examples=["Send the quotation"])
    deadline: Optional[datetime] = Field(None, description="Normalized ISO deadline if resolvable")
    deadline_raw: Optional[str] = Field(None, description="Original verbatim deadline text", examples=["tonight"])
    source: str = Field(default="conversation", description="Origin of commitment", examples=["conversation"])
    source_excerpt: str = Field(..., description="Verbatim text excerpt containing commitment", examples=["I'll send the quotation tonight."])
    expected_evidence: List[str] = Field(
        default_factory=list,
        description="Observable facts that would prove fulfillment",
        examples=[["quotation document", "sent message/email", "timestamp"]],
    )
    status: CommitmentStatus = Field(default="pending", description="Current verification status", examples=["pending"])
    confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="Extraction confidence", examples=[0.94])


class CommitmentCreate(CommitmentBase):
    user_id: Optional[str] = Field(None, description="Owner user ID if authenticated")
    ml_label: Optional[str] = Field(None, description="Local ML classification label (COMMITMENT or NON_COMMITMENT)")
    ml_confidence: Optional[float] = Field(None, description="Local ML commitment probability (0.0 to 1.0)")


class CommitmentUpdate(BaseModel):
    person: Optional[str] = Field(None, examples=["Rahul"])
    action: Optional[str] = Field(None, examples=["Send"])
    object: Optional[str] = Field(None, examples=["revised quotation"])
    description: Optional[str] = Field(None, examples=["Send the revised quotation"])
    deadline: Optional[datetime] = None
    deadline_raw: Optional[str] = Field(None, examples=["tomorrow 5 PM"])
    status: Optional[CommitmentStatus] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    expected_evidence: Optional[List[str]] = None


class CommitmentReviewRequest(BaseModel):
    status: CommitmentStatus = Field(..., description="Human reviewed/corrected status", examples=["fulfilled"])
    notes: Optional[str] = Field(None, description="Human reviewer notes or justification")


class CommitmentResponse(CommitmentBase):
    id: str = Field(..., description="Unique UUID of commitment", examples=["11111111-1111-1111-1111-111111111111"])
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CommitmentDetailResponse(CommitmentResponse):
    evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Linked evidence files")
    verification: Optional[Dict[str, Any]] = Field(None, description="Latest verification result")
    followup: Optional[Dict[str, Any]] = Field(None, description="Latest generated follow-up draft")

    model_config = {"from_attributes": True}
