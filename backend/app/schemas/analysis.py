"""Analysis Pydantic Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.commitment import CommitmentResponse


class AnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="Messy human communication (chat messages, email thread, meeting notes)",
        examples=["Rahul: I'll send the quotation tonight.\nRahul: I'll also update the pricing sheet tomorrow.\nMayur: Okay."],
    )
    source: str = Field(default="conversation", description="Source format or channel", examples=["conversation"])
    user_id: Optional[str] = Field(None, description="Optional user ID for scoping")


class AnalyzeResponse(BaseModel):
    analysis_id: str = Field(..., description="UUID tracking this analysis run")
    total_commitments: int = Field(..., description="Number of commitments discovered")
    commitments: List[CommitmentResponse] = Field(..., description="List of structured extracted commitments")
