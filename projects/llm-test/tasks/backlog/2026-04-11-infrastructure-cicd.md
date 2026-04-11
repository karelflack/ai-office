# Infrastructure & CI/CD

**Agent:** dag
**Status:** backlog
**Created:** 2026-04-11
**Model:** claude-sonnet-4-6
**depends_on:** 2026-04-11-system-architecture.md

## Description

Using bjorn's architecture output as the reference, produce: (1) a docker-compose.yml for local development with services for the Python API (FastAPI), PostgreSQL, Redis (for async job queue), and a pgAdmin container; (2) a Dockerfile for the Python API service using a multi-stage build (builder + slim runtime); (3) a GitHub Actions CI workflow (.github/workflows/ci.yml) that runs lint (ruff), type check (mypy), and pytest on every PR; (4) a GitHub Actions CD workflow that builds and pushes a Docker image to GHCR on merge to main. All files should be placed under projects/stackr/output/infra/. Document environment variables and secrets management approach in 2026-04-11-infra-setup.md.
