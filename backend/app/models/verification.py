"""VerificationResult database model."""

from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.utils.ids import generate_uuid

if TYPE_CHECKING:
    from .commitment import Commitment


class VerificationResult(Base):
    """The result of an evidence verification process for a commitment."""

    __tablename__ = "verification_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    commitment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("commitments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Status: fulfilled | partial | unfulfilled | unverified | contradictory
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_summary: Mapped[str] = mapped_column(Text, default="", nullable=False)

    missing_items: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)
    contradictions: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    verified_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    commitment: Mapped["Commitment"] = relationship("Commitment", back_populates="verification_results")
