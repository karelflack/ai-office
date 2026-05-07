"""Canonical agent registry for the ai-office framework.

Agent identity is filename-based: every `agents/{id}.md` file is a valid agent.
The original 16 are flagged as built-in (read-only — uploaded agents can be
deleted; built-ins cannot).
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
AGENTS_DIR = BASE_DIR / "agents"

# Lowercase letters/digits, optional dashes inside. Same shape as project slugs.
# Required because macOS filesystems are case-insensitive, so we can't rely on
# `Path.exists()` to reject "ARVE.md" — the regex enforces case-sensitivity.
AGENT_ID_RE = re.compile(r"^[a-z][a-z0-9-]{0,49}$")

# The original 16. Used to mark agents as built-in / read-only in the UI and
# to know which agents have hard-coded peer-review pairings.
BUILTIN_AGENTS = frozenset({
    "orchestrator", "arve", "bjorn", "dag", "else", "frode",
    "halvard", "guro", "jorunn", "ingrid", "knut", "laila",
    "magnus", "nora", "odd", "per",
})

# Canon role blurbs — used in the kickoff prompt and the dashboard UI.
# Short enough to fit next to a name in a list. Custom agents fall back to
# parsing their `.md` file for the first non-heading line.
BUILTIN_DESC = {
    "orchestrator": "plans and assigns work to the team",
    "bjorn":   "system architecture, tech stack, data models",
    "arve":    "writes code, scaffolds projects, implements features",
    "dag":     "DevOps, Docker, CI/CD pipelines, deployment",
    "magnus":  "legal, compliance, GDPR, PCI, privacy policy",
    "ingrid":  "UI/UX design, wireframes, user flows",
    "else":    "research, market analysis, competitor landscape",
    "jorunn":  "brand identity, naming, tone of voice",
    "halvard": "growth strategy, acquisition channels, onboarding",
    "frode":   "sprint planning, backlog breakdown, story points",
    "nora":    "pricing model, revenue streams, unit economics",
    "guro":    "social media content, launch copy, threads",
    "knut":    "project milestones, timeline, progress tracking",
    "laila":   "customer support docs, onboarding guides, FAQs",
    "odd":     "API testing, endpoint validation, test suites",
    "per":     "performance benchmarking, load testing, optimization",
}


def _scan_disk() -> set:
    """Return the set of agent ids that have an `agents/{id}.md` file on disk."""
    if not AGENTS_DIR.exists():
        return set()
    return {p.stem for p in AGENTS_DIR.glob("*.md") if p.is_file()}


# Back-compat: some callers import `VALID_AGENTS` directly. We keep the name
# but make it a module-level snapshot of the disk state at import time.
# Validation routines below do a fresh disk read so newly-uploaded agents work
# without a server restart.
VALID_AGENTS = BUILTIN_AGENTS | _scan_disk()


def is_valid(agent: str) -> bool:
    """True if agent is a built-in id OR `agents/{agent}.md` exists on disk."""
    if not agent or not AGENT_ID_RE.match(agent):
        return False
    if agent in BUILTIN_AGENTS:
        return True
    return (AGENTS_DIR / f"{agent}.md").exists()


def list_all() -> list:
    """Return every available agent as a list of dicts. Includes a short role
    blurb so the dashboard can show it next to the name."""
    on_disk = _scan_disk()
    ids = sorted(BUILTIN_AGENTS | on_disk)
    out = []
    for a in ids:
        out.append({
            "id": a,
            "builtin": a in BUILTIN_AGENTS,
            "exists": a in on_disk,
            "role": role(a),
        })
    return out


def read_agent(agent: str) -> str:
    """Return the raw markdown of `agents/{agent}.md`."""
    p = AGENTS_DIR / f"{agent}.md"
    if not p.exists():
        raise FileNotFoundError(f"Agent not found: {agent}")
    return p.read_text(encoding="utf-8")


def role(agent: str) -> str:
    """Return a one-line role blurb for an agent. Built-ins use the canon
    table; custom agents fall back to the first non-heading line of their
    .md (or the line right after a `## Role` header if present)."""
    if agent in BUILTIN_DESC:
        return BUILTIN_DESC[agent]
    if not is_valid(agent):
        return ""
    try:
        text = read_agent(agent)
    except FileNotFoundError:
        return ""
    in_role = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("## Role"):
            in_role = True
            continue
        if in_role and s and not s.startswith("#"):
            return s[:140]
        if not in_role and s and not s.startswith("#") and not s.startswith("---"):
            return s[:140]
    return ""
