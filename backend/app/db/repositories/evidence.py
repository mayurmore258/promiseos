"""Repository for Evidence and EvidenceChunk persistence and queries."""

from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.evidence import Evidence, EvidenceChunk


class EvidenceRepository:
    """Encapsulates database operations for evidence files and chunks."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, evidence: Evidence) -> Evidence:
        self.session.add(evidence)
        await self.session.flush()
        await self.session.refresh(evidence)
        return evidence

    async def get_by_id(self, evidence_id: str, load_chunks: bool = False) -> Optional[Evidence]:
        stmt = select(Evidence).where(Evidence.id == evidence_id)
        if load_chunks:
            stmt = stmt.options(selectinload(Evidence.chunks))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def find_by_hash(self, content_hash: str, commitment_id: Optional[str] = None) -> Optional[Evidence]:
        stmt = select(Evidence).where(Evidence.content_hash == content_hash)
        if commitment_id:
            stmt = stmt.where(Evidence.commitment_id == commitment_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_commitment(self, commitment_id: str, include_unassigned: bool = False) -> List[Evidence]:
        stmt = (
            select(Evidence)
            .options(selectinload(Evidence.chunks))
            .order_by(desc(Evidence.created_at))
        )
        if include_unassigned:
            stmt = stmt.where((Evidence.commitment_id == commitment_id) | (Evidence.commitment_id.is_(None)))
        else:
            stmt = stmt.where(Evidence.commitment_id == commitment_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_chunks(self, chunks: List[EvidenceChunk]) -> List[EvidenceChunk]:
        self.session.add_all(chunks)
        await self.session.flush()
        return chunks

    async def get_all_chunks_for_commitment(self, commitment_id: str) -> List[EvidenceChunk]:
        stmt = (
            select(EvidenceChunk)
            .join(Evidence, Evidence.id == EvidenceChunk.evidence_id)
            .where(Evidence.commitment_id == commitment_id)
            .order_by(EvidenceChunk.chunk_index)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
