"""Team memory and persistent run state."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_FILE = BASE_DIR / "memory" / "team_memory.json"
RUNS_DIR = BASE_DIR / "runs"


def read_memory() -> dict:
    return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))


def _run_path(task_id: str) -> Path:
    return RUNS_DIR / f"{task_id}.json"


def write_run(task_id: str, lines: list, done: bool) -> None:
    """Persist run output to runs/<task_id>.json."""
    RUNS_DIR.mkdir(exist_ok=True)
    _run_path(task_id).write_text(
        json.dumps({"lines": lines, "done": done}),
        encoding="utf-8",
    )


def read_run(task_id: str) -> dict:
    """Return {"lines": [...], "done": bool} for a run, or empty defaults."""
    p = _run_path(task_id)
    if not p.exists():
        return {"lines": [], "done": False}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"lines": [], "done": False}


def list_runs() -> dict:
    """Return {"running": [...], "done": [...]} task IDs from runs/ directory."""
    RUNS_DIR.mkdir(exist_ok=True)
    running, done = [], []
    for f in RUNS_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            (done if data.get("done") else running).append(f.stem)
        except Exception:
            pass
    return {"running": running, "done": done}
