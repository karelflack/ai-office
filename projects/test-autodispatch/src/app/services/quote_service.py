"""Quote loading, selection, and in-process caching.

Selection is deterministic by UTC day-of-year:
    index = (day_of_year - 1) % len(quotes)

This means every request on the same UTC date returns the same quote,
with no shared state and no cache-invalidation logic needed.
"""

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

_quotes: list[dict] = []
_cache: dict[str, dict] = {}

_DATA_PATH = Path(__file__).parent.parent / "data" / "quotes.json"


def load_quotes(path: Path = _DATA_PATH) -> None:
    """Load quotes from disk into module-level state.

    Called once at app startup via the FastAPI lifespan hook.
    Also called lazily by get_daily_quote if _quotes is empty.
    """
    global _quotes
    with open(path) as fh:
        data = json.load(fh)
    if not isinstance(data, list) or not data:
        raise ValueError(f"quotes file at {path} must be a non-empty JSON array")
    _quotes = data


def select_quote(quotes: list[dict], today: date) -> dict:
    """Pure function: pick a quote for a given date.

    Separated from I/O and cache so it is trivially unit-testable.
    """
    day_index = today.timetuple().tm_yday  # 1–366
    entry = quotes[(day_index - 1) % len(quotes)]
    return {
        "quote": entry["quote"],
        "author": entry["author"],
        "date": today.isoformat(),
    }


def get_daily_quote() -> Optional[dict]:
    """Return today's quote, loading from disk if needed and caching in-process."""
    if not _quotes:
        try:
            load_quotes()
        except Exception:
            return None

    today = datetime.now(timezone.utc).date()
    today_str = today.isoformat()

    if today_str not in _cache:
        _cache[today_str] = select_quote(_quotes, today)

    return _cache[today_str]
