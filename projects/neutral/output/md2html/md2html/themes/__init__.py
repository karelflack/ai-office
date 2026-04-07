from importlib.resources import files

_AVAILABLE = {"default", "dark", "github"}


def load(name: str) -> str:
    """Return the CSS string for the given theme name."""
    if name not in _AVAILABLE:
        raise ValueError(
            f"Unknown theme '{name}'. Available themes: {', '.join(sorted(_AVAILABLE))}"
        )
    return (files(__name__) / f"{name}.css").read_text(encoding="utf-8")


def available() -> list[str]:
    return sorted(_AVAILABLE)
