# Pathless AI Office

A virtual office where a team of AI agents do real work — research, code, design, legal, finance, growth — coordinated through a visual dashboard.

You build a team, brief them on what to make, and watch them ship. The orchestrator breaks the brief into tasks, agents run in phases, and they produce real deliverables: code, architecture docs, brand guides, pricing models, compliance reports. When done, the system runs your tests, opens a GitHub PR, and writes a summary to Notion — automatically.

---

## Getting Started

```bash
pip install -r requirements.txt
cp .env.example .env   # add your API keys + set OFFICE_PASS
python3 server.py
# open http://localhost:8000
```

If `OFFICE_PASS` is empty, the server prints a one-time random password to the terminal on startup. Add a value to `.env` to keep it across restarts.

---

## How It Works

1. **Trigger** — create a project from the dashboard, or label a Linear issue with the trigger label
2. **Plan** — the orchestrator generates a phased task plan, restricted to your team if one is set
3. **Run** — agents execute in three phases (foundation → build → verify), sharing memory as they go
4. **CI** — tests run automatically when all agents finish; failures route back to arve for repair
5. **Ship** — on passing, a GitHub PR is opened, Notion is updated, and Linear issues are closed

---

## The Pipeline

```
Linear webhook ──┐
                 ├──► Orchestrator ──► Phase 1 — foundation (architecture, research, compliance)
Dashboard ───────┘                          │
                                            ▼
                                     Phase 2 — build (code, design, brand, growth, finance)
                                            │
                                            ▼
                                     Phase 3 — verify (API tests, performance)
                                            │
                                            ▼
                                       CI tests ──fail──► arve fixes ──► CI tests
                                            │
                                           pass
                                            │
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                          GitHub PR      Notion      Linear + Slack
```

---

## Agents

The office ships with 16 built-in agents. You can also upload custom agents — drop a markdown role file in the dashboard and it becomes a first-class agent immediately.

| Agent | Specialty |
|---|---|
| **Orchestrator** | Task planning, agent assignment |
| **Arve** | Code — implementation, bug fixes |
| **Bjorn** | System architecture, data models |
| **Dag** | DevOps, Docker, CI/CD |
| **Magnus** | Legal, compliance, GDPR |
| **Ingrid** | UI/UX design, wireframes |
| **Jorunn** | Brand identity, tone of voice |
| **Else** | Research, competitor analysis |
| **Halvard** | Growth strategy, acquisition |
| **Frode** | Sprint planning, backlog |
| **Nora** | Pricing, revenue modeling |
| **Guro** | Social media, copywriting |
| **Knut** | Project tracking, milestones |
| **Laila** | Customer support, docs |
| **Odd** | API testing, validation |
| **Per** | Performance benchmarking |

Built-in agents are read-only. Custom agents can be edited or deleted from the Agents page.

---

## Teams

A team is a curated subset of agents with a fixed canon skeleton plus deputies:

- **Canon (always present):** orchestrator, bjorn (Phase 1), arve (Phase 2), odd (Phase 3)
- **Deputies:** any other agents you assign — built-in or custom

When a project is bound to a team, kickoff is **hard-restricted** to team members. The orchestrator decides — per project — which canon agents and deputies fire and which phase each deputy lands in. Same deputy can land in different phases on different projects.

No team selected → all 16 built-in agents are available with the default phase rules.

---

## Sandbox

Pick any agent, give them a one-off task, see what they produce. No project files, no memory, no other agents. Useful for trying out a custom agent before adding them to a team.

---

## Skills

A library of reusable skill markdown files (`skills/{name}.md`) that you can browse and upload from the dashboard. Skills are a passive library today — wiring them into agent prompts is on the roadmap.

---

## Integrations

All integrations are optional. Add keys to `.env` to enable.

| Integration | What it does |
|---|---|
| **Linear** | Creates issues per task at kickoff, updates them as tasks complete, triggers runs via webhook |
| **GitHub** | Creates repo, pushes code, opens PR when all agents finish |
| **Notion** | Writes a project summary page (architecture, strategy, implementation, PR link) on completion |
| **Slack** | Sends agent completion notifications via n8n |
| **n8n** | Webhook bridge for Slack notifications |

---

## Quality Loop

Every agent run goes through three layers:

1. **Self-evaluation** — each agent scores its output 1–10. Below 7 → retries with specific fixes (up to 2x)
2. **Peer review** — selected agents review each other's work. Revision requested → original agent re-runs. When a project is bound to a team, peer review only fires if the reviewer is also in the team.
3. **CI tests** — pytest or npm test runs after all agents finish. Fails → arve fixes and reruns (up to 2x)

---

## Shared Memory

Agents share decisions across three levels:

| Level | File | Scope |
|---|---|---|
| Team | `memory/team_memory.json` | Global across all projects |
| Project | `projects/{slug}/memory/project_memory.json` | Per project |
| Decisions | `projects/{slug}/memory/decisions/{category}.md` | Per category |

Categories: `architecture`, `implementation`, `strategy`, `brand`, `compliance`.

Each agent reads relevant categories before starting and appends a structured entry after completing.

---

## Budget Guardrail

Set `PROJECT_BUDGET_USD` to cap per-project spend. The server checks the project's running cost before every agent (or peer-review) spawn and pauses the project once the cap is crossed. Resume from the dashboard or `POST /api/projects/{slug}/resume`.

---

## Health Check

```bash
python3 tests/health_check.py
```

Runs 15 component checks (claude CLI, API key, server, auth, project lifecycle, task lifecycle, memory thread safety, webhook HMAC, CI detection, GitHub, Notion, Linear, output dir, agent files). Spends no tokens.

Also available as `GET /api/health`.

---

## Environment Variables

```bash
ANTHROPIC_API_KEY=        # required
OFFICE_USER=admin         # dashboard login username
OFFICE_PASS=              # dashboard login password — required (random one generated if blank)
OPENAI_API_KEY=           # optional — web search for agents
GITHUB_TOKEN=             # optional — push code + open PR
GITHUB_USERNAME=          # optional — required if GITHUB_TOKEN set
LINEAR_API_KEY=           # optional — create/update Linear issues
LINEAR_TEAM_ID=           # optional — required if LINEAR_API_KEY set
LINEAR_WEBHOOK_SECRET=    # optional — verify Linear webhook signatures
WEBHOOK_TRIGGER_LABEL=    # optional — label that triggers a run (default: ai-office)
NOTION_API_KEY=           # optional — write project summary to Notion
NOTION_DATABASE_ID=       # optional — required if NOTION_API_KEY set
N8N_WEBHOOK_URL=          # optional — Slack notifications via n8n
PROJECT_BUDGET_USD=       # optional — per-project spend cap in USD (auto-pauses)
```

---

## Folder Structure

```
server.py                  — HTTP server + REST API + agent orchestration
dashboard/
  menu.html                — landing page (after login)
  index.html               — project view (run, output, memory)
  new-project.html         — create a project, optionally bind to a team
  agents.html              — browse / upload / delete custom agents
  teams.html               — build a team (canon + deputies)
  skills.html              — browse / upload skill markdown
  sandbox.html             — ad-hoc single-agent runs
  login.html
core/
  agents.py                — filename-based agent registry (16 built-ins + custom)
  teams.py                 — team CRUD, canon skeleton
  skills.py                — skill library
  tasks.py                 — task lifecycle, dependency resolution
  projects.py              — project CRUD
  memory.py                — run logs, project memory
  tokens.py                — SQLite usage + cost tracking
agents/*.md                — role definitions (16 built-ins + any custom uploads)
teams/*.json               — saved teams
skills/*.md                — uploaded skill files
integrations/              — github, linear, notion, n8n, jira modules
tools/                     — MCP server for web search
tests/test_core.py         — pytest suite
tests/health_check.py      — 15-component system health check
CLAUDE.md                  — agent session protocol
SETUP.md                   — onboarding guide
.env.example               — all environment variables documented
```

---

## License

MIT
