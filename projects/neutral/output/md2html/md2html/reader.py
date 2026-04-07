from pathlib import Path


def read(path: Path) -> str:
    """Read a Markdown file from disk and return its contents as a string."""
    return path.read_text(encoding="utf-8")
