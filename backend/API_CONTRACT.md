# PromiseOS Backend API Contract

> **Target Audience:** Frontend Teammate (React + Vite)  
> **Base URL:** `http://localhost:8000/api`  
> **Swagger UI:** `http://localhost:8000/docs`  
> **OpenAPI JSON:** `http://localhost:8000/openapi.json`  
> **Specification Version:** 1.0.0

---

## Architecture Overview

PromiseOS backend exposes a clean REST API for discovering commitments, managing evidence, running verification, and generating human-reviewed follow-ups.

```
Frontend (React/Vite)
       │ HTTP / JSON / Multipart
       ▼
PromiseOS FastAPI Backend (/api)
  ├── POST   /api/analyze              (Analyze conversation -> extract commitments)
  ├── GET    /api/commitments          (List commitments with filters)
  ├── GET    /api/commitments/{id}     (Full commitment detail + evidence + verification + followups)
  ├── PATCH  /api/commitments/{id}     (Edit commitment details)
  ├── POST   /api/commitments/{id}/review (Human review/override commitment status)
  ├── POST   /api/evidence/upload      (Multipart file upload: TXT, PDF, DOCX, CSV, XLSX)
  ├── POST   /api/evidence/search      (Retrieve and rank evidence chunks for commitment)
  ├── POST   /api/verify/{id}          (Trigger verification engine)
  ├── POST   /api/verify/{id}/review   (Human review/override verification result)
  ├── POST   /api/followup/{id}        (Generate follow-up draft)
  ├── POST   /api/followup/{id}/approve(Human approves follow-up draft)
  ├── GET    /api/health               (Health check)
  └── GET    /api/ready                (Readiness check)
```

---

## Standard Error Format

All error responses return HTTP status `>= 400` with this exact JSON schema:

```json
{
  "error": {
    "code": "COMMITMENT_NOT_FOUND",
    "message": "Commitment '11111111-1111-1111-1111-111111111111' was not found.",
    "details": {
      "resource": "commitment",
      "id": "11111111-1111-1111-1111-111111111111"
    }
  }
}
```

### Common Error Codes:
- `VALIDATION_ERROR` (422): Malformed request body, missing fields, or empty conversation.
- `COMMITMENT_NOT_FOUND` (404): Specified commitment UUID does not exist.
- `EVIDENCE_NOT_FOUND` (404): Evidence ID not found.
- `FOLLOWUP_NOT_FOUND` (404): Follow-up ID not found.
- `UNSUPPORTED_FILE_TYPE` (400): File extension not in supported set (`.txt, .pdf, .docx, .csv, .xlsx, .md, .json`).
- `FILE_SIZE_EXCEEDED` (413): File exceeds `MAX_UPLOAD_SIZE_MB` (default: 25MB).
- `MALFORMED_FILE` (400): Corrupted or unparseable document.
- `SECURITY_VIOLATION` (400): Attempted path traversal or unsafe file access.
- `INTERNAL_SERVER_ERROR` (500): Server error (no credentials or stack traces exposed).

---

## Commitment Status Lifecycle

```
[ pending ] ──► (evidence uploaded) ──► POST /api/verify/{id}
                                                 │
                   ┌─────────────────────────────┼─────────────────────────────┐
                   ▼                             ▼                             ▼
             [ fulfilled ]                  [ partial ]                 [ unverified ]
                   │                             │                             │
                   ▼                             ▼                             ▼
            (All criteria met)           (Missing elements)           (Insufficient evidence)
                                                 │
                                                 ▼
                                        [ contradictory ]
                                                 │
                                      (Conflicting statements)
                                                 │
                                                 ▼
                                        [ unfulfilled ]
                                (Affirmative proof of non-delivery)
```

> **Principle:** Absence of evidence NEVER defaults to failure. If no evidence is provided, status is **`unverified`**.

---

## Endpoints

### 1. Analyze Communication

- **URL:** `POST /api/analyze`
- **Description:** Ingests raw conversation text, extracts commitments with who/what/when, and generates expected evidence requirements.

#### Request Body:
```json
{
  "text": "Rahul: I'll send the quotation tonight.\nRahul: I'll also update the pricing sheet tomorrow.\nMayur: Okay.",
  "source": "conversation",
  "user_id": null
}
```

#### Response: `201 Created`
```json
{
  "analysis_id": "8f3b6c20-6d45-4bb6-a9ce-541249b6d610",
  "total_commitments": 2,
  "commitments": [
    {
      "id": "11111111-1111-1111-1111-111111111111",
      "user_id": null,
      "person": "Rahul",
      "action": "Send",
      "object": "quotation",
      "description": "Send the quotation",
      "deadline": "2026-10-04T23:59:59",
      "deadline_raw": "tonight",
      "source": "conversation",
      "source_excerpt": "Rahul: I'll send the quotation tonight.",
      "expected_evidence": [
        "quotation document",
        "sent message/email",
        "timestamp"
      ],
      "status": "pending",
      "confidence": 0.94,
      "created_at": "2026-10-04T12:00:00Z",
      "updated_at": "2026-10-04T12:00:00Z"
    },
    {
      "id": "22222222-2222-2222-2222-222222222222",
      "user_id": null,
      "person": "Rahul",
      "action": "Update",
      "object": "pricing sheet",
      "description": "Update the pricing sheet",
      "deadline": "2026-10-05T23:59:59",
      "deadline_raw": "tomorrow",
      "source": "conversation",
      "source_excerpt": "Rahul: I'll also update the pricing sheet tomorrow.",
      "expected_evidence": [
        "updated pricing sheet / CSV",
        "delivery cost updates",
        "version change log"
      ],
      "status": "pending",
      "confidence": 0.92,
      "created_at": "2026-10-04T12:00:00Z",
      "updated_at": "2026-10-04T12:00:00Z"
    }
  ]
}
```

---

### 2. List Commitments

- **URL:** `GET /api/commitments`
- **Query Parameters:**
  - `status` (optional, string): Filter by `pending`, `fulfilled`, `partial`, `unfulfilled`, `unverified`, `contradictory`.
  - `person` (optional, string): Substring search on committer's name (e.g. `Rahul`).
  - `limit` (default: 100): Pagination limit.
  - `offset` (default: 0): Pagination offset.

#### Response: `200 OK`
```json
[
  {
    "id": "11111111-1111-1111-1111-111111111111",
    "user_id": null,
    "person": "Rahul",
    "action": "Send",
    "object": "quotation",
    "description": "Send the quotation",
    "deadline": "2026-10-04T23:59:59",
    "deadline_raw": "tonight",
    "source": "conversation",
    "source_excerpt": "Rahul: I'll send the quotation tonight.",
    "expected_evidence": ["quotation document", "sent message/email", "timestamp"],
    "status": "fulfilled",
    "confidence": 0.94,
    "created_at": "2026-10-04T12:00:00Z",
    "updated_at": "2026-10-04T12:00:00Z"
  }
]
```

---

### 3. Get Full Commitment Details

- **URL:** `GET /api/commitments/{id}`
- **Description:** Comprehensive view with linked evidence files, latest verification, and follow-up draft.

#### Response: `200 OK`
```json
{
  "id": "11111111-1111-1111-1111-111111111111",
  "person": "Rahul",
  "action": "Send",
  "object": "quotation",
  "description": "Send the quotation",
  "deadline": "2026-10-04T23:59:59",
  "deadline_raw": "tonight",
  "source": "conversation",
  "source_excerpt": "Rahul: I'll send the quotation tonight.",
  "expected_evidence": [
    "quotation document",
    "sent message/email",
    "timestamp"
  ],
  "status": "fulfilled",
  "confidence": 0.94,
  "created_at": "2026-10-04T12:00:00Z",
  "updated_at": "2026-10-04T12:00:00Z",
  "evidence": [
    {
      "id": "33333333-3333-3333-3333-333333333331",
      "file_name": "quotation.txt",
      "evidence_type": "document",
      "mime_type": "text/plain",
      "file_size": 650,
      "content_hash": "e3b0c442...",
      "relevance_score": 0.96,
      "created_at": "2026-10-04T12:05:00Z"
    }
  ],
  "verification": {
    "id": "44444444-4444-4444-4444-444444444441",
    "status": "fulfilled",
    "explanation": "Retrieved evidence quotation.txt confirms Quotation Ref #Q-2026-901 was dispatched before the deadline.",
    "evidence_summary": "Quotation document verified with dispatch timestamp.",
    "missing_items": [],
    "contradictions": [],
    "confidence": 0.95,
    "verified_at": "2026-10-04T12:10:00Z"
  },
  "followup": null
}
```

---

### 4. Update Commitment (Human Edit)

- **URL:** `PATCH /api/commitments/{id}`
- **Description:** Allows manual editing of any commitment attribute.

#### Request Body:
```json
{
  "person": "Rahul Sharma",
  "object": "revised quotation",
  "deadline_raw": "tomorrow 5pm"
}
```

#### Response: `200 OK`
Returns updated `CommitmentResponse`.

---

### 5. Review / Correct Commitment Status

- **URL:** `POST /api/commitments/{id}/review`
- **Description:** Human user reviews and marks or overrides the status.

#### Request Body:
```json
{
  "status": "fulfilled",
  "notes": "Verified offline directly with Rahul via call."
}
```

#### Response: `200 OK`
Returns updated `CommitmentResponse`.

---

### 6. Upload Evidence File

- **URL:** `POST /api/evidence/upload`
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `file`: Binary file (TXT, PDF, DOCX, CSV, XLSX)
  - `commitment_id` (optional, string): UUID of commitment to link

#### Example cURL:
```bash
curl -X POST http://localhost:8000/api/evidence/upload \
  -F "file=@quotation.txt" \
  -F "commitment_id=11111111-1111-1111-1111-111111111111"
```

#### Response: `201 Created`
```json
{
  "id": "33333333-3333-3333-3333-333333333331",
  "commitment_id": "11111111-1111-1111-1111-111111111111",
  "file_name": "quotation.txt",
  "mime_type": "text/plain",
  "file_size": 650,
  "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "chunk_count": 2,
  "is_duplicate": false,
  "created_at": "2026-10-04T12:05:00Z"
}
```

> **Duplicate Handling:** If the exact same file content (same SHA-256 hash) is uploaded again for the same commitment, the endpoint returns the existing record with `"is_duplicate": true` without creating redundant records.

---

### 7. Search Evidence for Commitment

- **URL:** `POST /api/evidence/search`
- **Description:** Returns ranked evidence chunks scored against commitment criteria.

#### Request Body:
```json
{
  "commitment_id": "11111111-1111-1111-1111-111111111111",
  "query": null,
  "top_k": 5
}
```

#### Response: `200 OK`
```json
{
  "commitment_id": "11111111-1111-1111-1111-111111111111",
  "total_found": 1,
  "candidates": [
    {
      "chunk_id": "chunk-uuid-1",
      "evidence_id": "33333333-3333-3333-3333-333333333331",
      "file_name": "quotation.txt",
      "chunk_index": 0,
      "content": "Official Quotation Ref #Q-2026-901 sent to Mayur...",
      "relevance_score": 0.85,
      "match_reasons": [
        "Matched commitment deliverable/object 'quotation'",
        "Matched committer entity 'rahul'",
        "Matched 2/3 planned evidence criteria"
      ]
    }
  ]
}
```

---

### 8. Run Verification

- **URL:** `POST /api/verify/{commitment_id}`
- **Description:** Compares promised criteria with all candidate evidence chunks. Automatically sets the commitment's status.

#### Request Body (Optional):
```json
{
  "notes": "Verify against today's upload batch"
}
```

#### Response: `200 OK`
```json
{
  "id": "44444444-4444-4444-4444-444444444441",
  "commitment_id": "11111111-1111-1111-1111-111111111111",
  "status": "fulfilled",
  "evidence": [
    {
      "file_name": "quotation.txt",
      "excerpt": "Official Quotation Ref #Q-2026-901 sent to Mayur...",
      "relevance_score": 0.85,
      "source_type": "uploaded_file"
    }
  ],
  "explanation": "Retrieved evidence quotation.txt confirms Quotation Ref #Q-2026-901 was dispatched before the deadline with pricing and delivery terms.",
  "evidence_summary": "Quotation document verified with dispatch timestamp.",
  "missing_items": [],
  "contradictions": [],
  "confidence": 0.95,
  "verified_at": "2026-10-04T12:10:00Z"
}
```

---

### 9. Review / Override Verification

- **URL:** `POST /api/verify/{commitment_id}/review`
- **Description:** Human user approves or overrides the verification status.

#### Request Body:
```json
{
  "status": "partial",
  "notes": "Override: Document sent, but requires sign-off from finance."
}
```

#### Response: `200 OK`
Returns updated `VerificationResponse`.

---

### 10. Generate Follow-up Draft

- **URL:** `POST /api/followup/{commitment_id}`
- **Description:** Generates a polite, non-accusatory message draft based on the latest verification status.

#### Request Body (Optional):
```json
{
  "tone": "polite",
  "custom_instruction": "Mention we need the delivery cost by noon"
}
```

#### Response: `201 Created`
```json
{
  "id": "55555555-5555-5555-5555-555555555552",
  "commitment_id": "22222222-2222-2222-2222-222222222222",
  "draft": "Hi Rahul, thanks for updating the base catalog prices. We noticed delivery costs are still listed as TBD. Could you share the delivery figures when available?",
  "approved": false,
  "approved_at": null,
  "created_at": "2026-10-04T12:15:00Z"
}
```

---

### 11. Human Approves Follow-up Draft

- **URL:** `POST /api/followup/{followup_id}/approve`
- **Description:** Human confirms approval. The frontend can optionally submit an `edited_draft`.

#### Request Body:
```json
{
  "approved": true,
  "edited_draft": "Hi Rahul, thank you for updating the pricing sheet! Could you let us know when the delivery charges will be ready?"
}
```

#### Response: `200 OK`
```json
{
  "id": "55555555-5555-5555-5555-555555555552",
  "commitment_id": "22222222-2222-2222-2222-222222222222",
  "draft": "Hi Rahul, thank you for updating the pricing sheet! Could you let us know when the delivery charges will be ready?",
  "approved": true,
  "approved_at": "2026-10-04T12:20:00Z",
  "created_at": "2026-10-04T12:15:00Z"
}
```

---

### 12. Health & Readiness

- **`GET /api/health`**
  ```json
  { "status": "ok", "app": "PromiseOS Backend", "version": "1.0.0" }
  ```
- **`GET /api/ready`**
  ```json
  {
    "status": "ready",
    "database": "connected",
    "storage": "ready",
    "llm_mode": "mock",
    "active_providers": ["mock"]
  }
  ```
