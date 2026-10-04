-- ============================================================
-- PromiseOS Database Indexes
-- ============================================================

-- Commitments Indexes
CREATE INDEX IF NOT EXISTS idx_commitments_user_id ON commitments(user_id);
CREATE INDEX IF NOT EXISTS idx_commitments_status ON commitments(status);
CREATE INDEX IF NOT EXISTS idx_commitments_deadline ON commitments(deadline);
CREATE INDEX IF NOT EXISTS idx_commitments_person ON commitments(person);
CREATE INDEX IF NOT EXISTS idx_commitments_created_at ON commitments(created_at DESC);

-- Evidence Indexes
CREATE INDEX IF NOT EXISTS idx_evidence_commitment_id ON evidence(commitment_id);
CREATE INDEX IF NOT EXISTS idx_evidence_content_hash ON evidence(content_hash);
CREATE INDEX IF NOT EXISTS idx_evidence_created_at ON evidence(created_at DESC);

-- Evidence Chunks Indexes
CREATE INDEX IF NOT EXISTS idx_evidence_chunks_evidence_id ON evidence_chunks(evidence_id);
CREATE INDEX IF NOT EXISTS idx_evidence_chunks_index ON evidence_chunks(evidence_id, chunk_index);

-- Verification Results Indexes
CREATE INDEX IF NOT EXISTS idx_verification_commitment_id ON verification_results(commitment_id);
CREATE INDEX IF NOT EXISTS idx_verification_status ON verification_results(status);
CREATE INDEX IF NOT EXISTS idx_verification_created_at ON verification_results(created_at DESC);

-- Followup Indexes
CREATE INDEX IF NOT EXISTS idx_followups_commitment_id ON followups(commitment_id);
CREATE INDEX IF NOT EXISTS idx_followups_approved ON followups(approved);
