# Auth System — URL Shortener

**Agent:** arve
**Date:** 2026-04-01
**Status:** Complete — all 20 tests passing

## What was added

### New files
- `app/auth.py` — password hashing (passlib/bcrypt), JWT creation/verification (python-jose/HS256), `get_current_user` and `get_optional_user` FastAPI dependencies.

### Modified files
- `app/models.py` — added `User` model (`id`, `email`, `hashed_password`, `created_at`); added optional `owner_id` FK and `owner` relationship to `Link`.
- `app/schemas.py` — added `UserCreate`, `UserResponse`, `Token`, `TokenData`, `LinkResponse`; updated `ShortenResponse` with optional `owner_id`.
- `app/crud.py` — added `create_user`, `get_user_by_email`, `get_links_by_owner`; updated `create_link` to accept `owner_id`.
- `app/main.py` — added `POST /register`, `POST /login`, `GET /me/links`; updated `POST /shorten` to accept optional auth; updated `DELETE /{code}` to require auth and enforce ownership.
- `requirements.txt` — added `passlib[bcrypt]`, `python-jose[cryptography]`, `python-multipart`, `email-validator`, pinned `bcrypt==4.2.1`.

### Updated tests
- `tests/test_api.py` — added 12 new tests covering registration, login, authenticated shorten, `/me/links`, owner delete, cross-user 403, and unauthenticated 401. Updated the original `test_delete` tests to supply a Bearer token (DELETE now requires auth).

## Key design decisions

**Optional auth on POST /shorten.** Anonymous link creation is preserved — the endpoint reads the Bearer token if present but does not require it. This means existing integrations without auth continue to work.

**DELETE requires auth.** The original endpoint required no auth. This was changed: any authenticated user can delete an anonymous link; only the link's owner can delete an owned link. Unauthenticated DELETE returns 401.

**JWT subject is the user's email.** The `sub` claim stores the email, which is also unique in the DB. This keeps token verification simple — one DB query on each protected request.

**bcrypt pinned to 4.2.1.** bcrypt 5.0.0 removed the `__about__` module that passlib uses to detect the library version. When passlib cannot detect the version it falls back to a 72-byte wrap-bug detection test, which bcrypt 5 now rejects with a `ValueError`. Pinning to 4.2.1 avoids this until passlib ships a compatible update. This decision is noted in `requirements.txt`.

**`get_optional_user` dependency.** Rather than duplicating token-parsing logic in the shorten endpoint, a dedicated dependency returns `None` instead of raising 401 when no token is present. This keeps the main endpoint handler clean.

## Endpoint summary

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| POST | /register | None | Creates user, returns JWT |
| POST | /login | None | OAuth2 password form, returns JWT |
| POST | /shorten | Optional | Sets owner_id if authenticated |
| GET | /me/links | Required | Returns caller's links |
| GET | /{code}/stats | None | Public |
| GET | /{code} | None | Public redirect |
| DELETE | /{code} | Required | Owner or any authed user for anon links |
