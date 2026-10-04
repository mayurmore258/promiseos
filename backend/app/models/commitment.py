"""Commitment database model."""

from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.utils.ids import generate_uuid

if TYPE_CHECKING:
    from .user import User
    from .evidence import Evidence
    from .verification import VerificationResult
    from .followup import Followup


class Commitment(Base):
    """Discovered commitment extracted from communication."""

    __tablename__ = "commitments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    person: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    object: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    deadline_raw: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    source: Mapped[str] = mapped_column(String(50), default="conversation", nullable=False)
    source_excerpt: Mapped[str] = mapped_column(Text, nullable=False)

    # List of planned/expected evidence strings or requirement objects
    expected_evidence: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)

    # Status: pending | fulfilled | partial | unfulfilled | unverified | contradictory
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.9, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="commitments")
    evidence_items: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="commitment", cascade="all, delete-orphan")
    verification_results: Mapped[List["VerificationResult"]] = relationship("VerificationResult", back_populates="commitment", cascade="all, delete-orphan", order_by="VerificationResult.created_at")
    followups: Mapped[List["Followup"]] = relationship("Followup", back_populates="commitment", cascade="all, delete-orphan", order_by="Followup.created_at")
