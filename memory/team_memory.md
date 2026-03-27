# Team Memory

_This file is the human-readable log of the ai-office team's shared state. Update it after every significant action._

---

## Project Status

**Current phase:** Initialization
**Last updated:** 2026-03-27

The ai-office framework has been initialized with the Norwegian team agents.

---

## Active Decisions

- Agents should always read `team_memory.json` before starting work
- Task files use the naming convention `YYYY-MM-DD-<slug>.md`
- One agent per task — no concurrent ownership
- Shared memory lives at `memory/team_memory.json` and `memory/team_memory.md`

---

## Recent Updates

- 2026-03-27: Framework initialized. Repo structure created.
- 2026-03-27: Norwegian team agents integrated: Arve, Bjørn, Dag, Else, Frode, Halvard, Guro, Jorunn, Ingrid, Knut, Laila, Magnus, Nora, Odd, Per.
- 2026-03-27: Login page built. Created `dashboard/login.html` and added `/api/login` POST endpoint to `server.py`. Credentials configurable via `OFFICE_USER` / `OFFICE_PASS` env vars (default: admin/admin).
- 2026-03-27: Login page rebuilt (self-contained). `dashboard/login.html` now uses sessionStorage auth (no backend endpoint needed). Credentials: admin/office. Dashboard auth-gated at top of script block.

---

## Agent Notes

- **Orchestrator** (2026-03-27): Completed task `2026-03-27-build-login-page.md` and `2026-03-27-build-a-login-screen.md`. Built `dashboard/login.html` (dark-themed login form matching dashboard style) and added `/api/login` POST handler to `server.py`. Credentials via `OFFICE_USER`/`OFFICE_PASS` env vars.
- **Orchestrator** (2026-03-27): Re-ran build-login-page tasks. Delegated to Arve. Final implementation: self-contained sessionStorage auth in `dashboard/login.html`, credentials admin/office, auth gate added to `dashboard/index.html` script. Tasks moved to completed/.
- **Arve** (coding): Ready. No active tasks.
- **Bjørn** (architecture): Ready. No active tasks.
- **Dag** (devops): Ready. No active tasks.
- **Else** (research) (2026-03-27): Completed task `2026-03-27-research-the-top-5-open-source-frameworks-for-building-multi-agent-ai-systems.md`. Researched and documented the top 5 open source frameworks for building multi-agent AI systems: LangGraph, AutoGen/Microsoft Agent Framework, CrewAI, OpenAI Agents SDK, and OpenHands. Key findings: no single framework wins across all dimensions; AutoGen maintenance mode is a real risk for new projects; LangGraph is production standard but carries steep learning curve; OpenHands is a distinct category (software engineering automation, not general orchestration). Full report at `output/2026-03-27-top-5-open-source-multi-agent-frameworks.md`.
- **Frode** (sprint planning): Ready. No active tasks.
- **Halvard** (growth): Ready. No active tasks.
- **Guro** (social media): Ready. No active tasks.
- **Jorunn** (branding): Ready. No active tasks.
- **Ingrid** (UI/UX): Ready. No active tasks.
- **Knut** (project tracking): Ready. No active tasks.
- **Laila** (support): Ready. No active tasks.
- **Magnus** (legal) (2026-03-27): Completed task `2026-03-27-draft-legal-document-on-ai-agent-usage-in-business.md`. Drafted `docs/ai-agent-usage-policy.md` — a comprehensive AI Agent Usage Policy covering GDPR compliance (lawful basis, data minimization, DPA requirements, erasure obligations), EU AI Act high-risk classification, liability limitations, human-in-the-loop requirements, transparency/disclosure obligations, incident response, and a pre-deployment risk checklist. Added compliance requirement: all AI agent deployments must be registered in an Agent Registry before go-live. Recommend professional legal review before external adoption.
- **Orchestrator** (2026-03-27): Completed task `2026-03-27-research-the-top-5-competitors-building-ai-agent-platforms-and-summarize-their-strengths.md`. Researched and documented the top 5 AI agent platform competitors as of early 2026: LangGraph (LangChain), Microsoft Agent Framework (AutoGen + Semantic Kernel), CrewAI, OpenAI Agents SDK + Responses API, and Salesforce Agentforce. Full report saved to `output/2026-03-27-ai-agent-platform-competitor-research.md`.
- **Orchestrator** (2026-03-27): Detected duplicate active task for competitor research (already completed). Removed duplicate from `tasks/active/`, verified output and completed task file are consistent.
- **Orchestrator** (2026-03-27): Completed task `2026-03-27-research-the-top-5-open-source-frameworks-for-building-multi-agent-ai-systems.md`. Delegated to Else. Report at `output/2026-03-27-top-5-open-source-multi-agent-frameworks.md`. Top 5: LangGraph, AutoGen/Microsoft Agent Framework, CrewAI, OpenAI Agents SDK, OpenHands.
- **Nora** (finance): Ready. No active tasks.
- **Odd** (API testing): Ready. No active tasks.
- **Per** (benchmarking): Ready. No active tasks.
