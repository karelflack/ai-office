# System Architecture

**Agent:** bjorn
**Status:** active
**Created:** 2026-04-11
**Model:** claude-sonnet-4-6

## Description

Design the full Stackr system architecture. Produce: (1) a Mermaid C4 context diagram showing how users, the dashboard frontend, backend API, and external data sources interact; (2) a component diagram for the Python backend — API layer, dependency ingestion service, vulnerability scanner integration (e.g. OSV or Snyk API), and PostgreSQL schema for stacks, dependencies, CVEs, and teams; (3) a data model ERD covering all core entities with field types and relationships; (4) a decision record on auth strategy (JWT vs session), multi-tenancy model (schema-per-tenant vs row-level), and async job approach for vulnerability scanning. Output to projects/stackr/output/ as 2026-04-11-system-architecture.md.
