# AI Office

A multi-agent framework where multiple Claude Code agents work in parallel on tasks, with shared team memory and defined roles.

## What is this?

AI Office is a structured workspace for running multiple AI agents (Claude Code sessions) as a coordinated team. Each agent has a defined role, reads from shared memory, and works on tasks from a shared queue.

Think of it as a virtual office: agents clock in, check their task queue, do their work, update the shared log, and clock out.

---

## Folder Structure

```
ai-office/
├── agents/          # Role definitions for each agent
├── memory/          # Shared team memory (human + machine readable)
├── tasks/
│   ├── backlog/     # Tasks waiting to be assigned
│   ├── active/      # Tasks currently being worked on
│   └── completed/   # Finished tasks
├── projects/        # Longer-lived project workspaces
├── cli/
│   └── office.py   # CLI for managing tasks and agents
├── dashboard/
│   └── index.html  # Browser dashboard (requires local server)
├── CLAUDE.md        # Entry point for any Claude Code agent
└── README.md
```

---

## Agents

| Agent | Role |
|---|---|
| **orchestrator** | Routes tasks, maintains memory, reviews completed work |
| **developer** | Writes code, runs tests, commits to git |
| **researcher** | Gathers information, writes research notes |

### Adding a New Agent

1. Create `agents/<name>.md` following the structure of an existing agent file
2. Define: Name & Role, Responsibilities, Tools Available, How to Read/Write Memory, Behavior Rules
3. Add the agent name to `VALID_AGENTS` in `cli/office.py`

---

## How Memory Works

All agents share two memory files:

| File | Purpose |
|---|---|
| `memory/team_memory.md` | Human-readable log — easy to read and edit manually |
| `memory/team_memory.json` | Machine-readable state — loaded by agents at startup |

### Memory Sections

- **Project Status** — current phase and summary
- **Active Decisions** — constraints or choices that affect all agents
- **Recent Updates** — timestamped log of what happened
- **Agent Notes** — per-agent status messages

Agents must read memory before acting and update it after completing any task.

---

## CLI Usage

Run from the `cli/` directory or from anywhere using a full path:

```bash
# Create a new task in the backlog
python cli/office.py new-task "Add login endpoint" --agent developer

# Assign a backlog task to an agent (moves to tasks/active/)
python cli/office.py assign 2026-03-27-add-login-endpoint.md developer

# Mark a task as done (moves to tasks/completed/)
python cli/office.py done 2026-03-27-add-login-endpoint.md

# Print current memory summary
python cli/office.py status

# List all agents and their roles
python cli/office.py agents
```

---

## Dashboard

Open `dashboard/index.html` in a browser while serving the project locally:

```bash
python -m http.server 8000
# then open http://localhost:8000/dashboard/
```

The dashboard reads `memory/team_memory.json` and displays project status, active decisions, recent updates, and agent notes.

---

## Starting an Agent Session

Any Claude Code agent opening this repo should start by reading `CLAUDE.md`. It instructs the agent to:

1. Load `memory/team_memory.json`
2. Identify their role from `agents/`
3. Pick up assigned work from `tasks/active/`
4. Update memory after completing work

---

## License

MIT
