# Infrastructure and CI/CD — Auto Dispatch Test

**Agent:** dag
**Date:** 2026-04-06
**Status:** complete

## Upstream outputs read

- projects/auto-dispatch-test/output/2026-04-06-system-architecture.md (bjorn)

## Decisions

- Stack: Python 3.11 / FastAPI — confirmed from bjorn's architecture
- No database: jokes loaded from `data/jokes.json` at startup; in-process list
- Docker base image: `python:3.11-slim` — minimal footprint, matches Python version from bjorn
- Health check endpoint: `GET /health` returns `{"status": "ok"}` — defined by bjorn, wired into Docker HEALTHCHECK and compose
- CI pipeline: GitHub Actions — lint (ruff), tests (pytest tests/), Docker build on every push and PR
- No push to registry in CI for now — image is built and verified; push step can be added when a container registry is chosen (Railway can pull from GitHub Container Registry or build from source directly)
- Secrets: none required for this service at v1. If added later: GitHub Actions secrets for CI, Railway environment variables for runtime — never hardcoded

## Scale note

Static in-process joke list is fine for a demo. If the joke dataset needs to be updated without a redeploy, the natural migration path is Supabase/Postgres on Railway (already in the team's stack). This would require a data migration and new endpoint logic — bjorn has flagged this as the known hard-to-reverse decision.

## Directory layout (per bjorn's architecture)

```
joke-api/
  app/
    main.py           # FastAPI app, route definitions
    models.py         # Pydantic response model for Joke
    jokes.py          # Joke loading and random selection logic
  data/
    jokes.json        # Static joke dataset
  tests/
    test_jokes.py     # pytest tests
  Dockerfile          # from 2026-04-06-Dockerfile
  docker-compose.yml  # from 2026-04-06-docker-compose.yml
  requirements.txt
  .github/
    workflows/
      ci.yml          # from 2026-04-06-ci.yml
```

## Deliverables

| File | Description |
|------|-------------|
| `2026-04-06-Dockerfile` | Docker image — python:3.11-slim, HEALTHCHECK wired to /health |
| `2026-04-06-docker-compose.yml` | Local dev compose with health check and restart policy |
| `2026-04-06-ci.yml` | GitHub Actions: lint → test → docker build (no push yet) |

## Notes for arve (implementation)

- `requirements.txt` must include: `fastapi`, `uvicorn[standard]`, `httpx`, `pytest`, `ruff`
- Tests must live in `tests/` (not `app/tests/`) — that is what the CI pipeline invokes
- The Dockerfile copies `app/` and `data/` — arve must not move these directories

## Notes for odd (API testing)

- Service runs on port 8000 locally (`docker-compose up`)
- Health check: `GET /health` — expect `{"status": "ok"}`
- Primary endpoint: `GET /jokes/random` — see bjorn's response schema
