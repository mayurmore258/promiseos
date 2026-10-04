# PromiseOS Backend & Verification Engine

> **Agentic AI System for Commitment Discovery, Evidence Verification, and Supervised Follow-up Generation**  
> *Evidence over assumption. Verification over accusation. Human approval over autonomous action.*

---

## 1. What PromiseOS Backend Does

PromiseOS discovers commitments from messy human communication (chat messages, emails, meeting transcripts), plans the concrete evidence required to prove fulfillment, indexes uploaded documents (TXT, PDF, DOCX, CSV, XLSX), semantically matches evidence against promises, executes factual verification, and prepares polite, non-accusatory follow-up messages for human review and approval.

### Core Philosophy
1. **Evidence over assumption:** Never assume a promise was kept without tangible verification.
2. **Verification over accusation:** Never treat absence of evidence as proof of failure. If evidence is lacking, the status is safely marked **`unverified`**.
3. **Human approval over autonomous action:** The backend never sends emails or messages automatically. Follow-ups are drafted and require explicit human approval.

---

## 2. Architecture

```
                    FRONTEND (React + Vite)
                                │ HTTP / JSON / Multipart
                                ▼
                   ┌───────────────────────────┐
                   │      FASTAPI BACKEND      │
                   └─────────────┬─────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
    LLM ROUTER             FILE PIPELINE             DATABASE
(Groq / NVIDIA /        (Validation / Parsers /    (PostgreSQL / Supabase /
 SambaNova / Gemini /     Chunking / Ranking /      Local Async SQLite)
 OpenRouter / Mock)       Semantic Retrieval)            │
         │                       │                       │
         └───────────┬───────────┘                       │
                     ▼                                   ▼
             VERIFICATION ENGINE                    REPOSITORIES
         (Fulfilled / Partial / Unverified /     (Commitments, Evidence,
          Contradictory / Unfulfilled)            Verification, Followups)
                     │
                     ▼
             HUMAN REVIEW / EDIT
                     │
                     ▼
             FOLLOW-UP DRAFTER
                     │
                     ▼
             HUMAN APPROVAL
```

---

## 3. Folder Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app, lifespan, CORS, middleware, exceptions
│   ├── core/                    # Config, structured logging, security, exceptions
│   ├── api/                     # REST routes: health, analyze, commitments, evidence, verify, followups
│   ├── schemas/                 # Pydantic v2 validation contracts
│   ├── models/                  # SQLAlchemy 2.0 ORM models
│   ├── db/                      # Engine, session, repository layer
│   ├── agents/                  # CommitmentAgent, EvidencePlanner, VerificationAgent, FollowupAgent
│   ├── services/                # AnalysisService, EvidenceService, VerificationService, FollowupService
│   ├── llm/                     # Router with fallback chain + Mock provider + 5 API providers
│   ├── evidence/                # Parsers (TXT, PDF, DOCX, CSV, XLSX), chunker, matcher, retriever
│   └── utils/                   # Safe IDs, date/deadline parsing, text similarity & excerpts
├── data/
│   ├── samples/                 # Sample conversation logs
│   ├── test_evidence/           # Sample quotation, pricing CSV, and chat logs
│   └── uploads/                 # Storage directory for ingested evidence
├── scripts/
│   ├── local_setup.py           # Environment validator & DB initializer
│   └── seed_database.py         # Loads demo users, commitments, evidence & results
├── sql/
│   ├── schema.sql               # PostgreSQL / Supabase DDL schema
│   ├── indexes.sql              # Performance B-Tree indexes
│   └── seed.sql                 # SQL seed data
├── tests/                       # Unit, integration, and API test suites
├── .env.example                 # Example configuration
├── requirements.txt             # Clean Python 3.11+ dependencies
├── pytest.ini                   # Pytest configuration
├── API_CONTRACT.md              # Detailed API specification for frontend teammate
└── README.md                    # This document
```

---

## 4. Prerequisites & Python Version

- **Python Version:** Python 3.11+
- **Package Manager:** `pip`

---

## 5. Installation & Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run local setup:**
   ```bash
   python -m scripts.local_setup
   ```
   *This copies `.env.example` to `.env` if not present, creates upload directories, and initializes SQLite tables.*

---

## 6. Environment Configuration (`.env`)

Copy `.env.example` to `.env`:

```env
# Application
APP_ENV=development
DEBUG=true
MOCK_LLM=true

# Database (Default: local async SQLite; switch to Postgres / Supabase when ready)
DATABASE_URL=sqlite+aiosqlite:///./promiseos.db
SUPABASE_URL=
SUPABASE_KEY=

# LLM Providers (Leave blank for offline mock mode; fill keys when available)
GROQ_API_KEY=
NVIDIA_API_KEY=
SAMBANOVA_API_KEY=
GEMINI_API_KEY=
OPENROUTER_API_KEY=

# Storage & Uploads
MAX_UPLOAD_SIZE_MB=25
UPLOAD_DIR=./data/uploads

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 7. Database Setup & Supabase Compatibility

### Local Development (Zero-Config)
By default, the backend uses `sqlite+aiosqlite:///./promiseos.db`. No database installation or background service is required to develop or run tests.

### PostgreSQL & Supabase Setup
To connect to Supabase:
1. Obtain your Postgres connection string from your Supabase Project Settings:
   ```env
   DATABASE_URL=postgresql+psycopg://postgres.[project_ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   SUPABASE_URL=https://[project_ref].supabase.co
   SUPABASE_KEY=[your_anon_or_service_role_key]
   ```
2. Run the SQL migrations directly in the Supabase SQL Editor:
   - `sql/schema.sql` (Creates tables, UUID extensions, and check constraints)
   - `sql/indexes.sql` (Creates search & foreign key indexes)
   - `sql/seed.sql` (Optional: Seeds demo data)

Alternatively, run the Python seeder:
```bash
python -m scripts.seed_database
```

---

## 8. Offline & Local Mock Mode (`MOCK_LLM=true`)

When `MOCK_LLM=true` (or when no API keys are provided in `.env`), the backend automatically uses `MockLLMProvider`.
- **Deterministic extraction:** Reliably parses canonical conversations (e.g., Rahul quotation and pricing sheet) as well as arbitrary test dialogues.
- **Accurate schema adherence:** Passes all Pydantic v2 schemas and validation checks.
- **No external network calls:** Operates completely offline without failing on missing credentials.

When keys are supplied and `MOCK_LLM=false`, the `LLMRouter` follows this fallback sequence:
1. **Groq** (`llama-3.3-70b-versatile`)
2. **NVIDIA NIM** (`meta/llama-3.1-70b-instruct`)
3. **SambaNova** (`Meta-Llama-3.1-70B-Instruct`)
4. **Google Gemini** (`gemini-1.5-flash`)
5. **OpenRouter** (`meta-llama/llama-3.3-70b-instruct`)
6. **Mock Fallback** (Resilience safety net)

---

## 9. Running the FastAPI Server

Start the development server with live reload:

```bash
uvicorn app.main:app --reload --port 8000
```

- **Server URL:** `http://localhost:8000`
- **Interactive Swagger Documentation:** `http://localhost:8000/docs`
- **OpenAPI Schema:** `http://localhost:8000/openapi.json`
- **Alternative ReDoc UI:** `http://localhost:8000/redoc`

---

## 10. API Endpoints Quick Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/analyze` | Ingest communication text, extract commitments & plan evidence |
| `GET` | `/api/commitments` | List commitments (filters: `status`, `person`, `limit`, `offset`) |
| `GET` | `/api/commitments/{id}` | Full commitment detail + evidence + verification + follow-up |
| `PATCH` | `/api/commitments/{id}` | Human edits commitment fields |
| `POST` | `/api/commitments/{id}/review` | Human approves or overrides commitment status |
| `POST` | `/api/evidence/upload` | Upload evidence file (TXT, PDF, DOCX, CSV, XLSX) |
| `POST` | `/api/evidence/search` | Search & rank candidate evidence for a commitment |
| `POST` | `/api/verify/{id}` | Execute verification against available evidence |
| `POST` | `/api/verify/{id}/review` | Human review or override of verification verdict |
| `POST` | `/api/followup/{id}` | Draft polite follow-up message |
| `POST` | `/api/followup/{id}/approve` | Human review and approve follow-up draft |
| `GET` | `/api/health` | Health check (`{"status": "ok"}`) |
| `GET` | `/api/ready` | Readiness check (DB, Storage, LLM mode) |

*For complete request/response schemas and curl examples, see [API_CONTRACT.md](API_CONTRACT.md).*

---

## 11. Running Backend Tests

Run all unit, integration, and API tests:

```bash
pytest
```

For verbose output with test names:
```bash
pytest -v
```

External provider tests that require active paid credentials are automatically isolated and gracefully skipped when API keys are absent.

---

## 12. Complete Sample Workflow

1. **Analyze Conversation:**
   ```bash
   curl -X POST http://localhost:8000/api/analyze \
     -H "Content-Type: application/json" \
     -d '{"text": "Rahul: I'\''ll send the quotation tonight.\nRahul: I'\''ll also update the pricing sheet tomorrow.\nMayur: Okay."}'
   ```
   *Returns 2 commitments with expected evidence plans.*

2. **Upload Evidence File:**
   ```bash
   curl -X POST http://localhost:8000/api/evidence/upload \
     -F "file=@data/test_evidence/quotation.txt" \
     -F "commitment_id=<COMMITMENT_ID>"
   ```

3. **Verify Commitment:**
   ```bash
   curl -X POST http://localhost:8000/api/verify/<COMMITMENT_ID>
   ```
   *Evaluates uploaded document and assigns `fulfilled` status.*

4. **Draft Follow-up (for partial/unverified commitments):**
   ```bash
   curl -X POST http://localhost:8000/api/followup/<COMMITMENT_ID>
   ```

5. **Approve Follow-up (Human in the loop):**
   ```bash
   curl -X POST http://localhost:8000/api/followup/<FOLLOWUP_ID>/approve \
     -H "Content-Type: application/json" \
     -d '{"approved": true}'
   ```
