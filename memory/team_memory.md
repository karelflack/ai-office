# Team Memory

_This file is the human-readable log of the ai-office team's shared state. Update it after every significant action._

---

## Project Status

**Current phase:** Active development
**Last updated:** 2026-04-01

The ai-office framework is operational. The full Norwegian team is integrated and has completed multiple tasks across two projects (Neutral, Landing Page). The dashboard has a visual office floor, per-agent work windows, project workspaces, kickoff flow, and output panel.

---

## Active Decisions

- Agents should always read `team_memory.json` before starting work
- Task files use the naming convention `YYYY-MM-DD-<slug>.md`
- One agent per task — no concurrent ownership
- Shared memory lives at `memory/team_memory.json` and `memory/team_memory.md`
- Project-scoped memory lives at `projects/{slug}/memory/project_memory.json`
- All deliverables go to `projects/{slug}/output/` — never to repo root
- Orchestrator must delegate specialist work — never do it directly

---

## Recent Updates

- 2026-03-27: Framework initialized. Norwegian team integrated (Arve, Bjørn, Dag, Else, Frode, Halvard, Guro, Jorunn, Ingrid, Knut, Laila, Magnus, Nora, Odd, Per).
- 2026-03-27: Login page built (`dashboard/login.html`, sessionStorage auth, credentials: admin/office).
- 2026-03-27: Else — top 5 open source multi-agent frameworks researched and documented.
- 2026-03-27: Else — top 5 AI agent platform competitors researched and documented.
- 2026-03-27: Magnus — AI Agent Usage Policy drafted (GDPR, EU AI Act, liability, incident response).
- 2026-03-28: `core/` module extracted — shared domain logic for tasks, memory, projects, agents.
- 2026-03-28: Project workspaces added — each project has isolated tasks, memory, and output.
- 2026-03-29: Dashboard redesigned — visual office floor with glass panels, agent avatars at desks.
- 2026-03-29: Kickoff flow added — describe a project, orchestrator generates a task plan.
- 2026-03-29: Output panel added — browse and read all agent deliverables in the dashboard.
- 2026-03-30: Neutral project — Bjorn, Ingrid, Else, Jorunn, Arve all completed landing page tasks.
- 2026-04-01: Neutral project — Else (competitive analysis), Magnus (privacy policy + compliance checklist), Nora (pricing model), Halvard (growth strategy) all completed.
- 2026-04-01: Per-agent work windows added — each running agent gets their own live output window.

---

## Agent Notes

- **Orchestrator**: Routes tasks, delegates to specialists. Completed login page (delegated to Arve) and open source frameworks research (delegated to Else). Duplicate competitor research task detected and cleaned up.
- **Arve** (coding): Completed landing page implementation for Neutral project. `projects/neutral/output/landing-page/` — full Next.js 15 codebase.
- **Bjørn** (architecture): Completed tech stack selection for Neutral project. Next.js static export, Tailwind v4, Framer Motion, Vercel.
- **Dag** (devops): Ready. No active tasks.
- **Else** (research): Completed top 5 open source multi-agent frameworks (`output/2026-03-27-top-5-open-source-multi-agent-frameworks.md`). Completed AI agent platform competitor research (`output/2026-03-27-ai-agent-platform-competitor-research.md`). Completed Neutral market research (`projects/neutral/output/2026-03-30-market-research.md`). Completed competitive analysis for AI Office launch (`projects/neutral/output/2026-04-01-competitive-analysis.md`).
- **Frode** (sprint planning): Ready. No active tasks.
- **Halvard** (growth): Completed go-to-market playbook for first 100 customers (`projects/neutral/output/2026-04-01-growth-strategy.md`).
- **Guro** (social media): Ready. No active tasks.
- **Jorunn** (branding): Completed brand identity and homepage copy for Neutral (`projects/neutral/output/2026-03-30-brand-copy.md`).
- **Ingrid** (UI/UX): Completed visual design system and wireframe for Neutral (`projects/neutral/output/2026-03-30-design-direction.md`).
- **Knut** (project tracking): Completed B2B launch milestone tracker for Neutral (`projects/neutral/output/2026-04-01-launch-milestones.md`).
- **Laila** (support): Ready. No active tasks.
- **Magnus** (legal): Completed AI Agent Usage Policy (`output/ai-agent-usage-policy.md`). Completed privacy policy and engineering compliance checklist for Neutral (`projects/neutral/output/2026-04-01-privacy-policy.md`, `2026-04-01-compliance-checklist.md`).
- **Nora** (finance): Completed B2B SaaS pricing model for Neutral — 3 tiers, unit economics, revenue projections (`projects/neutral/output/2026-04-01-pricing-model.md`).
- **Odd** (API testing): Ready. No active tasks.
- **Per** (benchmarking): Ready. No active tasks.
