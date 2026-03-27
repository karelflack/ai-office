#!/usr/bin/env python3
"""
office.py — CLI for managing the ai-office multi-agent framework.

Usage:
  python office.py new-task "<title>" --agent <role>
  python office.py assign <task-file> <agent>
  python office.py done <task-file>
  python office.py status
  python office.py agents
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_BACKLOG = ROOT / "tasks" / "backlog"
TASKS_ACTIVE = ROOT / "tasks" / "active"
TASKS_COMPLETED = ROOT / "tasks" / "completed"
MEMORY_JSON = ROOT / "memory" / "team_memory.json"
AGENTS_DIR = ROOT / "agents"

VALID_AGENTS = ["orchestrator", "developer", "researcher"]


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text


def new_task(title: str, agent: str) -> None:
    if agent not in VALID_AGENTS:
        print(f"Error: unknown agent '{agent}'. Valid agents: {', '.join(VALID_AGENTS)}")
        sys.exit(1)

    today = date.today().isoformat()
    slug = slugify(title)
    filename = f"{today}-{slug}.md"
    filepath = TASKS_BACKLOG / filename

    content = f"""# {title}

**Agent:** {agent}
**Status:** backlog
**Created:** {today}

## Description

_Add task description here._

## Acceptance Criteria

- [ ] _Define what done looks like._
"""
    filepath.write_text(content)
    print(f"Created: tasks/backlog/{filename}")


def assign(task_file: str, agent: str) -> None:
    if agent not in VALID_AGENTS:
        print(f"Error: unknown agent '{agent}'. Valid agents: {', '.join(VALID_AGENTS)}")
        sys.exit(1)

    src = TASKS_BACKLOG / task_file
    if not src.exists():
        src = TASKS_ACTIVE / task_file
    if not src.exists():
        print(f"Error: task file '{task_file}' not found in backlog or active.")
        sys.exit(1)

    content = src.read_text()
    content = re.sub(r"(\*\*Agent:\*\*\s*)[\w]+", f"**Agent:** {agent}", content)
    content = re.sub(r"(\*\*Status:\*\*\s*)[\w]+", "**Status:** active", content)

    dest = TASKS_ACTIVE / task_file
    dest.write_text(content)
    if src != dest:
        src.unlink()
    print(f"Assigned '{task_file}' to {agent} → tasks/active/")


def done(task_file: str) -> None:
    src = TASKS_ACTIVE / task_file
    if not src.exists():
        src = TASKS_BACKLOG / task_file
    if not src.exists():
        print(f"Error: task file '{task_file}' not found.")
        sys.exit(1)

    content = src.read_text()
    content = re.sub(r"(\*\*Status:\*\*\s*)[\w]+", "**Status:** completed", content)

    dest = TASKS_COMPLETED / task_file
    dest.write_text(content)
    src.unlink()
    print(f"Moved '{task_file}' → tasks/completed/")


def status() -> None:
    if not MEMORY_JSON.exists():
        print("Error: memory/team_memory.json not found.")
        sys.exit(1)

    memory = json.loads(MEMORY_JSON.read_text())

    ps = memory.get("project_status", {})
    print(f"\n=== Project Status ===")
    print(f"Phase:        {ps.get('phase', 'unknown')}")
    print(f"Last updated: {ps.get('last_updated', 'unknown')}")
    print(f"Summary:      {ps.get('summary', '')}")

    decisions = memory.get("active_decisions", [])
    print(f"\n=== Active Decisions ({len(decisions)}) ===")
    for d in decisions:
        print(f"  - {d}")

    updates = memory.get("recent_updates", [])
    print(f"\n=== Recent Updates ===")
    for u in updates[-5:]:
        print(f"  [{u.get('date', '?')}] {u.get('note', '')}")

    notes = memory.get("agent_notes", {})
    print(f"\n=== Agent Notes ===")
    for agent, note in notes.items():
        print(f"  {agent}: {note}")

    active = list(TASKS_ACTIVE.glob("*.md"))
    backlog = list(TASKS_BACKLOG.glob("*.md"))
    completed = list(TASKS_COMPLETED.glob("*.md"))
    print(f"\n=== Tasks ===")
    print(f"  Backlog:   {len(backlog)}")
    print(f"  Active:    {len(active)}")
    print(f"  Completed: {len(completed)}")
    print()


def agents() -> None:
    print("\n=== Agents ===")
    for agent_file in sorted(AGENTS_DIR.glob("*.md")):
        name = agent_file.stem
        lines = agent_file.read_text().splitlines()
        role_line = ""
        for i, line in enumerate(lines):
            if line.startswith("## Role") and i + 1 < len(lines):
                role_line = lines[i + 1].strip()
                break
        print(f"  {name:<20} {role_line}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="ai-office CLI — manage agents and tasks"
    )
    subparsers = parser.add_subparsers(dest="command")

    p_new = subparsers.add_parser("new-task", help="Create a new task in backlog")
    p_new.add_argument("title", help="Task title")
    p_new.add_argument("--agent", required=True, help="Agent role to assign")

    p_assign = subparsers.add_parser("assign", help="Move task to active and assign agent")
    p_assign.add_argument("task_file", help="Task filename (e.g. 2026-03-27-my-task.md)")
    p_assign.add_argument("agent", help="Agent role")

    p_done = subparsers.add_parser("done", help="Mark a task as completed")
    p_done.add_argument("task_file", help="Task filename")

    subparsers.add_parser("status", help="Print memory summary")
    subparsers.add_parser("agents", help="List agents and their roles")

    args = parser.parse_args()

    if args.command == "new-task":
        new_task(args.title, args.agent)
    elif args.command == "assign":
        assign(args.task_file, args.agent)
    elif args.command == "done":
        done(args.task_file)
    elif args.command == "status":
        status()
    elif args.command == "agents":
        agents()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
