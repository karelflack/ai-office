"""Canonical agent registry for the ai-office framework."""

VALID_AGENTS = {
    "orchestrator", "arve", "bjorn", "dag", "else", "frode",
    "halvard", "guro", "jorunn", "ingrid", "knut", "laila",
    "magnus", "nora", "odd", "per",
}


def is_valid(agent: str) -> bool:
    return agent in VALID_AGENTS
