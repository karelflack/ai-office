"""Team memory and persistent run state."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_FILE = BASE_DIR / "memory" / "team_memory.json"
RUNS_DIR = BASE_DIR / "runs"


def read_memory() -> dict:
    return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))


def read_project_memory(slug: str) -> dict:
    p = BASE_DIR / "projects" / slug / "memory" / "project_memory.json"
    if not p.exists():
        raise FileNotFoundError(f"Project memory not found: {slug}")
    return json.loads(p.read_text(encoding="utf-8"))


def _run_path(task_id: str, project_slug: str = None) -> Path:
    if project_slug:
        return RUNS_DIR / project_slug / f"{task_id}.json"
    return RUNS_DIR / f"{task_id}.json"


def write_run(task_id: str, lines: list, done: bool, project_slug: str = None) -> None:
    """Persist run output to runs/{project_slug}/{task_id}.json."""
    p = _run_path(task_id, project_slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"lines": lines, "done": done}), encoding="utf-8")


def read_run(task_id: str, project_slug: str = None) -> dict:
    """Return {"lines": [...], "done": bool}, or empty defaults if not found."""
    p = _run_path(task_id, project_slug)
    if not p.exists():
        return {"lines": [], "done": False}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"lines": [], "done": False}


def list_runs(project_slug: str = None) -> dict:
    """Return {"running": [...], "done": [...], "web_search": [...]} task IDs."""
    run_dir = (RUNS_DIR / project_slug) if project_slug else RUNS_DIR
    run_dir.mkdir(parents=True, exist_ok=True)
    running, done, web_search = [], [], []
    for f in run_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            is_done = data.get("done", False)
            (done if is_done else running).append(f.stem)
            # Flag tasks that have used web_search and are still running
            if not is_done:
                lines = data.get("lines", [])
                if any("[OpenAI]" in l for l in lines):
                    web_search.append(f.stem)
        except Exception:
            pass
    return {"running": running, "done": done, "web_search": web_search}
