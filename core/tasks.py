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


def _get_task_dirs(project_slug: str = None) -> dict:
    """Return task directories — project-scoped if slug given, global otherwise."""
    if project_slug:
        base = BASE_DIR / "projects" / project_slug / "tasks"
        return {
            "backlog":   base / "backlog",
            "active":    base / "active",
            "completed": base / "completed",
        }
    return TASK_DIRS


def find_task(filename: str, project_slug: str = None):
    """Search backlog → active → completed. Returns (bucket, Path) or (None, None)."""
    for bucket, directory in _get_task_dirs(project_slug).items():
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


def create_task(title: str, agent: str, description: str = "", project_slug: str = None) -> str:
    """Write a new task file to backlog/. Returns the filename."""
    today = date.today().isoformat()
    filename = f"{today}-{slugify(title)}.md"
    dirs = _get_task_dirs(project_slug)
    backlog_dir = dirs["backlog"]
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


def assign_task(filename: str, agent: str, project_slug: str = None) -> None:
    """Move task to active/ and update Agent + Status fields."""
    bucket, src = find_task(filename, project_slug)
    if src is None:
        raise FileNotFoundError(f"Task not found: {filename}")

    dirs = _get_task_dirs(project_slug)
    active_dir = dirs["active"]
    active_dir.mkdir(parents=True, exist_ok=True)
    dest = active_dir / filename

    content = src.read_text(encoding="utf-8")
    content = update_markdown_fields(content, agent=agent, status="active")
    dest.write_text(content, encoding="utf-8")
    if src != dest:
        src.unlink()


def complete_task(filename: str, project_slug: str = None) -> None:
    """Move task to completed/ and update Status field."""
    bucket, src = find_task(filename, project_slug)
    if src is None:
        raise FileNotFoundError(f"Task not found: {filename}")

    dirs = _get_task_dirs(project_slug)
    completed_dir = dirs["completed"]
    completed_dir.mkdir(parents=True, exist_ok=True)
    dest = completed_dir / filename

    content = src.read_text(encoding="utf-8")
    content = update_markdown_fields(content, status="completed")
    dest.write_text(content, encoding="utf-8")
    if src != dest:
        src.unlink()


def list_tasks(project_slug: str = None) -> dict:
    """Return {"backlog": [...], "active": [...], "completed": [...]} sorted filenames."""
    result = {}
    for bucket, directory in _get_task_dirs(project_slug).items():
        directory.mkdir(parents=True, exist_ok=True)
        result[bucket] = sorted(
            f.name for f in directory.iterdir()
            if f.is_file() and f.name.endswith(".md")
        )
    return result
