# Pathless AI Office

A virtual office where a team of 16 AI agents do real work — research, code, design, legal, finance, growth — coordinated through a visual dashboard.

You describe what you want to build (or create a Linear issue). The orchestrator assigns the right agents, breaks it into tasks, and they work through it in parallel. Each agent produces real deliverables: code, architecture docs, research reports, brand guides, pricing models. When done, the system runs your tests, opens a GitHub PR, and writes a summary to Notion — automatically.

---

## Getting Started

```bash
pip install -r requirements.txt
cp .env.example .env   # add your API keys
python3 server.py
# open http://localhost:8000
```

---

## How It Works

1. **Trigger** — create a Linear issue labelled `pathless`, or use the Kickoff screen in the dashboard
2. **Plan** — the orchestrator generates a task plan and assigns the right agents
3. **Run** — agents execute in three phases, sharing memory as they go
4. **CI** — tests run automatically when all agents finish
5. **Ship** — on passing, a GitHub PR is opened, Notion is updated, and Linear issues are closed

---

## The Pipeline

```
Linear webhook  ──┐
                  ├──► Orchestrator ──► Phase 1 (bjorn, dag, magnus)
Dashboard kickoff ┘                         │
                                            ▼
                                    Phase 2 (arve, ingrid, jorunn, else, halvard, frode, nora, guro)
                                            │
                                            ▼
                                    Phase 3 (odd, per)
                                            │
                                            ▼
                                       CI Tests ──fail──► arve fixes ──► CI Tests
                                            │
                                           pass
                                            │
                              ┌─────────────┼─────────────┐
                              ▼             ▼              ▼
                           GitHub PR     Notion        Linear + Slack
```

---

## The Team

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
2. **Peer review** — selected agents review each other's work. Revision requested → original agent re-runs
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

## Environment Variables

```bash
ANTHROPIC_API_KEY=        # required
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
```

---

## Folder Structure

```
server.py              — HTTP server + REST API + agent orchestration
dashboard/index.html   — full frontend (single file)
dashboard/diagram.html — system architecture diagram
core/
  agents.py            — agent registry
  tasks.py             — task lifecycle, dependency resolution
  projects.py          — project CRUD
  memory.py            — run logs, project memory
agents/*.md            — role definitions for each agent
tools/                 — MCP server for web search
tests/test_core.py     — 79 pytest tests
CLAUDE.md              — agent session protocol
SETUP.md               — onboarding guide
.env.example           — all environment variables documented
```

---

## License

MIT
