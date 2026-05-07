"""Team workspace — a team is a curated set of deputy agents.

Stored as `teams/{slug}.json`:

    {
      "slug": "marketing",
      "name": "Marketing",
      "description": "Brand + growth focus",
      "deputies": ["jorunn", "halvard", "guro", "nora", "else"],
      "created": "2026-05-07"
    }

The skeleton is fixed for every team:
- orchestrator (always plans the work)
- bjorn (Phase 1 — foundation)
- arve  (Phase 2 — build)
- odd   (Phase 3 — verify)

Deputies have no fixed phase. At kickoff the orchestrator reads the project
description and decides — for each canon and deputy — whether they fire and
which phase they fire in. This pushes the routing decision to the smartest
part of the system, instead of asking the user to predict it.
"""

import json
import re
from datetime import date
from pathlib import Path

from core import agents as agent_registry

BASE_DIR = Path(__file__).resolve().parent.parent
TEAMS_DIR = BASE_DIR / "teams"

# Always-present skeleton. Cannot be removed, reordered, or moved.
CANON_AGENTS = ("orchestrator", "bjorn", "arve", "odd")
CANON_PHASE = {"bjorn": "1", "arve": "2", "odd": "3"}

TEAM_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,49}$")


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s_-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def _team_file(slug: str) -> Path:
    return TEAMS_DIR / f"{slug}.json"


def list_teams() -> list:
    """Return every team as a list of dicts, sorted by name."""
    if not TEAMS_DIR.exists():
        return []
    out = []
    for p in sorted(TEAMS_DIR.glob("*.json")):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue
    out.sort(key=lambda t: (t.get("name") or t.get("slug") or "").lower())
    return out


def get_team(slug: str) -> dict:
    p = _team_file(slug)
    if not p.exists():
        raise FileNotFoundError(f"Team not found: {slug}")
    return json.loads(p.read_text(encoding="utf-8"))


def create_team(name: str, description: str = "", deputies: list = None) -> dict:
    """Create a new team file. Returns the saved dict."""
    name = (name or "").strip()
    if not name:
        raise ValueError("Team name is required")

    slug = _slugify(name)
    if not TEAM_SLUG_RE.match(slug):
        raise ValueError(f"Could not derive valid slug from name: {name!r}")

    TEAMS_DIR.mkdir(parents=True, exist_ok=True)
    if _team_file(slug).exists():
        raise ValueError(f"Team already exists: {slug}")

    cleaned = []
    seen = set()
    for a in deputies or []:
        a = str(a).strip().lower()
        if a in CANON_AGENTS:
            # Canon agents are always present — never store them as deputies.
            continue
        if a and agent_registry.is_valid(a) and a not in seen:
            cleaned.append(a)
            seen.add(a)

    data = {
        "slug": slug,
        "name": name,
        "description": (description or "").strip(),
        "deputies": cleaned,
        "created": date.today().isoformat(),
    }
    _team_file(slug).write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def delete_team(slug: str) -> None:
    p = _team_file(slug)
    if p.exists():
        p.unlink()


def deputies_in_team(team: dict) -> list:
    """Return only the live deputies (orphans whose .md was deleted are dropped).
    Self-healing — saved teams never silently point at ghosts."""
    return [a for a in (team.get("deputies") or []) if agent_registry.is_valid(a)]


def all_agents_in_team(team: dict) -> list:
    """Canon (always) + live deputies."""
    return list(CANON_AGENTS) + deputies_in_team(team)
