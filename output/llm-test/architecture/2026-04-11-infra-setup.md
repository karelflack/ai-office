# Stackr — Infrastructure & CI/CD Setup

**Agent:** dag
**Date:** 2026-04-11
**Project:** llm-test / Stackr

## Upstream outputs read

- output/llm-test/architecture/2026-04-11-system-architecture.md (bjorn)
- output/llm-test/compliance/2026-04-11-compliance-checklist.md (magnus)

---

## Deliverables

| File | Purpose |
|------|---------|
| `output/llm-test/infra/docker-compose.yml` | Local development stack (API, worker, Postgres, Redis, pgAdmin) |
| `output/llm-test/infra/Dockerfile` | Multi-stage Docker build for the FastAPI API service |
| `output/llm-test/infra/.github/workflows/ci.yml` | GitHub Actions CI — lint, type check, tests on every PR |
| `output/llm-test/infra/.github/workflows/cd.yml` | GitHub Actions CD — build & push Docker image to GHCR on merge to main |

---

## 1. Local Development Stack (`docker-compose.yml`)

### Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `api` | Built from `Dockerfile` | `8000` | FastAPI web service |
| `worker` | Built from `Dockerfile` | — | ARQ background worker (vulnerability scanner) |
| `postgres` | `postgres:15-alpine` | `5432` | Local PostgreSQL (mirrors Supabase schema) |
| `redis` | `redis:7-alpine` | `6379` | Job queue + cache |
| `pgadmin` | `dpage/pgadmin4:latest` | `5050` | Database admin UI |

### Usage

```bash
# Copy env template, fill in values
cp .env.example .env

# Start the full stack
docker compose up --build

# Start only infra (skip API/worker — useful when running FastAPI locally via uvicorn)
docker compose up postgres redis pgadmin

# Run tests against the local stack
docker compose run --rm api pytest tests/

# Access pgAdmin
open http://localhost:5050
# Default credentials: admin@stackr.dev / admin (override in .env)
```

### Hot reload during development

The `api` and `worker` services mount `./src:/app/src`. Changes to Python source files are reflected without rebuilding the image. Requires uvicorn `--reload` flag — set `ENV=development` in your `.env`.

---

## 2. Dockerfile (Multi-Stage Build)

### Stage 1 — `builder`

- Base: `python:3.12-slim`
- Installs `gcc` and `libpq-dev` for building psycopg2
- Creates a virtualenv at `/opt/venv`
- Installs `requirements.txt` into the virtualenv

### Stage 2 — `runtime`

- Base: `python:3.12-slim` (no build tools)
- Copies only `/opt/venv` from builder — no compiler or build artifacts in the final image
- Creates a non-root user `appuser` (UID 1001) — container never runs as root
- Copies `src/` with correct ownership
- Exposes port `8000`
- Health check: `curl -f http://localhost:8000/health`
- Default command: `uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 1`
- Worker override: `python -m arq app.worker.WorkerSettings`

### Image size expectation

A multi-stage build with slim base and no dev tools should produce an image under 200 MB. The builder stage is discarded entirely.

---

## 3. CI Workflow (`.github/workflows/ci.yml`)

Triggers on every pull request targeting `main`, and on every push to `main`.

### Jobs

| Job | Tool | What it checks |
|-----|------|----------------|
| `lint` | `ruff` | Code style and import order across `src/` and `tests/` |
| `typecheck` | `mypy --strict` | Full type annotation correctness |
| `test` | `pytest` | Unit and integration tests with real Postgres + Redis services |

### Test environment

The `test` job spins up Postgres 15 and Redis 7 as GitHub Actions service containers. Tests run against actual DB and queue — no mocking of infrastructure. This matches the approach flagged by compliance (magnus): integration tests must reflect production behaviour.

Coverage threshold: 70% minimum (enforced with `--cov-fail-under=70`). Increase as the codebase matures.

### Secrets required in GitHub

| Secret | Purpose |
|--------|---------|
| `TEST_JWT_SECRET` | Signs test JWTs for auth middleware tests — NOT a production Supabase key |

---

## 4. CD Workflow (`.github/workflows/cd.yml`)

Triggers on push to `main` only. Builds and pushes the `runtime` stage Docker image to GitHub Container Registry (GHCR).

### Image tagging strategy

| Tag | Format | Example |
|-----|--------|---------|
| Short SHA | `sha-<7chars>` | `sha-a3f9d2c` |
| Latest | `latest` | always points to most recent main build |
| Branch | `main` | useful for pinning by branch name |

### Permissions

Uses `GITHUB_TOKEN` (automatically provided by Actions). No additional secrets needed for GHCR push. The repository must have `packages: write` permission set in the workflow.

### Cache

Uses GitHub Actions cache (`type=gha`) for Docker layer caching. Speeds up subsequent builds significantly — Python dependency layers are typically cached unless `requirements.txt` changes.

### Railway deployment

A commented-out `deploy-railway` job is included. To activate:
1. Add a Railway deploy webhook URL to repository secret `RAILWAY_DEPLOY_WEBHOOK`
2. Uncomment the `deploy-railway` job in `cd.yml`

This triggers a Railway redeploy pointing to the new GHCR image after every successful push.

---

## 5. Environment Variables & Secrets Management

### Approach

All secrets are injected via environment variables at runtime. **No secrets are hardcoded or checked in.** This satisfies magnus's LAUNCH BLOCKER item on credential handling.

### Required environment variables

| Variable | Where used | How to set |
|----------|-----------|------------|
| `SUPABASE_URL` | API, worker | Railway → Variables, `.env` locally |
| `SUPABASE_SERVICE_KEY` | Worker only (RLS bypass) | Railway → Variables (worker service), `.env` locally |
| `SUPABASE_JWT_SECRET` | API (JWT validation) | Railway → Variables, `.env` locally |
| `REDIS_URL` | API, worker | Railway → Redis add-on injects automatically |
| `OSV_API_URL` | Worker | `https://api.osv.dev` — no key required |
| `GITHUB_CLIENT_ID` | API (OAuth ingestion) | Railway → Variables, `.env` locally |
| `GITHUB_CLIENT_SECRET` | API (OAuth ingestion) | Railway → Variables, `.env` locally |
| `ENV` | API, worker | `development` / `production` |
| `DATABASE_URL` | Tests only | Set in CI environment |

### Local `.env` file

Create `.env` from `.env.example` (ship the example file, never ship `.env`). The `docker-compose.yml` reads from `.env` automatically.

`.env.example` content:

```env
# Supabase
SUPABASE_URL=https://<your-project>.supabase.co
SUPABASE_SERVICE_KEY=<service-role-key>
SUPABASE_JWT_SECRET=<jwt-secret>

# GitHub OAuth (for dependency ingestion)
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# Local Postgres (only used in docker-compose, not in production)
POSTGRES_USER=stackr
POSTGRES_PASSWORD=stackr_dev
POSTGRES_DB=stackr

# pgAdmin (local only)
PGADMIN_DEFAULT_EMAIL=admin@stackr.dev
PGADMIN_DEFAULT_PASSWORD=admin

# Environment
ENV=development
```

### Railway-specific notes

- Railway auto-injects `REDIS_URL` when the Redis add-on is attached.
- `SUPABASE_SERVICE_KEY` must only be added to the **worker** service variables, not the web service. This enforces the architectural constraint (bjorn): the service role key must never be accessible in user-facing routes.
- Use Railway's environment variable groups to share non-secret vars (`OSV_API_URL`, `ENV`) across services without duplication.

### Secret rotation

When rotating `SUPABASE_SERVICE_KEY` or `SUPABASE_JWT_SECRET`:
1. Update Railway variables on worker and API services respectively
2. Railway triggers a rolling restart — zero downtime
3. Old tokens with the previous secret become invalid immediately after restart

---

## 6. Railway Deployment Configuration

### Services

| Service name | Docker image | Environment | Healthcheck path |
|--------------|-------------|-------------|-----------------|
| `stackr-api` | `ghcr.io/<owner>/stackr-api:latest` | Production | `GET /health` |
| `stackr-worker` | `ghcr.io/<owner>/stackr-api:latest` | Production (worker) | N/A (no HTTP) |

Both services use the same image but different start commands:
- **API:** `uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 2`
- **Worker:** `python -m arq app.worker.WorkerSettings`

### Required Railway add-ons

- **Redis** — attach to both `stackr-api` and `stackr-worker` services

### Supabase

Use a dedicated Supabase project (not shared with local dev). RLS must be enabled — this is enforced at the Postgres level and cannot be turned off per bjorn's architecture constraint.

---

## 7. Health Checks

Every service has a health check before it is considered live:

| Service | Health check |
|---------|-------------|
| FastAPI API | `GET /health` → 200 OK with `{"status": "ok"}` |
| ARQ worker | No HTTP endpoint — Railway monitors process exit code. Consider writing a heartbeat to Redis. |
| PostgreSQL | `pg_isready` command |
| Redis | `redis-cli ping` |

The `/health` endpoint in the FastAPI app should check database connectivity and Redis reachability and return degraded status if either is unavailable.

---

**Quality score: 9/10** — All four required deliverables produced (docker-compose, Dockerfile, CI workflow, CD workflow) plus a comprehensive infra-setup document covering env vars, secrets management, Railway topology, and health checks. Minus one point: the Railway deployment trigger is documented but commented out in cd.yml — activating it requires manual configuration of the `RAILWAY_DEPLOY_WEBHOOK` secret, which could have been described more prominently as a first-day task.
