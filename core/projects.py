"""Project workspace management — each project has its own tasks, memory, and output."""

import json
from datetime import date
from pathlib import Path

from core.tasks import slugify

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = BASE_DIR / "projects"


def project_dir(slug: str) -> Path:
    return PROJECTS_DIR / slug


def project_task_dirs(slug: str) -> dict:
    base = project_dir(slug) / "tasks"
    return {
        "backlog":   base / "backlog",
        "active":    base / "active",
        "completed": base / "completed",
    }


def project_memory_file(slug: str) -> Path:
    return project_dir(slug) / "memory" / "project_memory.json"


def list_projects() -> list:
    """Return list of project dicts sorted alphabetically."""
    if not PROJECTS_DIR.exists():
        return []
    result = []
    for p in sorted(PROJECTS_DIR.iterdir()):
        json_file = p / "project.json"
        if p.is_dir() and json_file.exists():
            try:
                result.append(json.loads(json_file.read_text(encoding="utf-8")))
            except Exception:
                pass
    return result


def get_project(slug: str) -> dict:
    p = project_dir(slug) / "project.json"
    if not p.exists():
        raise FileNotFoundError(f"Project not found: {slug}")
    return json.loads(p.read_text(encoding="utf-8"))


def create_project(name: str, description: str = "") -> str:
    """Create project directory structure. Returns the slug."""
    slug = slugify(name)
    p = project_dir(slug)
    if (p / "project.json").exists():
        raise ValueError(f"Project already exists: {slug}")

    for subdir in ["tasks/backlog", "tasks/active", "tasks/completed", "memory", "output"]:
        (p / subdir).mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()

    (p / "project.json").write_text(
        json.dumps({"name": name, "slug": slug, "description": description, "created": today}, indent=2),
        encoding="utf-8",
    )

    (p / "memory" / "project_memory.json").write_text(
        json.dumps({
            "project": name,
            "slug": slug,
            "description": description,
            "created": today,
            "agent_notes": {},
        }, indent=2),
        encoding="utf-8",
    )

    (p / "output" / "README.md").write_text(
        f"# {name} — Output\n\n"
        "| File | Description | Agent | Date |\n"
        "|------|-------------|-------|------|\n",
        encoding="utf-8",
    )

    return slug
