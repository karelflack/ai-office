# CI/CD Pipeline

**Agent:** dag
**Status:** active
**Created:** 2026-04-07
**depends_on:** 2026-04-07-implementation.md

## Description

Set up CI/CD for the markdown-to-HTML converter. Create: (1) a Dockerfile that installs dependencies and packages the CLI tool, (2) a GitHub Actions workflow that runs on push to main — installs deps, runs the test suite, and builds the Docker image, (3) a .dockerignore and any necessary build scripts. Ensure the pipeline fails fast on test errors. Base this on arve's implementation structure.
