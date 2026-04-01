# Ops README — URL Shortener

Quick reference for running, deploying, and debugging the URL shortener API.

## Local Development

### Prerequisites
- Docker Desktop (or Docker + Compose plugin)
- Python 3.12+ (only needed if running outside Docker)

### Start everything with Docker Compose

```bash
cp .env.example .env          # fill in POSTGRES_PASSWORD and SECRET_KEY
docker compose up --build
```

The API is available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

To stop and remove containers (keeps the Postgres volume):

```bash
docker compose down
```

To also wipe the database volume:

```bash
docker compose down -v
```

### Running without Docker (for fast iteration)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env          # point DATABASE_URL / REDIS_URL at local services
uvicorn app.main:app --reload
```

### Running tests

```bash
pytest                        # all tests
pytest -k test_shorten        # single test
pytest --tb=short -q          # quiet output
```

### Linting and formatting

```bash
ruff check .                  # lint
ruff format .                 # auto-format
mypy app/                     # type check
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `SECRET_KEY` | Yes | App secret (session signing, etc.) |
| `BASE_URL` | Yes | Public base URL used in shortened links |
| `LOG_LEVEL` | No | `debug`/`info`/`warning`/`error` (default: `info`) |
| `POSTGRES_USER` | Compose only | DB username for the `db` service |
| `POSTGRES_PASSWORD` | Compose only | DB password for the `db` service |
| `POSTGRES_DB` | Compose only | DB name for the `db` service |

Secrets (`SECRET_KEY`, `POSTGRES_PASSWORD`) must **never** be committed. Use `.env` locally; use Railway/Vercel environment variable panels in production.

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push:

### On all branches
1. Spins up Postgres 16 + Redis 7 as service containers
2. Installs Python dependencies
3. Runs `ruff` lint + format check
4. Runs `mypy` type check
5. Runs the full test suite with `pytest`

### On merge to `main` only
6. Builds the Docker image
7. Pushes to GitHub Container Registry (`ghcr.io/<owner>/<repo>:latest` and `sha-<commit>`)

The build step is gated behind a successful test run — it will not trigger if tests fail.

---

## Docker Image

| Detail | Value |
|---|---|
| Base image | `python:3.12-slim` (multi-stage) |
| Exposed port | `8000` |
| Health check | `GET /health` every 30s |
| Run as | Non-root user `appuser` (uid 1000) |
| Registry | `ghcr.io/<owner>/<repo>` |

Pull the latest image:

```bash
docker pull ghcr.io/<owner>/<repo>:latest
```

Run standalone (you must supply all env vars):

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=... \
  -e REDIS_URL=... \
  -e SECRET_KEY=... \
  -e BASE_URL=... \
  ghcr.io/<owner>/<repo>:latest
```

---

## Deployment (Railway)

1. Create a new Railway project and link the GitHub repo.
2. Add a **PostgreSQL** plugin and a **Redis** plugin from the Railway dashboard.
3. Railway auto-populates `DATABASE_URL` and `REDIS_URL` from the plugins.
4. Set `SECRET_KEY` and `BASE_URL` as environment variables in the Railway service settings.
5. Railway will build the Dockerfile and deploy on every push to `main`.

Health check path: `/health` (Railway uses this for zero-downtime deploys; configure it in the service settings).

---

## Scaling Notes

- Redis acts as a read-through cache for redirect lookups — the `GET /{code}` hot path never hits Postgres for cached codes.
- The API is stateless; horizontal scaling (multiple Railway replicas or instances) works without any changes.
- Postgres is the single write bottleneck at scale. If write throughput becomes an issue, consider partitioning the `urls` table by `created_at` before adding read replicas.
- The current Redis config (`maxmemory 128mb`, `allkeys-lru`) is appropriate for a small deployment. Increase `maxmemory` as the URL table grows.
