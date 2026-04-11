## [2026-04-11] bjorn — System Architecture

**Decision:** Stackr uses FastAPI (Python) backend on Railway, React + TypeScript frontend on Vercel, Supabase (Postgres + Auth), Redis for job queue (ARQ), and OSV.dev for vulnerability data. Row-level security (RLS) for multi-tenancy. JWT auth via Supabase. Async vulnerability scanning via ARQ workers.

**Reason:** Simple stack a 2-person team can maintain. Supabase RLS is enforced at Postgres level, removing a class of application bugs. ARQ is lightweight async queue that works with FastAPI. OSV.dev is free, maintained by Google, covers all major ecosystems. JWTs are stateless and API-first friendly.

**Impact:**
- Arve: use `team_id` on every DB write; never bypass RLS with service role key in user-facing routes; inject team context via FastAPI dependency from JWT
- Dag: Railway needs web dyno + worker dyno + Redis add-on; env vars: SUPABASE_URL, SUPABASE_SERVICE_KEY, REDIS_URL, OSV_API_URL
- Magnus: user PII in Supabase auth.users; dependency/CVE data is confidential per team; RLS enforces tenant isolation
- Ingrid: scan jobs are async — UI must poll /scan-jobs/{id} every ~3s while status is queued/running
---
