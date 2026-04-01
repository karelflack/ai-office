# Ops README — Auth Infrastructure and Secrets Management

This document supplements the existing ops README with instructions specific to the
authentication system: environment variable setup, JWT secret rotation, Alembic
migrations, and rate limiting.

---

## New Environment Variables

Add these to Railway's service environment panel and to your local `.env` file.
Never set them directly in docker-compose.yml or commit them to the repo.

| Variable | Required | Default | Description |
|---|---|---|---|
| `JWT_SECRET_KEY` | Yes | none | Signs all JWTs. Must be a cryptographically random string. |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm. Do not change unless you add RS256 key support. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `1440` | How long access tokens stay valid (24 hours). |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `30` | How long refresh tokens stay valid. |
| `RATE_LIMIT_AUTH_LOGIN` | No | `10/minute` | slowapi limit string for POST /login per IP. |
| `RATE_LIMIT_AUTH_REGISTER` | No | `5/minute` | slowapi limit string for POST /register per IP. |

### Generating a secure JWT_SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

This produces 64 hex characters (256 bits). Copy the output directly into Railway's
environment variable panel. Do not wrap it in quotes.

---

## Alembic Migrations

Alembic manages all schema changes. Migrations run automatically in CI and on Railway
deploys. You should never need to run `Base.metadata.create_all()` in production —
that call is fine for the SQLite dev setup but Alembic owns the schema otherwise.

### First-time setup (local)

```bash
# Install Alembic if not already in requirements-dev.txt
pip install alembic

# Initialise Alembic (only once, already done if alembic/ dir exists)
alembic init alembic

# Generate the initial migration from your SQLAlchemy models
alembic revision --autogenerate -m "initial schema with users and links"

# Apply it
alembic upgrade head
```

### Generating a migration after a model change

```bash
alembic revision --autogenerate -m "add refresh_tokens table"
alembic upgrade head
```

Always review the generated file in `alembic/versions/` before committing.
Autogenerate can miss some things (e.g. CHECK constraints, partial indexes).

### Rolling back

```bash
alembic downgrade -1    # one step back
alembic downgrade base  # all the way back to zero (destructive)
```

### CI behaviour

The GitHub Actions CI workflow runs `alembic upgrade head` against a fresh Postgres
service container before running tests. This validates that:
- All migration files parse correctly
- They apply cleanly in order on a blank database
- The ORM models match the migrated schema (tests will fail if they don't)

### Railway deploy behaviour

The GitHub Actions deploy job runs `railway run alembic upgrade head` after the new
image is live. Railway's `run` command executes in the same environment as the service
(same env vars, same network), so `DATABASE_URL` resolves to the production database.

Migration runs before traffic shifts to the new image — zero-downtime deploys require
that migrations are backward-compatible (additive-only: new tables, new nullable columns).
Destructive schema changes (dropping columns, renaming tables) require a two-deploy
strategy: deploy code that works with both old and new schema, migrate, then clean up.

---

## JWT Secret Key Rotation (Production)

Rotating the JWT secret invalidates all existing tokens immediately. Every logged-in
user will be signed out and must log in again. Warn users before rotating if possible.

### Steps

1. Generate a new secret:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. In the Railway dashboard, navigate to your service > Variables.
   Update `JWT_SECRET_KEY` to the new value.

3. Railway will detect the variable change and trigger a redeploy automatically.
   The new secret takes effect when the new container is live.

4. All tokens signed with the old key will fail validation immediately.
   Users will receive a 401 and be redirected to the login page.

5. If you need a grace period (allow old tokens to stay valid for N minutes while
   new tokens are issued with the new key), you must implement a "previous key"
   fallback in `app/auth.py` — try decoding with the new key first, fall back to the
   old key if that fails, and remove the fallback after the old tokens expire.
   This is optional complexity; for most small-team deployments, immediate rotation is
   simpler and lower risk.

### When to rotate

- Any time a team member with production access leaves
- Any time the key is logged, printed, or committed (even briefly)
- On a scheduled basis (quarterly is a reasonable default for low-sensitivity apps)
- Immediately if you suspect a compromise

### Audit trail

Railway logs the timestamp of every variable change. If you need a separate audit log,
note the rotation date and reason in a team runbook or Notion page.

---

## Rate Limiting

Auth endpoints are rate-limited via slowapi backed by Redis. The limits are configurable
via environment variables and default to values appropriate for a production SaaS:

| Endpoint | Default limit | Rationale |
|---|---|---|
| `POST /register` | 5/minute per IP | Prevents account creation spam |
| `POST /login` | 10/minute per IP | Allows reasonable retry but blocks brute force |

### How it works

slowapi reads the client IP from the `X-Forwarded-For` header (set by Railway's proxy)
and increments a counter in Redis for each request. When the counter exceeds the limit,
the request is rejected with `HTTP 429` and a `Retry-After: 60` header.

Because the counter lives in Redis (not in-process memory), the limit is correctly
enforced across all workers and replicas.

### Adjusting limits

Update `RATE_LIMIT_AUTH_LOGIN` and `RATE_LIMIT_AUTH_REGISTER` in Railway's environment
variable panel. No code change or redeploy is needed for values that are only read from
env — confirm this matches how your `app/rate_limiting.py` reads the variable.

slowapi limit format: `"<count>/<period>"` where period is `second`, `minute`, `hour`, or `day`.
Examples: `"10/minute"`, `"100/hour"`, `"3/second"`.

### Monitoring

Rate limit events are logged at WARNING level by slowapi. If you see a spike in 429s,
check Railway logs:

```bash
railway logs --service url-shortener | grep "Rate limit exceeded"
```

---

## Health Check

The Dockerfile health check hits `GET /health` every 30 seconds. This endpoint must
return `200` for Railway to route traffic to the container. Add it to `app/main.py` if
not already present:

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

Railway uses this endpoint for zero-downtime deploys: the old container continues
serving traffic until the new one passes its first health check.

---

## Bottleneck Warning

The current auth implementation uses synchronous bcrypt hashing in the request thread
(`passlib[bcrypt]`). bcrypt is intentionally slow (cost factor 12 by default). Under
sustained high concurrency on `/register` or `/login`, this will block uvicorn workers.

At small scale (< 100 concurrent auth requests) this is not a problem. If you expect
bursty auth traffic at scale, options in priority order:

1. Increase workers (already set to 2 in the Dockerfile)
2. Add Railway replicas (horizontal scale, no code change)
3. Move hashing to a background task with `starlette.concurrency.run_in_threadpool`
4. Switch to argon2 with async support via `argon2-cffi`

Flag this before you exceed 500 concurrent users.
