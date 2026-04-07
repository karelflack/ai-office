import sys
import time
from pathlib import Path

import click

from md2html import reader, parser, renderer, writer
from md2html.themes import load as load_theme, available as available_themes


def _build(input_path: Path, output_path: Path, theme: str) -> float:
    """Run the full parse → render → write pipeline. Returns elapsed seconds."""
    t0 = time.perf_counter()
    md = reader.read(input_path)
    fragment = parser.parse(md)
    css = load_theme(theme)
    title = input_path.stem.replace("-", " ").replace("_", " ").title()
    html = renderer.render(fragment, title=title, css=css)
    writer.write(html, output_path)
    return time.perf_counter() - t0


@click.command()
@click.option(
    "--input", "-i",
    "input_file",
    required=True,
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    help="Path to the source .md file.",
)
@click.option(
    "--output", "-o",
    "output_file",
    default=None,
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    help="Output path (default: same directory as input, .html extension).",
)
@click.option(
    "--theme", "-t",
    default="default",
    show_default=True,
    type=click.Choice(available_themes(), case_sensitive=False),
    help="Visual theme for the output HTML.",
)
@click.option(
    "--watch", "-w",
    is_flag=True,
    default=False,
    help="Rebuild whenever the input file is saved.",
)
@click.version_option(package_name="md2html")
def main(
    input_file: Path,
    output_file: Path | None,
    theme: str,
    watch: bool,
) -> None:
    """Convert a Markdown file to a self-contained, styled HTML file."""
    if output_file is None:
        output_file = input_file.with_suffix(".html")

    def build() -> None:
        try:
            elapsed = _build(input_file, output_file, theme)
            click.echo(f"[built] {output_file} ({elapsed:.2f}s)")
        except PermissionError as exc:
            click.echo(f"[error] Cannot write to {output_file}: {exc}", err=True)
            sys.exit(3)
        except Exception as exc:  # noqa: BLE001
            click.echo(f"[error] {exc}", err=True)
            sys.exit(2)

    build()

    if watch:
        click.echo(f"[watching] {input_file}  (Ctrl-C to stop)")
        try:
            from md2html.watcher import watch as run_watch
        except ImportError as exc:
            click.echo(str(exc), err=True)
            sys.exit(1)
        run_watch(input_file, build)
