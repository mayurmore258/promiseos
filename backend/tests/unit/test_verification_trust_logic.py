"""Unit and Trust Logic tests for the PromiseOS Verification Engine.

Explicitly covers the 5 core scenarios and PromiseOS behavioral invariants:
- TEST 1: FULFILLED
- TEST 2: PARTIALLY FULFILLED
- TEST 3: UNFULFILLED
- TEST 4: NO EVIDENCE -> UNVERIFIED (MANDATORY REGRESSION CHECK)
- TEST 5: CONTRADICTORY
"""

from datetime import datetime
import pytest
from app.agents.verification_agent import verification_agent
from app.models.commitment import Commitment
from app.schemas.evidence import EvidenceMatchChunk
from app.utils.ids import generate_uuid


def _create_mock_commitment(desc: str = "Send Rahul the proposal by Friday") -> Commitment:
    return Commitment(
        id=generate_uuid(),
        person="Rahul",
        action="Send",
        object="proposal",
        description=desc,
        deadline_raw="Friday",
        source="conversation",
        source_excerpt="I'll send Rahul the proposal by Friday.",
        expected_evidence=["proposal document", "sent message", "timestamp"],
        status="pending",
        confidence=0.95,
    )


@pytest.mark.asyncio
async def test_verification_scenario_1_fulfilled():
    """TEST 1 — FULFILLED

    Commitment: 'I'll send Rahul the proposal by Friday.'
    Evidence: 'Proposal sent to Rahul Friday at 3:15 PM.'
    """
    commitment = _create_mock_commitment()
    evidence_chunks = [
        EvidenceMatchChunk(
            chunk_id=generate_uuid(),
            evidence_id=generate_uuid(),
            file_name="email_log.txt",
            chunk_index=0,
            content="Proposal sent to Rahul Friday at 3:15 PM via Outlook dispatch.",
            relevance_score=0.92,
            match_reasons=["Matched object 'proposal'", "Matched person 'Rahul'"],
        )
    ]

    result = await verification_agent.verify(commitment, evidence_chunks)

    assert result.status == "fulfilled"
    assert result.confidence >= 0.85
    assert len(result.evidence) == 1
    assert len(result.missing_items) == 0
    assert len(result.contradictions) == 0
    assert "proposal" in result.explanation.lower()


@pytest.mark.asyncio
async def test_verification_scenario_2_partially_fulfilled():
    """TEST 2 — PARTIALLY FULFILLED

    Commitment requires: proposal completed & sent.
    Evidence shows: Proposal completed but not sent (or delivery terms pending).
    """
    commitment = _create_mock_commitment()
    evidence_chunks = [
        EvidenceMatchChunk(
            chunk_id=generate_uuid(),
            evidence_id=generate_uuid(),
            file_name="drafts_folder.txt",
            chunk_index=0,
            content="Proposal draft completed but not sent. Pending manager signoff.",
            relevance_score=0.80,
            match_reasons=["Matched object 'proposal'"],
        )
    ]

    result = await verification_agent.verify(commitment, evidence_chunks)

    assert result.status == "partial"
    assert len(result.missing_items) >= 1
    assert "pending" in result.explanation.lower() or "not sent" in result.explanation.lower()


@pytest.mark.asyncio
async def test_verification_scenario_3_unfulfilled():
    """TEST 3 — UNFULFILLED

    Commitment: 'I'll send Rahul the proposal by Friday.'
    Evidence: Affirmative proof that deadline passed and deliverable was not sent.
    """
    commitment = _create_mock_commitment()
    evidence_chunks = [
        EvidenceMatchChunk(
            chunk_id=generate_uuid(),
            evidence_id=generate_uuid(),
            file_name="incident_log.txt",
            chunk_index=0,
            content="Deadline passed and proposal was cancelled and failed to deliver. Rahul is still waiting for the proposal.",
            relevance_score=0.88,
            match_reasons=["Affirmative failure record"],
        )
    ]

    result = await verification_agent.verify(commitment, evidence_chunks)

    assert result.status == "unfulfilled"
    assert len(result.missing_items) >= 1
    assert "not completed" in result.explanation.lower() or "non-delivery" in result.explanation.lower()


@pytest.mark.asyncio
async def test_verification_scenario_4_no_evidence_must_be_unverified():
    """TEST 4 — NO EVIDENCE -> UNVERIFIED

    MANDATORY TRUST LOGIC:
    Absence of evidence MUST NEVER be treated as proof of failure.
    """
    commitment = _create_mock_commitment()
    evidence_chunks = []  # Zero evidence items

    result = await verification_agent.verify(commitment, evidence_chunks)

    assert result.status == "unverified", "Failure: Zero evidence was incorrectly inferred as failure!"
    assert "unverified" in result.status
    assert "absence of evidence is not proof of failure" in result.explanation.lower()


@pytest.mark.asyncio
async def test_verification_scenario_5_contradictory():
    """TEST 5 — CONTRADICTORY

    Evidence A: 'Proposal sent Friday.'
    Evidence B: 'Rahul says he never received the proposal.'
    """
    commitment = _create_mock_commitment()
    evidence_chunks = [
        EvidenceMatchChunk(
            chunk_id=generate_uuid(),
            evidence_id=generate_uuid(),
            file_name="sender_sent_box.txt",
            chunk_index=0,
            content="Proposal sent Friday at 5:00 PM to Rahul.",
            relevance_score=0.90,
        ),
        EvidenceMatchChunk(
            chunk_id=generate_uuid(),
            evidence_id=generate_uuid(),
            file_name="recipient_inbox_check.txt",
            chunk_index=1,
            content="Rahul checked inbox and reported he never received the proposal.",
            relevance_score=0.88,
        ),
    ]

    result = await verification_agent.verify(commitment, evidence_chunks)

    assert result.status == "contradictory"
    assert len(result.contradictions) >= 1 or "conflicting" in result.explanation.lower()


@pytest.mark.asyncio
async def test_verification_output_schema_adherence():
    """Verifies that all required fields are populated in verification output."""
    commitment = _create_mock_commitment()
    result = await verification_agent.verify(commitment, [])

    # Check schema fields
    assert hasattr(result, "commitment_id")
    assert hasattr(result, "status")
    assert hasattr(result, "explanation")
    assert hasattr(result, "evidence_summary")
    assert hasattr(result, "missing_items")
    assert hasattr(result, "contradictions")
    assert hasattr(result, "confidence")
    assert hasattr(result, "verified_at")

    # Check bounds
    assert 0.0 <= result.confidence <= 1.0
    assert result.status in ("fulfilled", "partial", "unfulfilled", "unverified", "contradictory")
    assert isinstance(result.missing_items, list)
    assert isinstance(result.contradictions, list)
