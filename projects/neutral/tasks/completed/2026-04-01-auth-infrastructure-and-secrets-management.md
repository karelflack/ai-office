# Auth Infrastructure and Secrets Management

**Agent:** dag
**Status:** completed
**Created:** 2026-04-01
**Completed:** 2026-04-01
**depends_on:** 2026-04-01-authentication-implementation.md

## Description

Update the DevOps setup to support the authentication system. Deliver: (1) add JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS to docker-compose.yml env vars with secure defaults and .env.example entries; (2) update the Dockerfile if any new dependencies (python-jose, passlib[bcrypt]) require system packages; (3) add Alembic migration step to the CI/CD pipeline so auth migrations run automatically on deploy; (4) add rate-limiting config (e.g. slowapi or nginx limit_req) for /auth/login and /auth/register endpoints to prevent brute force; (5) update the ops README section with instructions for rotating the JWT secret key in production. Output updated config files and an updated ops README section.

## Deliverables

- output/2026-04-01-docker-compose-auth.yml
- output/2026-04-01-env-example-auth
- output/2026-04-01-dockerfile-auth
- output/2026-04-01-github-actions-ci-auth.yml
- output/2026-04-01-rate-limiting-setup.py
- output/2026-04-01-ops-readme-auth-section.md
