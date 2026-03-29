# Docker & CI/CD Setup

**Agent:** orchestrator
**Status:** active
**Created:** 2026-03-29

## Description

Create a Docker Compose setup with services for the FastAPI app and PostgreSQL. Write a Dockerfile for the FastAPI app using a slim Python base image. Set up environment variable handling via .env files. Create a GitHub Actions CI pipeline that runs linting (ruff), type checking (mypy), and pytest on every push. Add a separate CD step that builds and pushes a Docker image on merge to main. Output docker-compose.yml, Dockerfile, and .github/workflows/ci.yml.
