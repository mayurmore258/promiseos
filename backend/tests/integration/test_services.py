"""Integration tests for Service layer operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.commitment import CommitmentReviewRequest, CommitmentUpdate
from app.schemas.followup import FollowupApproveRequest
from app.schemas.verification import VerificationReviewRequest
from app.services.analysis_service import AnalysisService
from app.services.commitment_service import CommitmentService
from app.services.evidence_service import EvidenceService
from app.services.followup_service import FollowupService
from app.services.verification_service import VerificationService


@pytest.mark.asyncio
async def test_analysis_service_lifecycle(db_session: AsyncSession):
    svc = AnalysisService(db_session)
    text = "Rahul: I'll send the quotation tonight.\nRahul: I'll also update the pricing sheet tomorrow.\nMayur: Okay."

    resp = await svc.analyze_text(text=text, source="conversation")
    assert resp.total_commitments == 2
    assert len(resp.commitments) == 2
    assert resp.commitments[0].person == "Rahul"
    assert len(resp.commitments[0].expected_evidence) > 0


@pytest.mark.asyncio
async def test_evidence_service_upload_and_deduplication(db_session: AsyncSession):
    analysis_svc = AnalysisService(db_session)
    analysis = await analysis_svc.analyze_text("Rahul: I'll send the quotation tonight.")
    com_id = analysis.commitments[0].id

    evidence_svc = EvidenceService(db_session)
    file_bytes = b"Official Quotation Ref #Q-2026-901 sent to Mayur."

    # First upload
    up1 = await evidence_svc.upload_evidence_file(
        file_bytes=file_bytes,
        original_filename="quotation.txt",
        commitment_id=com_id,
    )
    assert up1.is_duplicate is False
    assert up1.file_name == "quotation.txt"

    # Second upload of identical content -> deduplication!
    up2 = await evidence_svc.upload_evidence_file(
        file_bytes=file_bytes,
        original_filename="quotation.txt",
        commitment_id=com_id,
    )
    assert up2.is_duplicate is True
    assert up2.id == up1.id


@pytest.mark.asyncio
async def test_verification_and_followup_services(db_session: AsyncSession):
    # 1. Analyze
    analysis_svc = AnalysisService(db_session)
    analysis = await analysis_svc.analyze_text("Rahul: I'll also update the pricing sheet tomorrow.")
    com_id = analysis.commitments[0].id

    # 2. Upload partial evidence
    evidence_svc = EvidenceService(db_session)
    csv_bytes = b"Product,Price,Delivery\nWidget A,$50,TBD - Pending Logistics"
    await evidence_svc.upload_evidence_file(
        file_bytes=csv_bytes,
        original_filename="pricing.csv",
        commitment_id=com_id,
    )

    # 3. Verify
    ver_svc = VerificationService(db_session)
    ver = await ver_svc.verify_commitment(com_id)
    assert ver.status in ("partial", "fulfilled")
    assert ver.confidence > 0.0

    # 4. Generate follow-up draft
    followup_svc = FollowupService(db_session)
    f_draft = await followup_svc.generate_followup(com_id)
    assert f_draft.approved is False
    assert "Rahul" in f_draft.draft

    # 5. Approve follow-up
    f_approved = await followup_svc.approve_followup(
        followup_id=f_draft.id,
        approval=FollowupApproveRequest(approved=True, edited_draft="Hi Rahul, please send the delivery update."),
    )
    assert f_approved.approved is True
    assert f_approved.approved_at is not None
    assert "please send the delivery update" in f_approved.draft
