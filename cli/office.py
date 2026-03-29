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
import sys
from pathlib import Path

# Allow importing core/ from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import agents as agent_registry
from core import memory as mem
from core import tasks as task_mgr

AGENTS_DIR = task_mgr.BASE_DIR / "agents"


def new_task(title: str, agent: str) -> None:
    if not agent_registry.is_valid(agent):
        print(f"Error: unknown agent '{agent}'. Valid agents: {', '.join(sorted(agent_registry.VALID_AGENTS))}")
        sys.exit(1)

    filename = task_mgr.create_task(title, agent)
    print(f"Created: tasks/backlog/{filename}")


def assign(task_file: str, agent: str) -> None:
    if not agent_registry.is_valid(agent):
        print(f"Error: unknown agent '{agent}'. Valid agents: {', '.join(sorted(agent_registry.VALID_AGENTS))}")
        sys.exit(1)

    try:
        task_mgr.assign_task(task_file, agent)
    except FileNotFoundError:
        print(f"Error: task file '{task_file}' not found in backlog or active.")
        sys.exit(1)

    print(f"Assigned '{task_file}' to {agent} → tasks/active/")


def done(task_file: str) -> None:
    try:
        task_mgr.complete_task(task_file)
    except FileNotFoundError:
        print(f"Error: task file '{task_file}' not found.")
        sys.exit(1)

    print(f"Moved '{task_file}' → tasks/completed/")


def status() -> None:
    try:
        memory = mem.read_memory()
    except FileNotFoundError:
        print("Error: memory/team_memory.json not found.")
        sys.exit(1)

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

    counts = task_mgr.list_tasks()
    print(f"\n=== Tasks ===")
    print(f"  Backlog:   {len(counts['backlog'])}")
    print(f"  Active:    {len(counts['active'])}")
    print(f"  Completed: {len(counts['completed'])}")
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
