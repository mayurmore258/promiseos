"""Repository for Commitment persistence and queries."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.commitment import Commitment


class CommitmentRepository:
    """Encapsulates database operations for commitments."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, commitment: Commitment) -> Commitment:
        self.session.add(commitment)
        await self.session.flush()
        await self.session.refresh(commitment)
        return commitment

    async def get_by_id(self, commitment_id: str, load_relations: bool = False) -> Optional[Commitment]:
        stmt = select(Commitment).where(Commitment.id == commitment_id)
        if load_relations:
            stmt = stmt.options(
                selectinload(Commitment.evidence_items),
                selectinload(Commitment.verification_results),
                selectinload(Commitment.followups),
            )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list(
        self,
        status: Optional[str] = None,
        person: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Commitment]:
        stmt = select(Commitment).order_by(desc(Commitment.created_at))
        if status:
            stmt = stmt.where(Commitment.status == status)
        if person:
            stmt = stmt.where(Commitment.person.ilike(f"%{person}%"))
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, commitment: Commitment, update_dict: dict) -> Commitment:
        for key, value in update_dict.items():
            if hasattr(commitment, key) and value is not None:
                setattr(commitment, key, value)
        commitment.updated_at = datetime.utcnow()
        self.session.add(commitment)
        await self.session.flush()
        await self.session.refresh(commitment)
        return commitment

    async def delete(self, commitment: Commitment) -> None:
        await self.session.delete(commitment)
        await self.session.flush()
