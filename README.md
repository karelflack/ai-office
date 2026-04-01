# AI Office

A virtual office where a team of 16 AI agents do real work — research, code, design, legal, finance, growth — coordinated through a visual dashboard.

You describe what you want to build. The orchestrator assigns the right agents, breaks it into tasks, and they work through it in parallel. Each agent produces real deliverables: code, architecture docs, research reports, brand guides, pricing models.

---

## Getting Started

```bash
python3 server.py
# open http://localhost:8000/dashboard/
```

---

## How It Works

1. **Create a project** — use the project switcher in the header
2. **Kickoff** — describe what you want to build in one or two sentences
3. **Review the plan** — the orchestrator generates tasks and assigns agents
4. **Activate tasks** — move them from Backlog to Active
5. **Run All Active** — all agents start simultaneously, each in their own work window
6. **Review output** — open the Output panel to read what they produced

---

## The Team

| Agent | Department | Specialty |
|---|---|---|
| **Orchestrator** | — | Routes tasks, maintains memory, reviews work |
| **Arve** | Engineering | Writes, reviews, and debugs code |
| **Bjorn** | Engineering | System architecture and infrastructure design |
| **Dag** | Engineering | Deployments, CI/CD, Docker, monitoring |
| **Else** | Product | User research, competitor analysis, product insights |
| **Frode** | Product | Sprint planning, backlog prioritization |
| **Ingrid** | Design | UI/UX design, user flows, wireframes |
| **Jorunn** | Design | Brand identity, naming, tone of voice |
| **Halvard** | Marketing | Growth strategy, acquisition, onboarding |
| **Guro** | Marketing | Social media content, copywriting |
| **Knut** | Project Management | Tracking, milestones, blockers |
| **Laila** | Studio Operations | Customer support, help documentation |
| **Magnus** | Studio Operations | Legal, compliance, GDPR |
| **Nora** | Studio Operations | Pricing, revenue modeling, unit economics |
| **Odd** | Testing | API testing, endpoint validation |
| **Per** | Testing | Performance benchmarking, load testing |

---

## Project Workspaces

Each project is fully isolated:

```
projects/
└── my-project/
    ├── project.json          — name, description, created date
    ├── tasks/
    │   ├── backlog/          — tasks waiting to be activated
    │   ├── active/           — tasks currently running
    │   └── completed/        — finished tasks
    ├── memory/
    │   └── project_memory.json  — project-specific context for agents
    └── output/
        └── README.md         — index of all deliverables
```

Agents read project memory for context and write all deliverables to `output/`.

---

## Folder Structure

```
ai-office/
├── agents/          — role definitions for each agent
├── core/            — shared domain logic (tasks, memory, projects, agents)
├── cli/
│   └── office.py   — CLI for managing tasks and agents
├── dashboard/
│   └── index.html  — visual office dashboard
├── memory/          — global team memory
├── projects/        — project workspaces
├── runs/            — live run output (streamed per task)
├── tasks/           — global task queue (backlog/active/completed)
├── server.py        — HTTP server + REST API
└── CLAUDE.md        — entry point and protocol for any agent session
```

---

## Dashboard Features

- **Visual office floor** — all 16 agents at their desks, animated when working
- **Per-agent work windows** — each running agent gets their own live output window
- **Task Manager** — create, activate, assign, and delete tasks
- **Kickoff** — describe a project, get an auto-generated task plan with assigned agents
- **Run All Active** — start all active tasks simultaneously
- **Output panel** — browse and read all files agents have produced
- **Activity log** — real-time feed of what agents are doing

---

## Agent Memory

Agents share two levels of memory:

| File | Scope | Purpose |
|---|---|---|
| `memory/team_memory.json` | Global | Team-wide state, decisions, agent notes |
| `projects/{slug}/memory/project_memory.json` | Per project | Project goals, decisions, context |

Agents read memory before acting and update it after completing work.

---

## CLI

```bash
# List all tasks
python cli/office.py list

# Create a new task
python cli/office.py new-task "Write a pricing model" --agent nora

# Assign a task to an agent
python cli/office.py assign 2026-04-01-pricing-model.md nora

# Mark a task as done
python cli/office.py done 2026-04-01-pricing-model.md

# Print team memory summary
python cli/office.py status
```

---

## License

MIT
