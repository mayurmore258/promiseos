"""Integration tests for Database operations, repositories, and error handling."""

from datetime import datetime, timedelta
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.commitments import CommitmentRepository
from app.db.repositories.evidence import EvidenceRepository
from app.db.repositories.followups import FollowupRepository
from app.db.repositories.verification import VerificationRepository
from app.models.commitment import Commitment
from app.models.evidence import Evidence, EvidenceChunk
from app.models.followup import AnalysisRun, Followup
from app.models.user import User
from app.models.verification import VerificationResult
from app.utils.ids import generate_uuid


@pytest.mark.asyncio
async def test_database_table_creation_and_user(db_session: AsyncSession):
    user_id = generate_uuid()
    user = User(id=user_id, email=f"test_{user_id[:8]}@promiseos.local")
    db_session.add(user)
    await db_session.flush()

    fetched = await db_session.get(User, user_id)
    assert fetched is not None
    assert fetched.email.startswith("test_")


@pytest.mark.asyncio
async def test_commitment_repository_crud(db_session: AsyncSession):
    repo = CommitmentRepository(db_session)
    c_id = generate_uuid()

    c = Commitment(
        id=c_id,
        person="Rahul",
        action="Send",
        object="proposal",
        description="Send the proposal",
        deadline_raw="Friday",
        source="conversation",
        source_excerpt="I'll send the proposal Friday",
        expected_evidence=["proposal document", "timestamp"],
        status="pending",
        confidence=0.95,
    )
    created = await repo.create(c)
    assert created.id == c_id

    # Get by id
    fetched = await repo.get_by_id(c_id, load_relations=True)
    assert fetched is not None
    assert fetched.person == "Rahul"

    # List with filters
    items = await repo.list(status="pending", person="Rahul")
    assert any(i.id == c_id for i in items)

    # Update
    updated = await repo.update(fetched, {"object": "revised proposal", "status": "partial"})
    assert updated.object == "revised proposal"
    assert updated.status == "partial"

    # Delete
    await repo.delete(updated)
    assert await repo.get_by_id(c_id) is None


@pytest.mark.asyncio
async def test_evidence_and_chunk_repository(db_session: AsyncSession):
    com_repo = CommitmentRepository(db_session)
    ev_repo = EvidenceRepository(db_session)

    com = Commitment(
        id=generate_uuid(),
        person="Rahul",
        action="Send",
        object="quotation",
        description="Send quotation",
        source_excerpt="I'll send it",
        status="pending",
    )
    await com_repo.create(com)

    ev_id = generate_uuid()
    ev = Evidence(
        id=ev_id,
        commitment_id=com.id,
        file_name="quote.pdf",
        content_reference="uploads/quote.pdf",
        evidence_type="document",
        mime_type="application/pdf",
        file_size=1200,
        content_hash="aabbcc112233",
        relevance_score=0.9,
        source_type="uploaded_file",
        raw_text="Quotation details inside",
    )
    await ev_repo.create(ev)

    # Chunks
    chunks = [
        EvidenceChunk(
            id=generate_uuid(),
            evidence_id=ev_id,
            chunk_index=0,
            content="Chunk 1 content",
            metadata_json={"page": 1},
        ),
        EvidenceChunk(
            id=generate_uuid(),
            evidence_id=ev_id,
            chunk_index=1,
            content="Chunk 2 content",
            metadata_json={"page": 2},
        ),
    ]
    await ev_repo.create_chunks(chunks)

    # Fetch chunks
    all_chunks = await ev_repo.get_all_chunks_for_commitment(com.id)
    assert len(all_chunks) == 2
    assert all_chunks[0].chunk_index == 0

    # Find by hash
    found = await ev_repo.find_by_hash("aabbcc112233", commitment_id=com.id)
    assert found is not None
    assert found.id == ev_id


@pytest.mark.asyncio
async def test_verification_repository_and_followup_repository(db_session: AsyncSession):
    com_repo = CommitmentRepository(db_session)
    ver_repo = VerificationRepository(db_session)
    fol_repo = FollowupRepository(db_session)

    com = Commitment(
        id=generate_uuid(),
        person="Rahul",
        action="Send",
        object="report",
        description="Send weekly report",
        source_excerpt="Report coming soon",
        status="pending",
    )
    await com_repo.create(com)

    # Verification
    v_id = generate_uuid()
    v = VerificationResult(
        id=v_id,
        commitment_id=com.id,
        status="fulfilled",
        explanation="Report was verified.",
        evidence_summary="Verified via email.",
        confidence=0.95,
        verified_at=datetime.utcnow(),
    )
    await ver_repo.create(v)

    latest_v = await ver_repo.get_latest_by_commitment(com.id)
    assert latest_v is not None
    assert latest_v.status == "fulfilled"

    # Followup
    f_id = generate_uuid()
    f = Followup(
        id=f_id,
        commitment_id=com.id,
        draft="Hi Rahul, report looks good.",
        approved=False,
    )
    await fol_repo.create(f)

    # Human approves
    approved = await fol_repo.approve(f)
    assert approved.approved is True
    assert approved.approved_at is not None


@pytest.mark.asyncio
async def test_analysis_run_persistence(db_session: AsyncSession):
    run_id = generate_uuid()
    run = AnalysisRun(
        id=run_id,
        user_id=None,
        raw_input="Rahul: I'll send the quotation tonight.",
        extracted_count=1,
    )
    db_session.add(run)
    await db_session.flush()

    res = await db_session.get(AnalysisRun, run_id)
    assert res is not None
    assert res.extracted_count == 1
    assert "quotation" in res.raw_input


@pytest.mark.asyncio
async def test_database_rollback_on_error(db_session: AsyncSession):
    # Try inserting an invalid entity that violates constraints
    user_id = generate_uuid()
    u1 = User(id=user_id, email="unique@promiseos.local")
    db_session.add(u1)
    await db_session.flush()

    # Attempting duplicate unique email in the same session should raise error
    u2 = User(id=generate_uuid(), email="unique@promiseos.local")
    db_session.add(u2)
    with pytest.raises(Exception):
        await db_session.flush()

    await db_session.rollback()
