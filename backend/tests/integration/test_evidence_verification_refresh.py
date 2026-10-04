"""Regression tests for Evidence -> Verification Refresh bug.

Covers:
TEST 1: New evidence must be used by Verify Again (changes from UNVERIFIED to FULFILLED).
TEST 2: Verify Again recompiles fresh and updates conclusion on new evidence.
TEST 3: Current result selection returns newest verification result deterministically.
TEST 4: No evidence invariant (absence of evidence remains UNVERIFIED, never UNFULFILLED).
TEST 5: Exact DBMS regression with multi-turn conversation and priya_dbms_completion.txt.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.commitment import Commitment
from app.models.verification import VerificationResult
from app.services.analysis_service import AnalysisService
from app.services.commitment_service import CommitmentService
from app.services.evidence_service import EvidenceService
from app.services.verification_service import VerificationService
from app.utils.ids import generate_uuid


@pytest.mark.asyncio
async def test_1_new_evidence_must_be_used_on_verify_again(db_session: AsyncSession):
    """TEST 1: Create commitment, verify with no evidence (UNVERIFIED), add evidence, verify again (FULFILLED)."""
    analysis_svc = AnalysisService(db_session)
    res = await analysis_svc.analyze_text("Priya: I'll complete questions 1-5 tonight.")
    assert len(res.commitments) == 1
    cid = res.commitments[0].id

    # 1. Run initial verification with zero evidence
    ver_svc = VerificationService(db_session)
    v1 = await ver_svc.verify_commitment(cid)
    assert v1.status == "unverified"
    assert "No evidence has been provided yet" in v1.explanation
    assert len(v1.missing_items) > 0

    # 2. Upload relevant evidence
    ev_svc = EvidenceService(db_session)
    ev_bytes = (
        b"DBMS Assignment Completion\n\n"
        b"Priya has completed questions 1-5 of the DBMS assignment tonight.\n"
        b"Questions 1-5 are completed and ready for review."
    )
    await ev_svc.upload_evidence_file(
        file_bytes=ev_bytes,
        original_filename="priya_dbms_completion.txt",
        commitment_id=None,  # Uploaded to workspace
    )

    # 3. Call Verify Again
    v2 = await ver_svc.verify_commitment(cid)
    assert v2.status == "fulfilled"
    assert "No evidence has been provided yet" not in v2.explanation
    assert "All observable fulfillment criteria have been verified" in v2.explanation
    assert len(v2.missing_items) == 0
    assert v2.confidence >= 0.85

    # 4. Verify commitment detail reflects latest state
    comm_svc = CommitmentService(db_session)
    detail = await comm_svc.get_commitment_detail(cid)
    assert detail.status == "fulfilled"
    assert detail.verification is not None
    assert detail.verification["status"] == "fulfilled"
    assert len(detail.evidence) > 0
    assert any(e["file_name"] == "priya_dbms_completion.txt" for e in detail.evidence)


@pytest.mark.asyncio
async def test_2_verify_again_recomputes_with_updated_evidence(db_session: AsyncSession):
    """TEST 2: Verify Again recompiles fresh and updates conclusion on new evidence."""
    analysis_svc = AnalysisService(db_session)
    res = await analysis_svc.analyze_text("Rahul: I'll send the updated financial model by Friday.")
    cid = res.commitments[0].id

    ev_svc = EvidenceService(db_session)
    ver_svc = VerificationService(db_session)

    # 1. Add partial evidence
    await ev_svc.upload_evidence_file(
        file_bytes=b"Financial model draft partially completed, final logistics review is pending.",
        original_filename="financial_draft.txt",
        commitment_id=cid,
    )

    v1 = await ver_svc.verify_commitment(cid)
    assert v1.status == "partial"

    # 2. Add corroborating delivery confirmation
    await ev_svc.upload_evidence_file(
        file_bytes=b"The finalized financial model was delivered and proposal sent before Friday deadline.",
        original_filename="model_dispatch_receipt.txt",
        commitment_id=cid,
    )

    # 3. Verify Again
    v2 = await ver_svc.verify_commitment(cid)
    assert v2.status in ("fulfilled", "partial")
    # Must not be an unverified or stale first result ID
    assert v2.id != v1.id


@pytest.mark.asyncio
async def test_3_current_result_selection_deterministic_ordering(db_session: AsyncSession):
    """TEST 3: When multiple verification rows exist, commitment detail returns newest row deterministically."""
    comm = Commitment(
        id=generate_uuid(),
        person="Sara",
        action="Deploy",
        object="api",
        description="I will deploy the API tonight",
        source="conversation",
        source_excerpt="Sara: I will deploy the API tonight",
        expected_evidence=["deployment log"],
        status="unverified",
        confidence=0.9,
    )
    db_session.add(comm)
    await db_session.flush()

    # Create older verification result
    old_vr = VerificationResult(
        id=generate_uuid(),
        commitment_id=comm.id,
        status="unverified",
        explanation="Old unverified explanation",
        evidence_summary="None",
        missing_items=["log"],
        contradictions=[],
        confidence=0.5,
        created_at=datetime.utcnow() - timedelta(hours=2),
        verified_at=datetime.utcnow() - timedelta(hours=2),
    )
    # Create newer verification result
    new_vr = VerificationResult(
        id=generate_uuid(),
        commitment_id=comm.id,
        status="fulfilled",
        explanation="New verified fulfilled explanation",
        evidence_summary="Deployment verified",
        missing_items=[],
        contradictions=[],
        confidence=0.95,
        created_at=datetime.utcnow(),
        verified_at=datetime.utcnow(),
    )
    db_session.add_all([old_vr, new_vr])
    await db_session.flush()

    comm_svc = CommitmentService(db_session)
    detail = await comm_svc.get_commitment_detail(comm.id)
    assert detail.verification is not None
    assert detail.verification["id"] == new_vr.id
    assert detail.verification["status"] == "fulfilled"
    assert detail.verification["explanation"] == "New verified fulfilled explanation"


@pytest.mark.asyncio
async def test_4_no_evidence_invariant_remains_intact(db_session: AsyncSession):
    """TEST 4: Commitment with no evidence must be UNVERIFIED, never UNFULFILLED."""
    analysis_svc = AnalysisService(db_session)
    res = await analysis_svc.analyze_text("Marcus: I'll complete the security review by Monday.")
    cid = res.commitments[0].id

    ver_svc = VerificationService(db_session)
    v = await ver_svc.verify_commitment(cid)
    assert v.status == "unverified"
    assert v.status != "unfulfilled"
    assert "absence of evidence is not proof of failure" in v.explanation.lower()


@pytest.mark.asyncio
async def test_5_exact_dbms_regression_e2e(db_session: AsyncSession):
    """TEST 5: Multi-speaker DBMS conversation, questions rejected, evidence verified."""
    text = (
        "Neha: Have you completed the DBMS assignment?\n"
        "Priya: Not yet. I’ll complete questions 1–5 tonight.\n"
        "Neha: Okay, I’ll complete questions 6–10 and send them to you tomorrow morning.\n"
        "Priya: Perfect. Then I’ll combine everything and submit the assignment tomorrow."
    )

    analysis_svc = AnalysisService(db_session)
    analysis = await analysis_svc.analyze_text(text)

    # 1. Check commitments
    assert analysis.total_commitments == 3
    comms = analysis.commitments
    priya_q1_5 = next((c for c in comms if c.person == "Priya" and "1-5" in (c.object or "")), None)
    neha_q6_10 = next((c for c in comms if c.person == "Neha"), None)
    priya_submit = next((c for c in comms if c.person == "Priya" and "submit" in (c.description or "").lower()), None)

    assert priya_q1_5 is not None
    assert neha_q6_10 is not None
    assert priya_submit is not None

    # 2. Upload priya_dbms_completion.txt
    ev_svc = EvidenceService(db_session)
    await ev_svc.upload_evidence_file(
        file_bytes=(
            b"DBMS Assignment Completion\n\n"
            b"Priya has completed questions 1-5 of the DBMS assignment tonight.\n"
            b"Questions 1-5 are completed and ready for review."
        ),
        original_filename="priya_dbms_completion.txt",
        commitment_id=None,
    )

    # 3. Verify Priya's commitment
    ver_svc = VerificationService(db_session)
    ver = await ver_svc.verify_commitment(priya_q1_5.id)

    assert ver.status == "fulfilled"
    assert "No evidence has been provided yet" not in ver.explanation
    assert ver.confidence >= 0.85
    assert len(ver.missing_items) == 0
