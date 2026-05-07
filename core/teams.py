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
from core import skills as skill_registry

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


def create_team(name: str, description: str = "", deputies: list = None,
                skills: dict = None) -> dict:
    """Create a new team file. Returns the saved dict.

    `skills` is an optional `{agent_id: [skill_name, ...]}` map. Entries pointing
    at agents not in the team or skills not in the library are dropped silently
    — same self-healing model as deputies."""
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

    members = set(CANON_AGENTS) | set(cleaned)
    cleaned_skills = _clean_skills_map(skills, members)

    data = {
        "slug": slug,
        "name": name,
        "description": (description or "").strip(),
        "deputies": cleaned,
        "skills": cleaned_skills,
        "created": date.today().isoformat(),
    }
    _team_file(slug).write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def update_team(slug: str, name: str = None, description: str = None,
                deputies: list = None, skills: dict = None) -> dict:
    """Patch an existing team in place. Any field passed as None is left alone."""
    data = get_team(slug)
    if name is not None:
        nm = name.strip()
        if not nm:
            raise ValueError("Team name cannot be empty")
        data["name"] = nm
    if description is not None:
        data["description"] = description.strip()
    if deputies is not None:
        cleaned = []
        seen = set()
        for a in deputies:
            a = str(a).strip().lower()
            if a in CANON_AGENTS or not a or not agent_registry.is_valid(a):
                continue
            if a not in seen:
                cleaned.append(a); seen.add(a)
        data["deputies"] = cleaned
    members = set(CANON_AGENTS) | set(data.get("deputies") or [])
    if skills is not None:
        data["skills"] = _clean_skills_map(skills, members)
    else:
        # Re-clean stored skills against current member set so a removed deputy
        # also drops their skill assignments.
        data["skills"] = _clean_skills_map(data.get("skills") or {}, members)
    _team_file(slug).write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def _clean_skills_map(skills: dict, members: set) -> dict:
    """Drop unknown agents and unknown skills. Preserve order."""
    out: dict = {}
    if not isinstance(skills, dict):
        return out
    for agent_id, skill_list in skills.items():
        agent_id = str(agent_id).strip().lower()
        if agent_id not in members:
            continue
        if not isinstance(skill_list, list):
            continue
        cleaned = []
        seen = set()
        for s in skill_list:
            s = str(s).strip().lower()
            if not s or s in seen:
                continue
            if not skill_registry.exists(s):
                continue
            cleaned.append(s); seen.add(s)
        if cleaned:
            out[agent_id] = cleaned
    return out


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


def skills_for_agent(team: dict, agent_id: str) -> list:
    """Return the live skill names attached to `agent_id` on this team.
    Skills whose .md has been deleted are filtered out — never silent ghosts."""
    raw = (team.get("skills") or {}).get(agent_id) or []
    return [s for s in raw if skill_registry.exists(s)]


def all_attached_skills(team: dict) -> dict:
    """Self-healed `{agent_id: [skill_name, ...]}` for the whole team —
    only agents currently in the team, only skills currently on disk."""
    members = set(all_agents_in_team(team))
    out: dict = {}
    for agent_id, names in (team.get("skills") or {}).items():
        if agent_id not in members:
            continue
        live = [s for s in (names or []) if skill_registry.exists(s)]
        if live:
            out[agent_id] = live
    return out
