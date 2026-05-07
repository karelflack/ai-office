"""Skill workspace — a skill is a markdown file describing a capability.

Stored as `skills/{name}.md`. Currently a passive library: skills are not yet
attached to agents. The UI lets users upload and browse them so the content
is in place when wiring is added later.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = BASE_DIR / "skills"

SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,49}$")


def _skill_file(name: str) -> Path:
    return SKILLS_DIR / f"{name}.md"


def list_skills() -> list:
    """Return every skill as `{name, size}` dicts, sorted by name."""
    if not SKILLS_DIR.exists():
        return []
    out = []
    for p in sorted(SKILLS_DIR.glob("*.md")):
        try:
            out.append({"name": p.stem, "size": p.stat().st_size})
        except Exception:
            continue
    return out


def read_skill(name: str) -> str:
    if not SKILL_NAME_RE.match(name or ""):
        raise FileNotFoundError(f"Invalid skill name: {name}")
    p = _skill_file(name)
    if not p.exists():
        raise FileNotFoundError(f"Skill not found: {name}")
    return p.read_text(encoding="utf-8")


def create_skill(name: str, body: str) -> dict:
    name = (name or "").strip().lower()
    if not SKILL_NAME_RE.match(name):
        raise ValueError(f"Invalid skill name: {name!r}")
    if not (body or "").strip():
        raise ValueError("Skill body is required")
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    if _skill_file(name).exists():
        raise ValueError(f"Skill already exists: {name}")
    _skill_file(name).write_text(body, encoding="utf-8")
    return {"name": name, "size": len(body.encode("utf-8"))}


def delete_skill(name: str) -> None:
    if not SKILL_NAME_RE.match(name or ""):
        return
    p = _skill_file(name)
    if p.exists():
        p.unlink()
