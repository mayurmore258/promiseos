"""Unit tests for semantic matcher, candidate ranker, and retriever."""

import pytest
from app.evidence.matcher import EvidenceMatcher
from app.evidence.ranking import CandidateRanker
from app.schemas.evidence import EvidenceMatchChunk


def test_matcher_scoring_positive():
    matcher = EvidenceMatcher()
    commitment = {
        "person": "Rahul",
        "action": "Send",
        "object": "quotation",
        "description": "Send the quotation",
        "deadline_raw": "tonight",
        "expected_evidence": ["quotation document", "sent email/message", "timestamp"],
    }

    matching_text = "Official Quotation Ref #Q-2026-901 sent to Mayur tonight by Rahul."
    score, reasons = matcher.score(matching_text, commitment, file_name="quotation.txt")

    assert score > 0.5
    assert any("quotation" in r for r in reasons)
    assert any("rahul" in r for r in reasons)


def test_matcher_scoring_irrelevant():
    matcher = EvidenceMatcher()
    commitment = {
        "person": "Rahul",
        "action": "Send",
        "object": "quotation",
        "description": "Send the quotation",
        "deadline_raw": "tonight",
        "expected_evidence": ["quotation document"],
    }

    irrelevant_text = "The cafeteria will be closed on Sunday for routine pest control."
    score, reasons = matcher.score(irrelevant_text, commitment, file_name="notice.txt")

    assert score < 0.15


def test_candidate_ranker():
    ranker = CandidateRanker(min_threshold=0.2)
    candidates = [
        EvidenceMatchChunk(
            chunk_id="c1",
            evidence_id="e1",
            file_name="file1.txt",
            chunk_index=0,
            content="low score",
            relevance_score=0.1,
        ),
        EvidenceMatchChunk(
            chunk_id="c2",
            evidence_id="e2",
            file_name="file2.txt",
            chunk_index=0,
            content="high score",
            relevance_score=0.9,
        ),
        EvidenceMatchChunk(
            chunk_id="c3",
            evidence_id="e3",
            file_name="file3.txt",
            chunk_index=0,
            content="medium score",
            relevance_score=0.6,
        ),
    ]

    ranked = ranker.rank(candidates, top_k=2)
    assert len(ranked) == 2
    assert ranked[0].chunk_id == "c2"
    assert ranked[1].chunk_id == "c3"
