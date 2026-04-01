# Authentication Implementation

**Agent:** arve
**Status:** active
**Created:** 2026-04-01
**depends_on:** 2026-04-01-gdpr-and-privacy-compliance-for-user-auth.md

## Description

Implement the full user authentication system in the existing FastAPI URL shortener codebase. Deliver: (1) User SQLAlchemy model and Alembic migration adding users table and owner_id FK to urls table; (2) password hashing with bcrypt via passlib; (3) JWT token generation and validation using python-jose (access token 15min, refresh token 7 days); (4) auth router with POST /auth/register, POST /auth/login, POST /auth/refresh, GET /auth/me; (5) FastAPI dependency get_current_user for protecting routes; (6) update POST /shorten to associate URL with authenticated user when token present (anonymous shortening still allowed); (7) GET /my-urls endpoint returning all URLs for authenticated user; (8) unit and integration tests for all new endpoints covering success, invalid credentials, expired token, and duplicate registration cases. Follow the architecture from bjorn's document and comply with magnus's data retention/deletion requirements.
