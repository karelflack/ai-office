import mistune


_md = mistune.create_markdown(
    plugins=["strikethrough", "table", "url", "task_lists"],
)


def parse(md: str) -> str:
    """Parse a Markdown string and return an HTML fragment."""
    return _md(md)
