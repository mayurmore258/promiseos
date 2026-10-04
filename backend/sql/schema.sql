-- ============================================================
-- PromiseOS Database Schema
-- Compatible with PostgreSQL 15+ and Supabase
-- ============================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. USERS
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. COMMITMENTS
CREATE TABLE IF NOT EXISTS commitments (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    person VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    object VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    deadline TIMESTAMP WITH TIME ZONE,
    deadline_raw VARCHAR(100),
    source VARCHAR(50) DEFAULT 'conversation' NOT NULL,
    source_excerpt TEXT NOT NULL,
    expected_evidence JSONB DEFAULT '[]'::jsonb NOT NULL,
    status VARCHAR(30) DEFAULT 'pending' NOT NULL,
    confidence FLOAT DEFAULT 0.9 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT check_commitment_status CHECK (
        status IN ('pending', 'fulfilled', 'partial', 'unfulfilled', 'unverified', 'contradictory')
    )
);

-- 3. EVIDENCE
CREATE TABLE IF NOT EXISTS evidence (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    commitment_id VARCHAR(36) REFERENCES commitments(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    content_reference VARCHAR(500) NOT NULL,
    evidence_type VARCHAR(50) DEFAULT 'document' NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size INTEGER DEFAULT 0 NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    relevance_score FLOAT DEFAULT 0.0 NOT NULL,
    source_type VARCHAR(50) DEFAULT 'uploaded_file' NOT NULL,
    raw_text TEXT,
    metadata_json JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 4. EVIDENCE CHUNKS
CREATE TABLE IF NOT EXISTS evidence_chunks (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    evidence_id VARCHAR(36) NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata_json JSONB DEFAULT '{}'::jsonb NOT NULL,
    embedding_reference VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 5. VERIFICATION RESULTS
CREATE TABLE IF NOT EXISTS verification_results (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    commitment_id VARCHAR(36) NOT NULL REFERENCES commitments(id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL,
    explanation TEXT NOT NULL,
    evidence_summary TEXT DEFAULT '' NOT NULL,
    missing_items JSONB DEFAULT '[]'::jsonb NOT NULL,
    contradictions JSONB DEFAULT '[]'::jsonb NOT NULL,
    confidence FLOAT DEFAULT 0.0 NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT check_verification_status CHECK (
        status IN ('fulfilled', 'partial', 'unfulfilled', 'unverified', 'contradictory')
    )
);

-- 6. FOLLOWUPS
CREATE TABLE IF NOT EXISTS followups (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    commitment_id VARCHAR(36) NOT NULL REFERENCES commitments(id) ON DELETE CASCADE,
    draft TEXT NOT NULL,
    approved BOOLEAN DEFAULT FALSE NOT NULL,
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 7. ANALYSIS RUNS (AUDIT)
CREATE TABLE IF NOT EXISTS analysis_runs (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    user_id VARCHAR(36),
    raw_input TEXT NOT NULL,
    extracted_count INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
