# Team Memory

_Human-readable log of the ai-office framework's shared state. Updated after every significant change._

---

## Framework Status

**Current phase:** Production-ready
**Last updated:** 2026-04-11

The ai-office framework is fully operational. 16 specialized agents run as Claude CLI subprocesses with `--output-format stream-json`. All work is project-scoped. The dashboard provides a visual office floor with live agent output, a Memory tab for browsing decisions, and controls for peer review and token tracking.

---

## Active Decisions

- **Memory**: Agent decisions live in `projects/{slug}/memory/decisions/{category}.md` — five categories: `architecture`, `implementation`, `compliance`, `brand`, `strategy`. Seeded at project kickoff.
- **Self-eval**: Agents score output 1–10. Server retries up to 2x if score is below 7.
- **Peer review**: Togglable via dashboard (Review: ON/OFF). Assignments: arve→odd, bjorn→arve, dag→arve, jorunn↔ingrid, else↔halvard.
- **Web search**: Agents with web access (else, halvard, guro, laila, knut, nora, frode, jorunn, magnus) use OpenAI `gpt-4o-search-preview` via MCP. Shown with orange indicator in dashboard.
- **Phased execution**: Phase 1 (bjorn, dag, magnus) → Phase 2 (arve, ingrid, jorunn, else, halvard, frode, nora, guro) → Phase 3 (odd, per). Never run arve in parallel with magnus on user-data projects.
- **Task files**: `YYYY-MM-DD-<slug>.md` in `projects/{slug}/tasks/{bucket}/`
- **Output**: All deliverables go to `output/{slug}/{category}/` — `output/` and `projects/` are gitignored
- **MCP config**: `mcp_search.json` regenerated at server startup with real `OPENAI_API_KEY` — never commit it
- **Stuck tasks**: `_recover_stuck_tasks()` moves any `active/` tasks back to `backlog` on server restart
- **Magnus labels**: `LAUNCH BLOCKER` / `HIGH RISK` / `ADVISORY` — arve must implement all `LAUNCH BLOCKER` items

---

## Timeline

- **2026-03-27**: Framework initialized. Norwegian team of 16 agents integrated.
- **2026-03-27**: Login page (`dashboard/login.html`), sessionStorage auth, credentials: admin/office.
- **2026-03-28**: `core/` module extracted — shared domain logic for tasks, memory, projects, agents.
- **2026-03-28**: Project workspaces — each project has isolated `tasks/`, `memory/`, and `output/`.
- **2026-03-29**: Dashboard redesigned — visual office floor with glass panels, agent avatars at desks.
- **2026-03-29**: Kickoff flow — describe a project, orchestrator generates a phased task plan.
- **2026-03-29**: Output panel — browse and read all agent deliverables in the dashboard.
- **2026-03-30**: Neutral project — Bjorn, Ingrid, Else, Jorunn, Arve all completed tasks.
- **2026-04-01**: Neutral project — Else, Magnus, Nora, Halvard, Knut completed. Per-agent work windows added.
- **2026-04-05**: Structured decisions memory — `projects/{slug}/memory/decisions/{category}.md`. Kickoff seeds `strategy.md`.
- **2026-04-06**: Self-evaluation loop — agents score 1–10, server retries up to 2× if below 7.
- **2026-04-06**: Peer review system — second agent subprocess reviews output before dispatch unblocks.
- **2026-04-07**: Dashboard: peer review toggle button, token tracking (SQLite), Memory tab in output panel.
- **2026-04-08**: OpenAI web search via MCP — search agents get `--mcp-config` pointing to `tools/perplexity_search.py`.
- **2026-04-09**: Dashboard orange indicator for web search agents (dashed canvas ring, orange text).
- **2026-04-09**: Fixed MCP key substitution bug — `_write_mcp_config()` bakes real API key at startup.
- **2026-04-10**: Stuck-task recovery — `_recover_stuck_tasks()` on server restart. `output/` and `projects/` gitignored.
- **2026-04-11**: Stale file audit — CLAUDE.md rewritten, all 16 agent files updated, dead `backend/`+`frontend/` deleted, `core/projects.py` and `cli/office.py` updated.

---

## Agent Roster

| Agent | Role | Phase | Web Search | Peer Review |
|-------|------|-------|------------|-------------|
| bjorn | Architecture | 1 | — | reviewed by arve |
| dag | Infrastructure / DevOps | 1 | — | reviewed by arve |
| magnus | Legal / Compliance | 1 | yes | — |
| arve | Implementation | 2 | — | reviewed by odd |
| ingrid | UI/UX Design | 2 | — | reviewed by jorunn |
| jorunn | Brand / Tone | 2 | yes | reviewed by ingrid |
| else | Research / Insights | 2 | yes | reviewed by halvard |
| frode | Sprint Planning | 2 | yes | — |
| halvard | Growth Strategy | 2 | yes | reviewed by else |
| guro | Social Media | 2 | yes | — |
| nora | Pricing / Finance | 2 | yes | — |
| knut | Project Tracking | 2 | yes | — |
| laila | Customer Support | 2 | yes | — |
| odd | API Testing | 3 | — | — |
| per | Performance | 3 | — | — |
