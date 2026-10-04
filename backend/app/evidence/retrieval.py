"""Evidence Retrieval Abstraction for finding evidence relevant to commitments."""

from typing import Any, Dict, List, Optional
from app.evidence.matcher import EvidenceMatcher
from app.evidence.ranking import CandidateRanker
from app.models.commitment import Commitment
from app.models.evidence import Evidence, EvidenceChunk
from app.schemas.evidence import EvidenceMatchChunk


class EvidenceRetriever:
    """Retrieves and ranks evidence segments matching a commitment."""

    def __init__(self):
        self.matcher = EvidenceMatcher()
        self.ranker = CandidateRanker()

    def retrieve(
        self,
        commitment: Commitment,
        evidence_items: List[Evidence],
        top_k: int = 5,
        custom_query: Optional[str] = None,
    ) -> List[EvidenceMatchChunk]:
        """Evaluates chunks across all supplied evidence files and returns top matches."""
        com_dict = {
            "id": commitment.id,
            "person": commitment.person,
            "action": commitment.action,
            "object": commitment.object,
            "description": custom_query or commitment.description,
            "deadline_raw": commitment.deadline_raw,
            "expected_evidence": commitment.expected_evidence or [],
        }

        candidates: List[EvidenceMatchChunk] = []

        for ev in evidence_items:
            # If evidence has chunks, evaluate chunks
            if ev.chunks:
                for chunk in ev.chunks:
                    score, reasons = self.matcher.score(
                        chunk_text=chunk.content,
                        commitment=com_dict,
                        file_name=ev.file_name,
                    )
                    candidates.append(
                        EvidenceMatchChunk(
                            chunk_id=chunk.id,
                            evidence_id=ev.id,
                            file_name=ev.file_name,
                            chunk_index=chunk.chunk_index,
                            content=chunk.content,
                            relevance_score=score,
                            match_reasons=reasons,
                        )
                    )
            # If no chunks were created, evaluate the raw text directly
            elif ev.raw_text:
                score, reasons = self.matcher.score(
                    chunk_text=ev.raw_text,
                    commitment=com_dict,
                    file_name=ev.file_name,
                )
                candidates.append(
                    EvidenceMatchChunk(
                        chunk_id=ev.id,
                        evidence_id=ev.id,
                        file_name=ev.file_name,
                        chunk_index=0,
                        content=ev.raw_text[:500],
                        relevance_score=score,
                        match_reasons=reasons,
                    )
                )

        return self.ranker.rank(candidates, top_k=top_k)


evidence_retriever = EvidenceRetriever()
