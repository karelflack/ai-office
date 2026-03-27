# Build login page

**Agent:** orchestrator
**Status:** completed
**Completed:** 2026-03-27

## Work Done
- Created `dashboard/login.html`: dark-themed login form matching dashboard style.
- Added `POST /api/login` handler to `server.py`. Credentials via `OFFICE_USER`/`OFFICE_PASS` env vars (default: admin/admin).
- On success redirects to `/dashboard/`.
**Created:** 2026-03-27
