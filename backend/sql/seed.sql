-- ============================================================
-- PromiseOS Deterministic Seed Data
-- ============================================================

-- 1. Insert Demo User
INSERT INTO users (id, email, created_at)
VALUES ('00000000-0000-0000-0000-000000000001', 'mayur@promiseos.local', CURRENT_TIMESTAMP)
ON CONFLICT (id) DO NOTHING;

-- 2. Commitment 1: Send quotation tonight
INSERT INTO commitments (
    id,
    user_id,
    person,
    action,
    object,
    description,
    deadline,
    deadline_raw,
    source,
    source_excerpt,
    expected_evidence,
    status,
    confidence,
    created_at,
    updated_at
)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    '00000000-0000-0000-0000-000000000001',
    'Rahul',
    'Send',
    'quotation',
    'Send the quotation',
    CURRENT_DATE + TIME '23:59:59',
    'tonight',
    'conversation',
    'Rahul: I''ll send the quotation tonight.',
    '["quotation document", "sent email/message", "timestamp"]'::jsonb,
    'fulfilled',
    0.95,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (id) DO NOTHING;

-- 3. Commitment 2: Update pricing sheet tomorrow
INSERT INTO commitments (
    id,
    user_id,
    person,
    action,
    object,
    description,
    deadline,
    deadline_raw,
    source,
    source_excerpt,
    expected_evidence,
    status,
    confidence,
    created_at,
    updated_at
)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    '00000000-0000-0000-0000-000000000001',
    'Rahul',
    'Update',
    'pricing sheet',
    'Update the pricing sheet',
    CURRENT_DATE + INTERVAL '1 day' + TIME '23:59:59',
    'tomorrow',
    'conversation',
    'Rahul: I''ll also update the pricing sheet tomorrow.',
    '["updated pricing sheet / CSV", "delivery cost updates", "version change log"]'::jsonb,
    'partial',
    0.92,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (id) DO NOTHING;

-- 4. Evidence for Commitment 1 (Quotation file)
INSERT INTO evidence (
    id,
    commitment_id,
    file_name,
    content_reference,
    evidence_type,
    mime_type,
    file_size,
    content_hash,
    relevance_score,
    source_type,
    raw_text,
    metadata_json,
    created_at
)
VALUES (
    '33333333-3333-3333-3333-333333333331',
    '11111111-1111-1111-1111-111111111111',
    'quotation_revised.txt',
    'data/uploads/quotation_revised.txt',
    'document',
    'text/plain',
    1024,
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    0.96,
    'uploaded_file',
    'Quotation ref #Q-2026-901 sent to Mayur via email at 20:45 PM. Total amount: $12,500. Delivery terms included.',
    '{"author": "Rahul", "file_type": "txt"}'::jsonb,
    CURRENT_TIMESTAMP
)
ON CONFLICT (id) DO NOTHING;

-- 5. Evidence for Commitment 2 (Pricing sheet with missing delivery cost update)
INSERT INTO evidence (
    id,
    commitment_id,
    file_name,
    content_reference,
    evidence_type,
    mime_type,
    file_size,
    content_hash,
    relevance_score,
    source_type,
    raw_text,
    metadata_json,
    created_at
)
VALUES (
    '33333333-3333-3333-3333-333333333332',
    '22222222-2222-2222-2222-222222222222',
    'pricing_sheet_v2.csv',
    'data/uploads/pricing_sheet_v2.csv',
    'sheet',
    'text/csv',
    2048,
    'f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2',
    0.85,
    'uploaded_file',
    'Product,Base Price,Status\nWidget A,$50,Updated\nWidget B,$80,Updated\nDelivery Cost,TBD,Pending Verification',
    '{"author": "Rahul", "file_type": "csv"}'::jsonb,
    CURRENT_TIMESTAMP
)
ON CONFLICT (id) DO NOTHING;

-- 6. Verification Results
INSERT INTO verification_results (
    id,
    commitment_id,
    status,
    explanation,
    evidence_summary,
    missing_items,
    contradictions,
    confidence,
    verified_at,
    created_at
)
VALUES (
    '44444444-4444-4444-4444-444444444441',
    '11111111-1111-1111-1111-111111111111',
    'fulfilled',
    'Rahul promised to send the quotation tonight. Uploaded evidence quotation_revised.txt confirms Quotation #Q-2026-901 was dispatched with full pricing and delivery terms before midnight.',
    'Quotation document with timestamp 20:45 PM verifies delivery.',
    '[]'::jsonb,
    '[]'::jsonb,
    0.95,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO verification_results (
    id,
    commitment_id,
    status,
    explanation,
    evidence_summary,
    missing_items,
    contradictions,
    confidence,
    verified_at,
    created_at
)
VALUES (
    '44444444-4444-4444-4444-444444444442',
    '22222222-2222-2222-2222-222222222222',
    'partial',
    'Rahul promised to update the pricing sheet. Base prices for Widget A and B were updated in pricing_sheet_v2.csv, but delivery costs remain marked as TBD.',
    'pricing_sheet_v2.csv contains updated base prices but delivery charges remain unresolved.',
    '["Delivery Cost finalized in sheet"]'::jsonb,
    '[]'::jsonb,
    0.88,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (id) DO NOTHING;

-- 7. Followup Drafts (Waiting for Human Approval)
INSERT INTO followups (
    id,
    commitment_id,
    draft,
    approved,
    approved_at,
    created_at
)
VALUES (
    '55555555-5555-5555-5555-555555555552',
    '22222222-2222-2222-2222-222222222222',
    'Hi Rahul, thanks for updating the base prices on the pricing sheet. We noticed the delivery cost row is still marked TBD. Could you share the updated delivery figures when you get a chance?',
    FALSE,
    NULL,
    CURRENT_TIMESTAMP
)
ON CONFLICT (id) DO NOTHING;
