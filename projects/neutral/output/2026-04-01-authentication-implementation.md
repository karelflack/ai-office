# Authentication Implementation — Completion Pass

**Agent:** arve
**Date:** 2026-04-01
**Status:** Complete — 32 tests passing (20 existing + 12 new)

## What this session added

This session picks up from a previous arve pass that wired the basic auth skeleton.
Three gaps were addressed:

### 1. Fixed passlib/bcrypt 5.x incompatibility (root cause of all test failures)

**Bug:** bcrypt 5.0.0 removed the `__about__` module that passlib uses for version
detection. When passlib cannot detect the version it runs a 72-byte wrap-bug detection
probe, which bcrypt 5 now rejects with `ValueError: password cannot be longer than 72 bytes`.
This caused every test that called `register_user()` to crash with a 500.

**Fix:** Removed passlib from `auth.py` entirely. Password hashing now calls the bcrypt
library directly:

```python
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

`requirements.txt` was updated to drop `passlib[bcrypt]` and replace it with `bcrypt>=4.0.0`
(the direct API is stable across 4.x and 5.x).

### 2. Added refresh token support

The task spec requires a 15-minute access token and 7-day refresh token.
Added to `auth.py`:
- `create_refresh_token(data)` — signs with `type: "refresh"` claim, 7-day expiry
- `decode_refresh_token(token)` — validates type claim and returns email; raises 401 on failure
- `get_current_user` updated to reject refresh tokens (checks `type` claim)
- `get_optional_user` updated with the same guard

`schemas.py` updated:
- `Token` now includes `refresh_token: str`
- New `RefreshRequest` schema for the refresh endpoint body

### 3. Added `/auth/` router with all four required endpoints

`main.py` now mounts an `APIRouter(prefix="/auth")` exposing:

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/register | None | Register; returns access + refresh token |
| POST | /auth/login | None | Login via OAuth2 password form; returns both tokens |
| POST | /auth/refresh | None (uses refresh token in body) | Exchange refresh token for new token pair |
| GET | /auth/me | Required (access token) | Returns current user profile |

The legacy `/register` and `/login` flat routes are preserved for backward compatibility
and also return `refresh_token` now.

## Full endpoint list

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| POST | /auth/register | None | Creates user, returns access+refresh JWT |
| POST | /auth/login | None | OAuth2 password form, returns access+refresh JWT |
| POST | /auth/refresh | Refresh token in body | Issues new token pair |
| GET | /auth/me | Bearer access token | Returns id, email, created_at |
| POST | /register | None | Legacy alias for /auth/register |
| POST | /login | None | Legacy alias for /auth/login |
| POST | /shorten | Optional | Sets owner_id if authenticated |
| GET | /me/links | Required | Returns caller's links |
| GET | /{code}/stats | None | Public |
| GET | /{code} | None | Public redirect |
| DELETE | /{code} | Required | Owner or any authed user for anon links |

## Test coverage

12 new tests added to `tests/test_api.py`:

- `test_auth_register_returns_both_tokens` — response includes access_token + refresh_token
- `test_auth_register_duplicate_returns_409`
- `test_auth_login_valid_credentials`
- `test_auth_login_wrong_password_is_401`
- `test_auth_login_unknown_user_is_401`
- `test_auth_me_returns_user_profile` — verifies id, email, created_at
- `test_auth_me_requires_auth`
- `test_auth_refresh_issues_new_tokens` — new access token works on /auth/me
- `test_auth_refresh_with_invalid_token_is_401`
- `test_auth_refresh_token_rejected_as_access_token` — refresh token cannot authenticate protected routes
- `test_token_response_includes_refresh_token_on_legacy_register`
- `test_token_response_includes_refresh_token_on_legacy_login`

## Files changed

All changes are in `projects/test-handoffs/output/2026-04-01-url-shortener-api/`:

- `app/auth.py` — replaced passlib with direct bcrypt; added refresh token functions; hardened type-checking in get_current_user/get_optional_user
- `app/schemas.py` — Token gains refresh_token field; added RefreshRequest
- `app/main.py` — added auth_router with /auth/* endpoints; updated register/login to return both tokens
- `requirements.txt` — removed passlib; added bcrypt>=4.0.0 with explanation comment
- `tests/test_api.py` — 12 new tests for /auth/* router and refresh flow
