# API Test Report — Joke REST API

**Agent:** odd
**Date:** 2026-04-06
**Status:** complete — all tests passing

## Upstream outputs read

- projects/auto-dispatch-test/output/2026-04-06-system-architecture.md (bjorn)
- projects/auto-dispatch-test/output/2026-04-06-infrastructure-and-cicd.md (dag)
- projects/auto-dispatch-test/output/2026-04-06-main.py (arve)
- projects/auto-dispatch-test/output/2026-04-06-models.py (arve)
- projects/auto-dispatch-test/output/2026-04-06-jokes-module.py (arve)
- projects/auto-dispatch-test/output/2026-04-06-jokes.json (arve)
- projects/auto-dispatch-test/output/2026-04-06-test_jokes.py (arve)

## Test results

| Suite | Tests | Passed | Failed | File |
|-------|-------|--------|--------|------|
| arve's baseline suite | 16 | 16 | 0 | 2026-04-06-test_jokes.py |
| odd's expanded suite | 50 | 50 | 0 | 2026-04-06-test_api_odd.py |
| **Total** | **66** | **66** | **0** | — |

Run environment: Python 3.14.3, pytest 9.0.2, FastAPI (latest), Pydantic 2.x, macOS darwin arm64.

## Test coverage breakdown

### GET /jokes/random

#### Happy path (13 tests)
- HTTP 200 status code
- Content-Type is application/json
- Response body is a JSON object
- All four required fields present: `id`, `setup`, `punchline`, `category`
- No unexpected extra fields returned
- `id` is a positive integer
- `setup` is a non-empty string
- `punchline` is a non-empty string
- `category` is a non-empty string
- `id` is within the valid dataset range (1–30)
- `category` is one of the six documented values
- `setup` has realistic length (< 300 chars, no leading/trailing whitespace)
- `punchline` has realistic length (>= 5 chars, < 300 chars)

#### Randomness (4 tests)
- 10 calls do not all return the same joke ID (probability of false failure: ~10^-13)
- 20 calls cover at least 2 distinct categories
- 50 calls produce at least 10 distinct joke IDs (distribution check)
- Consecutive pairs eventually differ (loop up to 30 trials)

#### Error / edge cases (8 tests)
- Empty joke list triggers HTTP 500 with `{"detail": "No jokes available."}` (patched via `unittest.mock`)
- POST, PUT, DELETE, PATCH all return 405 Method Not Allowed
- Unknown query parameters are silently ignored — still 200 OK
- Trailing slash `/jokes/random/` does not produce a 5xx error
- Schema is stable across 5 repeated calls (no intermittent serialisation issues)

### GET /health (8 tests)

#### Happy path
- HTTP 200 status code
- Exact body `{"status": "ok"}`
- Content-Type is application/json
- `status` field value is the string `"ok"`
- No extra fields in response

#### Edge case
- Health returns 200 even when joke list is empty (liveness is independent of data)
- 10 repeated calls all return 200 (stability check)

#### Error case
- POST to `/health` returns 405

### Unknown routes (6 tests)
- Completely unknown path returns 404
- Unknown nested path (`/jokes/specific/12345`) returns 404
- Root path `/` returns 404 (not 500)
- 404 response body contains a `detail` field
- `/docs` (Swagger UI) is present and returns 200 — FastAPI default behaviour confirmed
- `/openapi.json` is present, returns 200, and contains `openapi` and `paths` keys

### OpenAPI contract (4 tests)
- `/jokes/random` is listed in the schema paths
- `/health` is listed in the schema paths
- `/jokes/random` has a `get` method documented
- OpenAPI version starts with `3.`

### Performance baseline (3 tests)
- Single call to `/jokes/random` completes in < 200ms (wall-clock, in-process test harness)
- Single call to `/health` completes in < 50ms
- Average of 10 sequential calls to `/jokes/random` is < 100ms each

### Security observations (4 tests)
See security section below for flags.

## Security flags

**SECURITY FLAG — No rate limiting on GET /jokes/random**
Confirmed: 100 rapid sequential calls all return 200. There is no 429 Too Many Requests response at any call volume. An attacker or malfunctioning client can exhaust server resources without restriction.
Recommendation: add `slowapi` (a FastAPI-compatible rate limiter) and apply a limit such as 60 requests/minute per IP on this endpoint.

**SECURITY FLAG — No rate limiting on GET /health**
Confirmed: 50 rapid calls all return 200. Health endpoints are frequently targeted by bots and scanners. While less sensitive than business endpoints, unrestricted access is still a risk.
Recommendation: apply the same rate limiter, or expose health only on an internal/private network path.

**No authentication required (by design for v1)**
The API is intentionally public per bjorn's architecture. This is acceptable for a static joke dataset. If the service ever returns user-specific data, authentication must be added before that deployment. Documented as a known gap to review at v2.

**CORS headers not configured**
FastAPI does not add CORS headers by default. The current state means browser clients from different origins cannot call this API. If a web frontend needs to consume this API, `CORSMiddleware` must be added to `app/main.py`.

## Gaps found in arve's test suite

Arve's 16-test suite is solid for a baseline. The following gaps were identified and covered by this suite:

| Gap | Covered by |
|-----|-----------|
| Empty dataset → 500 error path | `TestRandomJokeErrorCases::test_empty_jokes_list_returns_500` |
| PUT/DELETE/PATCH method rejection | `TestRandomJokeErrorCases::test_{put,delete,patch}_method_not_allowed` |
| Unknown query params ignored | `TestRandomJokeErrorCases::test_query_params_are_ignored_gracefully` |
| Health endpoint independence from data | `TestHealthEndpoint::test_health_is_not_affected_by_joke_store_state` |
| Randomness distribution over 50 calls | `TestRandomJokeRandomness::test_fifty_calls_produce_wide_distribution` |
| OpenAPI schema contract | `TestOpenAPIContract` class (4 tests) |
| Performance baseline | `TestPerformanceBaseline` class (3 tests) |
| Security surface | `TestSecurityObservations` class (4 tests, with inline flags) |
| Realistic data validation (length, whitespace) | `test_setup_is_a_question_or_statement`, `test_punchline_realistic_length` |

## How to run

```bash
# From the joke-api project root (after pip install -r requirements.txt)
pytest tests/test_api_odd.py -v

# Run the full suite (arve's + odd's):
pytest tests/ -v
```

## Decisions logged

- [DECISION] No rate limiting exists on either endpoint as of 2026-04-06. Flagged as a security risk. (2026-04-06)
- [DECISION] CORS headers are not configured. Browser clients cannot call the API without CORSMiddleware. (2026-04-06)
- [DECISION] Performance baseline passed: in-process latency < 100ms average over 10 calls. (2026-04-06)
- [DECISION] 66/66 tests pass on Python 3.14.3 using latest fastapi + pydantic 2.x (pinned versions in requirements.txt target 3.11; latest versions used here due to environment constraints). (2026-04-06)
