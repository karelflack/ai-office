"""Task management — create, find, assign, complete, list tasks."""

import re
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TASKS_DIR = BASE_DIR / "tasks"
TASK_DIRS = {
    "backlog":   TASKS_DIR / "backlog",
    "active":    TASKS_DIR / "active",
    "completed": TASKS_DIR / "completed",
}


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s_-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def find_task(filename: str):
    """Search backlog → active → completed. Returns (bucket, Path) or (None, None)."""
    for bucket, directory in TASK_DIRS.items():
        candidate = directory / filename
        if candidate.exists():
            return bucket, candidate
    return None, None


def update_markdown_fields(content: str, agent: str = None, status: str = None) -> str:
    if agent is not None:
        content = re.sub(
            r"^\*\*Agent:\*\*.*$", f"**Agent:** {agent}",
            content, flags=re.MULTILINE,
        )
    if status is not None:
        content = re.sub(
            r"^\*\*Status:\*\*.*$", f"**Status:** {status}",
            content, flags=re.MULTILINE,
        )
    return content


def create_task(title: str, agent: str, description: str = "") -> str:
    """Write a new task file to backlog/. Returns the filename."""
    today = date.today().isoformat()
    filename = f"{today}-{slugify(title)}.md"
    backlog_dir = TASK_DIRS["backlog"]
    backlog_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# {title}",
        "",
        f"**Agent:** {agent}",
        f"**Status:** backlog",
        f"**Created:** {today}",
        "",
    ]
    if description:
        lines += ["## Description", "", description, ""]

    (backlog_dir / filename).write_text("\n".join(lines), encoding="utf-8")
    return filename


def assign_task(filename: str, agent: str) -> None:
    """Move task to active/ and update Agent + Status fields."""
    bucket, src = find_task(filename)
    if src is None:
        raise FileNotFoundError(f"Task not found: {filename}")

    active_dir = TASK_DIRS["active"]
    active_dir.mkdir(parents=True, exist_ok=True)
    dest = active_dir / filename

    content = src.read_text(encoding="utf-8")
    content = update_markdown_fields(content, agent=agent, status="active")
    dest.write_text(content, encoding="utf-8")
    if src != dest:
        src.unlink()


def complete_task(filename: str) -> None:
    """Move task to completed/ and update Status field."""
    bucket, src = find_task(filename)
    if src is None:
        raise FileNotFoundError(f"Task not found: {filename}")

    completed_dir = TASK_DIRS["completed"]
    completed_dir.mkdir(parents=True, exist_ok=True)
    dest = completed_dir / filename

    content = src.read_text(encoding="utf-8")
    content = update_markdown_fields(content, status="completed")
    dest.write_text(content, encoding="utf-8")
    if src != dest:
        src.unlink()


def list_tasks() -> dict:
    """Return {"backlog": [...], "active": [...], "completed": [...]} sorted filenames."""
    result = {}
    for bucket, directory in TASK_DIRS.items():
        directory.mkdir(parents=True, exist_ok=True)
        result[bucket] = sorted(
            f.name for f in directory.iterdir()
            if f.is_file() and f.name.endswith(".md")
        )
    return result
