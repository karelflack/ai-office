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
            "failed":    base / "failed",
        }
    return TASK_DIRS


def find_task(filename: str, project_slug: str = None):
    """Search backlog → active → completed → failed. Returns (bucket, Path) or (None, None)."""
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


def parse_depends_on(content: str) -> str | None:
    """Return the depends_on filename from task content, or None."""
    m = re.search(r"^\*\*depends_on:\*\*\s*(.+)$", content, re.MULTILINE)
    if m:
        val = m.group(1).strip()
        return val if val and val.lower() != "none" else None
    return None


def parse_model(content: str) -> str | None:
    """Return the model from task content, or None (falls back to default)."""
    m = re.search(r"^\*\*Model:\*\*\s*(.+)$", content, re.MULTILINE)
    return m.group(1).strip() if m else None


def create_task(title: str, agent: str, description: str = "", project_slug: str = None,
                depends_on: str = None, model: str = None) -> str:
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
    ]
    if model:
        lines.append(f"**Model:** {model}")
    if depends_on:
        lines.append(f"**depends_on:** {depends_on}")
    lines.append("")
    if description:
        lines += ["## Description", "", description, ""]

    (backlog_dir / filename).write_text("\n".join(lines), encoding="utf-8")
    return filename


def resolve_handoffs(completed_filename: str, project_slug: str = None) -> list:
    """After a task completes, activate any backlog tasks that were waiting on it.

    Returns list of filenames that were activated.
    """
    dirs = _get_task_dirs(project_slug)
    backlog_dir = dirs["backlog"]
    if not backlog_dir.exists():
        return []

    activated = []
    for f in backlog_dir.glob("*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            dep = parse_depends_on(content)
            if dep and dep == completed_filename:
                # Parse the agent from the waiting task
                m = re.search(r"^\*\*Agent:\*\*\s*(.+)$", content, re.MULTILINE)
                agent = m.group(1).strip() if m else "orchestrator"
                assign_task(f.name, agent, project_slug=project_slug)
                activated.append(f.name)
        except Exception:
            pass
    return activated


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


def fail_task(filename: str, reason: str = "", project_slug: str = None) -> None:
    """Move task to failed/ and update Status field."""
    bucket, src = find_task(filename, project_slug)
    dirs = _get_task_dirs(project_slug)
    failed_dir = dirs["failed"]
    failed_dir.mkdir(parents=True, exist_ok=True)
    dest = failed_dir / filename

    if src is not None:
        content = src.read_text(encoding="utf-8")
        content = update_markdown_fields(content, status="failed")
        if reason:
            content += f"\n\n## Failure Reason\n\n{reason}\n"
        dest.write_text(content, encoding="utf-8")
        if src != dest:
            src.unlink()
    elif not dest.exists():
        return  # nothing to do


def cascade_fail(failed_filename: str, project_slug: str = None,
                 _visited: set = None) -> list:
    """Mark all tasks that depend (directly or transitively) on failed_filename as failed.

    Returns list of filenames that were cascade-failed.
    """
    if _visited is None:
        _visited = set()
    if failed_filename in _visited:
        return []  # Cycle guard — stop recursion
    _visited.add(failed_filename)

    dirs = _get_task_dirs(project_slug)
    cascaded = []
    reason = f"Blocked: dependency `{failed_filename}` failed."

    for bucket_name in ("backlog", "active"):
        bucket_dir = dirs.get(bucket_name)
        if not bucket_dir or not bucket_dir.exists():
            continue
        for f in bucket_dir.glob("*.md"):
            try:
                content = f.read_text(encoding="utf-8")
                dep = parse_depends_on(content)
                if dep and dep == failed_filename:
                    fail_task(f.name, reason=reason, project_slug=project_slug)
                    cascaded.append(f.name)
                    cascaded.extend(cascade_fail(f.name, project_slug=project_slug,
                                                 _visited=_visited))
            except Exception:
                pass
    return cascaded


def list_tasks(project_slug: str = None) -> dict:
    """Return {"backlog": [...], "active": [...], "completed": [...], "failed": [...]} sorted filenames."""
    result = {}
    for bucket, directory in _get_task_dirs(project_slug).items():
        directory.mkdir(parents=True, exist_ok=True)
        result[bucket] = sorted(
            f.name for f in directory.iterdir()
            if f.is_file() and f.name.endswith(".md")
        )
    return result
