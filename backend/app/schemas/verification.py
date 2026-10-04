"""Verification Pydantic Schemas."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

VerificationStatus = Literal[
    "fulfilled",
    "partial",
    "unfulfilled",
    "unverified",
    "contradictory",
]


class VerificationRequest(BaseModel):
    commitment_id: Optional[str] = Field(None, description="Commitment ID (also in URL path)")
    notes: Optional[str] = Field(None, description="Optional extra context for the verification agent")


class VerificationEvidenceItem(BaseModel):
    file_name: str
    excerpt: str
    relevance_score: float = 0.0
    source_type: str = "uploaded_file"


class VerificationResponse(BaseModel):
    id: Optional[str] = Field(None, description="Verification record UUID")
    commitment_id: str = Field(..., description="UUID of verified commitment")
    status: VerificationStatus = Field(..., description="Verification status outcome")
    evidence: List[VerificationEvidenceItem] = Field(
        default_factory=list,
        description="Evidence items supporting this verification",
    )
    explanation: str = Field(
        ...,
        description="Detailed explanation covering what was promised, what evidence shows, what it proves, and what remains uncertain",
    )
    evidence_summary: str = Field(
        default="",
        description="Summary of evidence items evaluated",
    )
    missing_items: List[str] = Field(default_factory=list, description="Items required by commitment not found in evidence")
    contradictions: List[str] = Field(default_factory=list, description="Contradictory facts observed across evidence")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    verified_at: Optional[datetime] = None


class VerificationReviewRequest(BaseModel):
    status: VerificationStatus = Field(..., description="Human approved/overridden status")
    notes: Optional[str] = Field(None, description="Human reviewer justification")
