"""Joke loading, in-process indexing, and selection logic.

Jokes are loaded once at startup from jokes.json. An O(1) dict index is built
keyed by joke id. All selection and filtering is then served from memory.
"""

import json
import random
from pathlib import Path
from typing import Optional

_jokes: list[dict] = []
_index: dict[int, dict] = {}

_DATA_PATH = Path(__file__).parent.parent / "data" / "jokes.json"


def load_jokes(path: Path = _DATA_PATH) -> None:
    """Load jokes from disk and build the ID index.

    Called once via FastAPI lifespan hook. Raises on missing or empty file
    so the app fails fast at startup rather than returning 500s at runtime.
    """
    global _jokes, _index
    with open(path) as fh:
        data = json.load(fh)
    if not isinstance(data, list) or not data:
        raise ValueError(f"jokes file at {path} must be a non-empty JSON array")
    _jokes = data
    _index = {joke["id"]: joke for joke in _jokes}


def get_random_joke() -> Optional[dict]:
    """Return a random joke, or None if the dataset is empty."""
    if not _jokes:
        return None
    return random.choice(_jokes)


def get_joke_by_id(joke_id: int) -> Optional[dict]:
    """Return the joke with the given ID, or None if not found."""
    return _index.get(joke_id)


def get_all_jokes(category: Optional[str] = None) -> list[dict]:
    """Return all jokes, optionally filtered by category (case-insensitive).

    Returns an empty list if no jokes match — never raises 404.
    """
    if category is None:
        return list(_jokes)
    needle = category.lower()
    return [j for j in _jokes if j["category"].lower() == needle]
