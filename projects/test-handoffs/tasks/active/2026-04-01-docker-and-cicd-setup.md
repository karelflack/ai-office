# Docker and CI/CD Setup

**Agent:** dag
**Status:** active
**Created:** 2026-04-01
**depends_on:** 2026-04-01-backend-implementation.md

## Description

Containerize the URL shortener API and set up a CI/CD pipeline. Write a Dockerfile and docker-compose.yml (app + database + optional Redis cache). Configure a GitHub Actions workflow that runs linting and tests on push, and builds the Docker image on merge to main. Include environment variable handling via .env.example and document the local dev and deployment flow in a concise ops README.
