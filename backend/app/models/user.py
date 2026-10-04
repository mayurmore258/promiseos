"""User database model."""

from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.utils.ids import generate_uuid

if TYPE_CHECKING:
    from .commitment import Commitment


class User(Base):
    """User entity representing the owner or actor."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    commitments: Mapped[List["Commitment"]] = relationship("Commitment", back_populates="user", cascade="all, delete-orphan")
