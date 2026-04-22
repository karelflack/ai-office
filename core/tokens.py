"""SQLite-backed token usage tracking + Claude Code JSONL parsing."""

import json
import sqlite3
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TOKENS_DB = BASE_DIR / "tokens.db"


def init_db() -> None:
    """Create the token_usage table if it doesn't exist."""
    con = sqlite3.connect(str(TOKENS_DB))
    con.execute("""
        CREATE TABLE IF NOT EXISTS token_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER NOT NULL,
            project TEXT,
            agent TEXT,
            task TEXT,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            cache_read_tokens INTEGER DEFAULT 0,
            cache_creation_tokens INTEGER DEFAULT 0,
            cost_usd REAL DEFAULT 0
        )
    """)
    con.commit()
    con.close()


def read_claude_code_usage() -> dict:
    """Parse token usage from Claude Code's local JSONL conversation files."""
    project_key = str(BASE_DIR).replace("/", "-")
    claude_dir = Path.home() / ".claude" / "projects" / project_key
    totals = {"input_tokens": 0, "output_tokens": 0,
              "cache_read_tokens": 0, "cache_creation_tokens": 0}
    try:
        for jsonl_path in claude_dir.rglob("*.jsonl"):
            try:
                with open(jsonl_path, encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if '"usage"' not in line:
                            continue
                        try:
                            entry = json.loads(line)
                            msg   = entry.get("message", {})
                            usage = msg.get("usage") if isinstance(msg, dict) else None
                            if not usage:
                                continue
                            totals["input_tokens"]          += usage.get("input_tokens", 0)
                            totals["output_tokens"]         += usage.get("output_tokens", 0)
                            totals["cache_read_tokens"]     += usage.get("cache_read_input_tokens", 0)
                            totals["cache_creation_tokens"] += usage.get("cache_creation_input_tokens", 0)
                        except Exception:
                            pass
            except Exception:
                pass
    except Exception:
        pass
    inp, out = totals["input_tokens"], totals["output_tokens"]
    cr,  cc  = totals["cache_read_tokens"], totals["cache_creation_tokens"]
    totals["cost_usd"] = round(
        (inp / 1_000_000) * 3.0  + (out / 1_000_000) * 15.0 +
        (cr  / 1_000_000) * 0.30 + (cc  / 1_000_000) * 3.75, 4)
    return totals


def record_usage(project: str, agent: str, task: str,
                 input_tokens: int, output_tokens: int,
                 cache_read_tokens: int, cache_creation_tokens: int,
                 cost_usd: float) -> None:
    """Insert a single token-usage row. Silent on failure."""
    try:
        con = sqlite3.connect(str(TOKENS_DB))
        con.execute(
            "INSERT INTO token_usage (ts, project, agent, task, input_tokens, output_tokens, "
            "cache_read_tokens, cache_creation_tokens, cost_usd) VALUES (?,?,?,?,?,?,?,?,?)",
            (int(time.time()), project, agent, task,
             input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens, cost_usd)
        )
        con.commit()
        con.close()
    except Exception:
        pass


def query(project_filter: str | None = None) -> dict:
    """Return {runs, totals} for the dashboard tokens view. Caller adds claude_code usage."""
    con = sqlite3.connect(str(TOKENS_DB))
    con.row_factory = sqlite3.Row
    try:
        if project_filter:
            runs = con.execute(
                "SELECT * FROM token_usage WHERE project=? ORDER BY ts DESC LIMIT 100",
                (project_filter,)
            ).fetchall()
            totals = con.execute(
                "SELECT SUM(input_tokens) as input_tokens, SUM(output_tokens) as output_tokens, "
                "SUM(cache_read_tokens) as cache_read_tokens, SUM(cost_usd) as cost_usd "
                "FROM token_usage WHERE project=?",
                (project_filter,)
            ).fetchone()
        else:
            runs = con.execute(
                "SELECT * FROM token_usage ORDER BY ts DESC LIMIT 100"
            ).fetchall()
            totals = con.execute(
                "SELECT SUM(input_tokens) as input_tokens, SUM(output_tokens) as output_tokens, "
                "SUM(cache_read_tokens) as cache_read_tokens, SUM(cost_usd) as cost_usd "
                "FROM token_usage"
            ).fetchone()
    finally:
        con.close()
    return {
        "runs": [dict(r) for r in runs],
        "totals": dict(totals) if totals else {},
    }
