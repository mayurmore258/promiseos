"""Database Seeding Script for PromiseOS.

Loads deterministic sample data into the configured database (SQLite or PostgreSQL/Supabase).
Usage:
    python -m scripts.seed_database
"""

import asyncio
from datetime import datetime, timedelta, time
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import logger
from app.db.session import AsyncSessionLocal, init_db
from app.models.commitment import Commitment
from app.models.evidence import Evidence
from app.models.followup import Followup
from app.models.user import User
from app.models.verification import VerificationResult


async def seed():
    logger.info("Initializing database tables before seeding...")
    await init_db()

    async with AsyncSessionLocal() as session:
        # 1. Create Demo User
        user_id = "00000000-0000-0000-0000-000000000001"
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, email="mayur@promiseos.local")
            session.add(user)
            await session.flush()
            logger.info("Created demo user: mayur@promiseos.local")

        now = datetime.now()
        tonight = datetime.combine(now.date(), time(23, 59, 59))
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(23, 59, 59))

        # 2. Commitment 1 (Send quotation)
        c1_id = "11111111-1111-1111-1111-111111111111"
        c1 = await session.get(Commitment, c1_id)
        if not c1:
            c1 = Commitment(
                id=c1_id,
                user_id=user_id,
                person="Rahul",
                action="Send",
                object="quotation",
                description="Send the quotation",
                deadline=tonight,
                deadline_raw="tonight",
                source="conversation",
                source_excerpt="Rahul: I'll send the quotation tonight.",
                expected_evidence=["quotation document", "sent email/message", "timestamp"],
                status="fulfilled",
                confidence=0.95,
            )
            session.add(c1)
            logger.info("Seeded Commitment 1: Send quotation")

        # 3. Commitment 2 (Update pricing sheet)
        c2_id = "22222222-2222-2222-2222-222222222222"
        c2 = await session.get(Commitment, c2_id)
        if not c2:
            c2 = Commitment(
                id=c2_id,
                user_id=user_id,
                person="Rahul",
                action="Update",
                object="pricing sheet",
                description="Update the pricing sheet",
                deadline=tomorrow,
                deadline_raw="tomorrow",
                source="conversation",
                source_excerpt="Rahul: I'll also update the pricing sheet tomorrow.",
                expected_evidence=["updated pricing sheet / CSV", "delivery cost updates", "version change log"],
                status="partial",
                confidence=0.92,
            )
            session.add(c2)
            logger.info("Seeded Commitment 2: Update pricing sheet")

        # 4. Evidence for Commitment 1
        e1_id = "33333333-3333-3333-3333-333333333331"
        e1 = await session.get(Evidence, e1_id)
        if not e1:
            e1 = Evidence(
                id=e1_id,
                commitment_id=c1_id,
                file_name="quotation.txt",
                content_reference="data/test_evidence/quotation.txt",
                evidence_type="document",
                mime_type="text/plain",
                file_size=650,
                content_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                relevance_score=0.96,
                source_type="uploaded_file",
                raw_text="Official Quotation Ref #Q-2026-901 sent to Mayur via email at 21:15 IST. Total $12,500.",
                metadata_json={"author": "Rahul"},
            )
            session.add(e1)

        # 5. Evidence for Commitment 2
        e2_id = "33333333-3333-3333-3333-333333333332"
        e2 = await session.get(Evidence, e2_id)
        if not e2:
            e2 = Evidence(
                id=e2_id,
                commitment_id=c2_id,
                file_name="pricing.csv",
                content_reference="data/test_evidence/pricing.csv",
                evidence_type="sheet",
                mime_type="text/csv",
                file_size=320,
                content_hash="f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2",
                relevance_score=0.88,
                source_type="uploaded_file",
                raw_text="SKU,Item Description,Base Price,Delivery Cost\nPRD-001,Widget Standard Tier,$45.00,TBD - Pending Logistics Update",
                metadata_json={"author": "Rahul"},
            )
            session.add(e2)

        # 6. Verification Results
        v1_id = "44444444-4444-4444-4444-444444444441"
        v1 = await session.get(VerificationResult, v1_id)
        if not v1:
            v1 = VerificationResult(
                id=v1_id,
                commitment_id=c1_id,
                status="fulfilled",
                explanation=(
                    "Rahul promised to send the quotation tonight. Uploaded evidence quotation.txt "
                    "verifies Quotation Ref #Q-2026-901 was dispatched before the deadline with pricing and delivery terms."
                ),
                evidence_summary="Quotation document verified with dispatch timestamp.",
                missing_items=[],
                contradictions=[],
                confidence=0.95,
            )
            session.add(v1)

        v2_id = "44444444-4444-4444-4444-444444444442"
        v2 = await session.get(VerificationResult, v2_id)
        if not v2:
            v2 = VerificationResult(
                id=v2_id,
                commitment_id=c2_id,
                status="partial",
                explanation=(
                    "Rahul promised to update the pricing sheet tomorrow. Evidence from pricing.csv "
                    "confirms catalog base prices have been updated, but delivery costs remain flagged as TBD."
                ),
                evidence_summary="Base prices updated; delivery costs unresolved.",
                missing_items=["Delivery Cost finalized in catalog"],
                contradictions=[],
                confidence=0.88,
            )
            session.add(v2)

        # 7. Follow-up Draft
        f2_id = "55555555-5555-5555-5555-555555555552"
        f2 = await session.get(Followup, f2_id)
        if not f2:
            f2 = Followup(
                id=f2_id,
                commitment_id=c2_id,
                draft=(
                    "Hi Rahul, thanks for updating the base catalog prices. "
                    "We noticed delivery costs are still listed as TBD. Could you share the delivery figures when available?"
                ),
                approved=False,
            )
            session.add(f2)

        await session.commit()
        logger.info("Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
