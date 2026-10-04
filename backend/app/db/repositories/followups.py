"""Repository for Followup message persistence and human approvals."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.followup import Followup


class FollowupRepository:
    """Encapsulates database operations for follow-up message drafts."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, followup: Followup) -> Followup:
        self.session.add(followup)
        await self.session.flush()
        await self.session.refresh(followup)
        return followup

    async def get_by_id(self, followup_id: str) -> Optional[Followup]:
        stmt = select(Followup).where(Followup.id == followup_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_latest_by_commitment(self, commitment_id: str) -> Optional[Followup]:
        stmt = (
            select(Followup)
            .where(Followup.commitment_id == commitment_id)
            .order_by(desc(Followup.created_at))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_by_commitment(self, commitment_id: str) -> List[Followup]:
        stmt = (
            select(Followup)
            .where(Followup.commitment_id == commitment_id)
            .order_by(desc(Followup.created_at))
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def approve(self, followup: Followup) -> Followup:
        """Records human approval for this draft."""
        followup.approved = True
        followup.approved_at = datetime.utcnow()
        self.session.add(followup)
        await self.session.flush()
        await self.session.refresh(followup)
        return followup

    async def update(self, followup: Followup, update_dict: dict) -> Followup:
        for key, value in update_dict.items():
            if hasattr(followup, key) and value is not None:
                setattr(followup, key, value)
        self.session.add(followup)
        await self.session.flush()
        await self.session.refresh(followup)
        return followup
