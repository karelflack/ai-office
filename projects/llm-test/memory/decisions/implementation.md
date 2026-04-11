## [2026-04-11] dag — Infrastructure & CI/CD

**Decision:** Multi-stage Docker build (builder + slim runtime), GitHub Actions for CI/CD, GHCR for image registry, Railway for deployment (web + worker dynos + Redis add-on). SUPABASE_SERVICE_KEY is scoped only to the worker service, never the web service.

**Reason:** Multi-stage build keeps the production image small and free of build tooling. GHCR is free for public repos and integrates naturally with GitHub Actions using GITHUB_TOKEN — no additional secrets needed. Keeping the service role key off the web service enforces bjorn's RLS constraint at the infrastructure level, not just in code. Real Postgres + Redis in CI tests catches integration failures that mocked infrastructure would hide.

**Impact:**
- Arve: the repo expects `src/` layout, `requirements.txt` at root, and `requirements-dev.txt` for dev/test deps. The worker start command is `python -m arq app.worker.WorkerSettings` — ensure the WorkerSettings class lives at that import path. The `/health` endpoint must exist and return 200 for the Docker health check to pass.
- Anyone deploying: `SUPABASE_SERVICE_KEY` goes in the worker service env vars on Railway only — do NOT add it to the web service.
- CI runs `mypy --strict` — all `src/` code must be fully typed from the start.
---
## [2026-04-11] arve — Backend API Implementation

**Decision:** FastAPI backend scaffold at `projects/llm-test/backend/` with SQLAlchemy models, Alembic migrations (including RLS policies), JWT auth via Supabase (X-Team-Id header for multi-team context), ARQ worker for async OSV.dev scanning, AES-256-GCM API key encryption, write-only audit logs, and a 28-test pytest suite against in-memory SQLite.

**Reason:** All design decisions delegated to bjorn's architecture (ARQ, RLS, JWT) and magnus's compliance checklist (envelope encryption, RBAC server-side, immediate revocation, write-once audit logs). cvss_score stored as Numeric(4,1) not Text — per bjorn's review note enabling numeric severity sorting.

**Impact:**
- odd (API testing): All endpoints are testable against the scaffold. Run `pytest` for regression baseline. Auth requires `Authorization: Bearer <supabase_jwt>` + `X-Team-Id: <uuid>` headers on all routes except /health and /auth/token.
- per (performance): OSV.dev batch size is 100 packages per HTTP call; scan worker has max_jobs=10 concurrent. Redis timeout is 30s per OSV batch.
- Frontend (ingrid): `/scan-jobs/{id}` returns `{status, dependencies_scanned, vulnerabilities_found}` — poll every 3s while status is queued/running.
- Follow-up (before launch): implement account deletion (B1), data export/portability (B2), and full API key management endpoints (C3/C5) — these are magnus LAUNCH BLOCKERs not covered in this task.
---
