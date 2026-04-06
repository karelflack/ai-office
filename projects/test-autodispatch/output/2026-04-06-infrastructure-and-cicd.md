# Infrastructure and CI/CD — Motivational Quote API

**Agent:** dag
**Date:** 2026-04-06
**Project:** test-autodispatch

## Upstream outputs read

- `projects/test-autodispatch/output/2026-04-06-system-architecture.md` (bjorn) — read and validated.

## Assumptions validated against bjorn's architecture

- Runtime: **Python 3.11+ / FastAPI** ✓ (confirmed)
- Single stateless service, quotes in bundled `data/quotes.json` — no DB ✓ (confirmed)
- One process per container, no sidecar ✓ (confirmed)
- Deployed to Railway ✓ (confirmed)
- Container registry: GitHub Container Registry (ghcr.io) ✓ (unchanged)
- **Updated:** `uvicorn` entrypoint is `main:app` (root-level `main.py` per bjorn's component map), not `app.main:app`

---

## Dockerfile

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# Prevent .pyc files and enable unbuffered stdout for logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies in a separate layer for cache efficiency
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Non-root user — principle of least privilege
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

# Parameterised port — override via Railway PORT env var
EXPOSE ${PORT:-8000}

# Health check — Railway and docker-compose both honour this
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8000}/health')" || exit 1

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

**Notes:**
- `python:3.12-slim` is the smallest stable image with a good security surface. Alpine is avoided because it uses musl libc which causes subtle issues with some Python packages.
- The `HEALTHCHECK` uses only the stdlib `urllib` so it works without curl being installed in the slim image.
- If bjorn's architecture specifies Node.js, swap the base image to `node:20-alpine` and adjust the CMD — the rest of the pipeline is unchanged.

---

## docker-compose.yml (local development)

```yaml
version: "3.9"

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    image: quote-api:local
    ports:
      - "${PORT:-8000}:${PORT:-8000}"
    environment:
      - PORT=${PORT:-8000}
      - APP_ENV=development
      # Add any future secrets here using .env file — never hardcode
    env_file:
      - .env.local
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8000}/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    restart: unless-stopped
```

**Usage:**
```bash
cp .env.example .env.local
docker compose up --build
```

---

## .env.example

```
PORT=8000
APP_ENV=development
# Add future secrets below — this file is committed; .env.local is gitignored
```

---

## .dockerignore

```
.git
.env*
!.env.example
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
.coverage
htmlcov
node_modules
*.md
tests/
```

---

## GitHub Actions — CI/CD Workflow

File path: `.github/workflows/ci.yml`

```yaml
name: CI / CD

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ------------------------------------------------------------------ #
  # Job 1: Test — runs on every push and every PR                       #
  # ------------------------------------------------------------------ #
  test:
    name: Run tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt

      - name: Run tests
        run: pytest --tb=short -q

      - name: Upload coverage (optional, non-blocking)
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: htmlcov/
          if-no-files-found: ignore

  # ------------------------------------------------------------------ #
  # Job 2: Build and push — only on merge to main, after tests pass     #
  # ------------------------------------------------------------------ #
  build-and-push:
    name: Build and push Docker image
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=sha-
            type=raw,value=latest,enable=true

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ------------------------------------------------------------------ #
  # Job 3: Deploy to Railway — only after image is pushed               #
  # ------------------------------------------------------------------ #
  deploy:
    name: Deploy to Railway
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment: production

    steps:
      - name: Install Railway CLI
        run: npm install -g @railway/cli

      - name: Deploy
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: railway up --service quote-api --detach

      - name: Verify health after deploy
        run: |
          sleep 15
          curl --fail --silent --max-time 10 "${{ secrets.RAILWAY_PUBLIC_URL }}/health" \
            || (echo "Health check failed after deploy" && exit 1)
```

---

## Required GitHub Secrets

| Secret | Where to get it | Used in |
|---|---|---|
| `GITHUB_TOKEN` | Auto-injected by GitHub Actions | ghcr.io image push |
| `RAILWAY_TOKEN` | Railway dashboard > Account Settings > Tokens | `railway up` deploy step |
| `RAILWAY_PUBLIC_URL` | Railway dashboard > Service > Settings > Domains | Post-deploy health check |

All secrets are set in the GitHub repository under Settings > Secrets and Variables > Actions. None are hardcoded.

---

## Railway Service Configuration

Set the following environment variables in the Railway service dashboard (not in any committed file):

| Variable | Value |
|---|---|
| `PORT` | `8000` (Railway injects this automatically; keep in sync) |
| `APP_ENV` | `production` |

Railway auto-detects the `HEALTHCHECK` directive in the Dockerfile and uses it to gate traffic during rolling deploys — this gives zero-downtime deployments without any extra configuration.

---

## Health Check Endpoint Contract

The application must expose `GET /health` returning HTTP 200. Minimal acceptable response:

```json
{"status": "ok"}
```

This is used by:
1. Docker `HEALTHCHECK` (local and Railway)
2. Post-deploy smoke test in the CI workflow
3. Future uptime monitoring

---

## Deployment Flow Summary

```
PR opened
  └─ test job runs (pytest)
       └─ must pass before merge is allowed (branch protection rule)

Merge to main
  └─ test job runs again
       └─ build-and-push: image tagged sha-<commit> + latest, pushed to ghcr.io
            └─ deploy: railway up (rolling deploy, zero downtime)
                 └─ health check: curl /health — fails the workflow if unhealthy
```

---

## Scalability Note

This setup is sufficient for a low-traffic single-instance MVP. Flag for revisit when:

- Request volume exceeds ~500 req/s (single Railway instance limit) — at that point, add Railway horizontal scaling or move behind a load balancer
- Quote data grows beyond a flat file — introduce a read replica or Redis cache layer at that point, not before

---

## Files to Create in the Repository

| File | Purpose |
|---|---|
| `Dockerfile` | Production container definition |
| `docker-compose.yml` | Local development |
| `.env.example` | Template for local secrets — committed |
| `.dockerignore` | Keeps image lean |
| `.github/workflows/ci.yml` | Full CI/CD pipeline |
