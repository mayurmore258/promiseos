"""Repository for VerificationResult persistence and queries."""

from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.verification import VerificationResult


class VerificationRepository:
    """Encapsulates database operations for verification results."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, result: VerificationResult) -> VerificationResult:
        self.session.add(result)
        await self.session.flush()
        await self.session.refresh(result)
        return result

    async def get_by_id(self, result_id: str) -> Optional[VerificationResult]:
        stmt = select(VerificationResult).where(VerificationResult.id == result_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_latest_by_commitment(self, commitment_id: str) -> Optional[VerificationResult]:
        stmt = (
            select(VerificationResult)
            .where(VerificationResult.commitment_id == commitment_id)
            .order_by(desc(VerificationResult.created_at))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_by_commitment(self, commitment_id: str) -> List[VerificationResult]:
        stmt = (
            select(VerificationResult)
            .where(VerificationResult.commitment_id == commitment_id)
            .order_by(desc(VerificationResult.created_at))
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update(self, result: VerificationResult, update_dict: dict) -> VerificationResult:
        for key, value in update_dict.items():
            if hasattr(result, key) and value is not None:
                setattr(result, key, value)
        self.session.add(result)
        await self.session.flush()
        await self.session.refresh(result)
        return result
