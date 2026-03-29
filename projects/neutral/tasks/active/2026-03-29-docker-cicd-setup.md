# Docker & CI/CD Setup

**Agent:** orchestrator
**Status:** active
**Created:** 2026-03-29

## Description

Create a docker-compose.yml with services for the FastAPI app and PostgreSQL (with a named volume for persistence). Write a Dockerfile for the FastAPI service using a multi-stage build. Set up a GitHub Actions workflow that runs on push: lint with ruff, run pytest, and build the Docker image. Include an .env.example with all required environment variables (DATABASE_URL, SECRET_KEY, etc.). Output all files to output/.
