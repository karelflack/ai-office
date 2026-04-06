"""
Loads jokes from data/jokes.json at module import time.
Returns a random joke, or None if the dataset is empty.
"""
import json
import random
from pathlib import Path

from app.models import Joke

_DATA_FILE = Path(__file__).parent.parent / "data" / "jokes.json"

_jokes: list[Joke] = []


def _load() -> list[Joke]:
    with open(_DATA_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    return [Joke(**item) for item in raw]


_jokes = _load()


def get_random_joke() -> Joke | None:
    if not _jokes:
        return None
    return random.choice(_jokes)
