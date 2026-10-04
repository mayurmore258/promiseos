"""Ranking and scoring filters for candidate evidence."""

from typing import Any, Dict, List
from app.schemas.evidence import EvidenceMatchChunk


class CandidateRanker:
    """Ranks and selects top candidate evidence chunks."""

    def __init__(self, min_threshold: float = 0.05):
        self.min_threshold = min_threshold

    def rank(self, candidates: List[EvidenceMatchChunk], top_k: int = 5) -> List[EvidenceMatchChunk]:
        """Filters by minimum relevance and sorts descending by relevance_score."""
        filtered = [c for c in candidates if c.relevance_score >= self.min_threshold]
        # Sort by relevance_score descending
        ranked = sorted(filtered, key=lambda c: c.relevance_score, reverse=True)
        return ranked[:top_k]
