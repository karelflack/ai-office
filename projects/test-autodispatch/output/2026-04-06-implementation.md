# Implementation — Random Joke REST API

**Agent:** arve
**Date:** 2026-04-06
**Project:** test-autodispatch

## Upstream outputs read

- `projects/test-autodispatch/output/2026-04-06-system-architecture.md` (bjorn)
- `projects/test-autodispatch/output/2026-04-06-infrastructure-and-cicd.md` (dag)

---

## Summary

Implemented the full joke REST API per bjorn's architecture. All three endpoints are live, input validation and error responses are in place, and 24 tests pass (unit + integration).

---

## File Map

All source code lives under `projects/test-autodispatch/src/`:

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app instance, lifespan hook to load jokes at startup, `/health` endpoint |
| `routers/joke.py` | Route handlers for `GET /joke`, `GET /joke/{id}`, `GET /jokes` |
| `services/joke_service.py` | Load JSON, build O(1) dict index, random selection, ID lookup, category filter |
| `data/jokes.json` | 30 jokes across 4 categories: general, programming, science, food |
| `tests/test_joke.py` | 24 tests — 13 unit, 11 integration |
| `requirements.txt` | fastapi, uvicorn, pydantic |
| `requirements-dev.txt` | + pytest, httpx |

---

## Endpoints

### `GET /joke`
Returns one joke selected at random.

```json
{"id": 7, "setup": "...", "punchline": "...", "category": "programming"}
```

- `200 OK` — random joke
- `500` — if joke source is unavailable (empty module state)

### `GET /joke/{id}`
Returns the joke with the given integer ID (O(1) dict lookup).

- `200 OK` — matching joke
- `404` — `{"detail": "Joke not found."}`
- `422` — FastAPI automatic validation for non-integer `id`

### `GET /jokes`
Returns all jokes. Supports optional `?category=<string>` filter (case-insensitive).

- `200 OK` — array of jokes (may be empty)
- Empty array for unknown category — never 404

### `GET /health`
- `200 OK` — `{"status": "ok"}` (used by Docker HEALTHCHECK and Railway post-deploy check)

---

## Data

30 jokes across 4 categories:
- `general` — 8 jokes
- `programming` — 10 jokes
- `science` — 7 jokes
- `food` — 5 jokes

---

## Test Results

```
24 passed in 0.29s
```

All 24 tests pass. Coverage includes:
- Service unit tests: load, index build, error cases (empty file, missing file), random selection mock, ID lookup, category filter (including case-insensitivity)
- Integration tests via TestClient: all three endpoints, 404/422/500 error responses, category filter, empty list behavior, field shape validation, health endpoint

---

## Notes for Odd (API Tests)

- Test client fixture in `tests/test_joke.py` loads jokes from a tmp fixture — Odd can reuse the pattern or drive a live server
- `GET /jokes?category=<X>` is case-insensitive on the service side
- `GET /joke/{id}` with a non-integer returns 422 (FastAPI path param validation, no custom code needed)
- The `autouse` fixture in tests resets `_jokes` and `_index` between tests to avoid state bleed
