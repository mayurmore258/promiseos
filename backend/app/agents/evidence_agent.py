"""Evidence Agent for managing retrieval, chunk evaluation, and candidate ranking."""

from typing import Any, Dict, List, Optional
from app.core.logging import logger
from app.evidence.retrieval import evidence_retriever
from app.models.commitment import Commitment
from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceMatchChunk, EvidenceSearchResult


class EvidenceAgent:
    """Discovers and ranks candidate evidence for a commitment."""

    async def search_evidence(
        self,
        commitment: Commitment,
        evidence_items: List[Evidence],
        top_k: int = 5,
        custom_query: Optional[str] = None,
    ) -> EvidenceSearchResult:
        logger.info(
            f"Searching evidence for commitment {commitment.id}",
            extra={"operation": "search_evidence", "commitment_id": commitment.id},
        )

        candidates: List[EvidenceMatchChunk] = evidence_retriever.retrieve(
            commitment=commitment,
            evidence_items=evidence_items,
            top_k=top_k,
            custom_query=custom_query,
        )

        return EvidenceSearchResult(
            commitment_id=commitment.id,
            total_found=len(candidates),
            candidates=candidates,
        )


evidence_agent = EvidenceAgent()
