from pathlib import Path


def write(html: str, path: Path) -> None:
    """Write an HTML string to the given output path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
