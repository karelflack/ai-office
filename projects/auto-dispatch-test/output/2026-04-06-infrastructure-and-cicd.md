# Infrastructure and CI/CD — Auto Dispatch Test

**Agent:** dag
**Date:** 2026-04-06
**Status:** complete

## Upstream outputs read

- projects/auto-dispatch-test/tasks/active/2026-04-06-system-architecture.md (bjorn) — task still active, no output file yet. Defaulting to Python/FastAPI as instructed.

## Decisions

- Stack: Python 3.12 / FastAPI — default per task instructions (bjorn's architecture not yet available)
- No database: jokes are stored as an in-memory list in the application (fits the simple scope)
- Docker base image: `python:3.12-slim` — minimal footprint, official image
- Health check endpoint: `GET /health` returns `{"status": "ok"}`
- CI pipeline: GitHub Actions — lint (ruff), tests (pytest), Docker build on every push to main and on PRs
- No push to registry in CI for now — image is built and verified, push can be added when a registry is chosen
- Secrets: no secrets required for this service; if added later they must go in GitHub Actions secrets and Railway env vars, never in code

## Scale note

An in-memory joke list is fine for a demo service. If the joke dataset grows or needs to be updated without a redeploy, move it to a database (Supabase/Postgres on Railway is the natural next step given the product stack).

## Deliverables

| File | Description |
|------|-------------|
| `2026-04-06-Dockerfile` | Multi-stage Docker image for the FastAPI service |
| `2026-04-06-docker-compose.yml` | Local dev compose file |
| `2026-04-06-ci.yml` | GitHub Actions CI pipeline |

## Directory layout assumed

```
projects/auto-dispatch-test/
  app/
    main.py          # FastAPI app entrypoint
    jokes.py         # Joke data and logic
    tests/
      test_api.py    # pytest tests (written by arve/odd)
  Dockerfile
  docker-compose.yml
  requirements.txt
  .github/
    workflows/
      ci.yml
```
