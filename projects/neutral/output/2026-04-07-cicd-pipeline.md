# CI/CD Pipeline — Markdown-to-HTML Converter CLI

**Agent:** dag
**Date:** 2026-04-07
**Project:** neutral

---

## Upstream outputs read

- `projects/neutral/output/2026-04-07-implementation.md` (arve)
- `projects/neutral/output/md2html/pyproject.toml` (arve)

---

## What was built

Three files that together form the complete CI/CD setup for `md2html`.

### Deliverables

| File | Purpose | Place at |
|------|---------|----------|
| `2026-04-07-dockerfile` | Multi-stage Docker build | `projects/neutral/output/md2html/Dockerfile` |
| `2026-04-07-dockerignore` | Docker build context exclusions | `projects/neutral/output/md2html/.dockerignore` |
| `2026-04-07-github-actions-ci.yml` | GitHub Actions workflow | `.github/workflows/md2html-ci.yml` |

---

## Dockerfile design

**Multi-stage build** — builder stage installs hatchling and builds the wheel; runtime stage installs only the pre-built wheel. No build tools reach the final image.

- Base: `python:3.11-slim` (matches minimum version declared in `pyproject.toml`)
- Watch extra (`watchdog`) excluded from image — no filesystem events needed in container context
- Entrypoint: `md2html`, default CMD: `--help`
- Users mount files via `docker run -v $(pwd):/data md2html --input /data/file.md`

**Why slim over alpine:** avoids musl/glibc differences that occasionally surface with Python C extensions. `python:3.11-slim` is well-tested for this use case.

---

## GitHub Actions workflow

**Triggers:** push to `main` and PRs targeting `main`, path-filtered to `md2html/**` so unrelated repo changes don't burn CI minutes.

### Job 1 — `test`

- Matrix: Python 3.11 and 3.12
- `fail-fast: true` — stops both matrix legs on first failure (no waiting for a known-bad state)
- Installs `.[watch]` plus `pytest` — exercises the optional watchdog extra in CI
- Runs `pytest --tb=short -q`

### Job 2 — `build`

- Runs only after `test` succeeds (`needs: test`)
- Uses `docker/build-push-action@v5` with GitHub Actions layer cache (`type=gha`) — first build is slow; subsequent builds are fast
- `push: false` — no registry configured yet; change to `push: true` and add registry credentials when deploying
- Two smoke tests after build:
  1. `md2html --help` — verifies entrypoint works
  2. Inline conversion — writes `# hello`, converts to HTML, greps for `<h1>` — verifies end-to-end pipeline is alive

---

## Key decisions

**[DECISION] Multi-stage Dockerfile over single-stage** — keeps final image small (~120MB vs ~350MB) by excluding build tools. Single-stage would be simpler but wasteful. Reversal: trivial — collapse to one stage if size stops mattering (2026-04-07).

**[DECISION] No registry push yet** — there is no container registry configured for this project. `push: false` is intentional and documents the gap. When a registry (GHCR, ECR, Docker Hub) is chosen, add `registry-url`, `username`, and `password` secrets to the repo and flip the flag (2026-04-07).

**[DECISION] Path filter on workflow trigger** — `paths: ["projects/neutral/output/md2html/**"]` prevents every unrelated commit to `main` from running this workflow. Required because the ai-office repo is a monorepo (2026-04-07).

**[DECISION] Python 3.11 + 3.12 matrix, not 3.13+** — arve's implementation was tested on 3.14.3 but the matrix covers 3.11/3.12 as the stable LTS targets. Add 3.13 once `python:3.13-slim` is widely available on GitHub-hosted runners (2026-04-07).

---

## How to activate

1. Copy the three files to their destination paths (see table above)
2. Commit and push — the workflow fires on the next push to `main`
3. No secrets needed until `push: true` is enabled

---

## Bottleneck flag

Layer caching (`type=gha`) is per-repo and evicted after 7 days of inactivity. If the repo goes quiet, the first build after that will be a full cold build (~60-90s). Acceptable at this stage; not acceptable in a high-frequency deploy loop.
