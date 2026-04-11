## [2026-04-11] dag — Infrastructure & CI/CD

**Decision:** Multi-stage Docker build (builder + slim runtime), GitHub Actions for CI/CD, GHCR for image registry, Railway for deployment (web + worker dynos + Redis add-on). SUPABASE_SERVICE_KEY is scoped only to the worker service, never the web service.

**Reason:** Multi-stage build keeps the production image small and free of build tooling. GHCR is free for public repos and integrates naturally with GitHub Actions using GITHUB_TOKEN — no additional secrets needed. Keeping the service role key off the web service enforces bjorn's RLS constraint at the infrastructure level, not just in code. Real Postgres + Redis in CI tests catches integration failures that mocked infrastructure would hide.

**Impact:**
- Arve: the repo expects `src/` layout, `requirements.txt` at root, and `requirements-dev.txt` for dev/test deps. The worker start command is `python -m arq app.worker.WorkerSettings` — ensure the WorkerSettings class lives at that import path. The `/health` endpoint must exist and return 200 for the Docker health check to pass.
- Anyone deploying: `SUPABASE_SERVICE_KEY` goes in the worker service env vars on Railway only — do NOT add it to the web service.
- CI runs `mypy --strict` — all `src/` code must be fully typed from the start.
---
