# md2html

Convert a Markdown file to a self-contained, styled HTML file.

The output is a single `.html` file with all CSS embedded — no external stylesheets, no CDN dependencies. Drop it anywhere and it will render correctly.

---

## Installation

```bash
# Base install (no watch mode)
pip install .

# With watch mode support
pip install ".[watch]"
```

Requires Python 3.11 or newer.

---

## Usage

```
md2html --input <file.md> [--output <file.html>] [--theme <name>] [--watch]
```

### Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--input` | `-i` | required | Path to source `.md` file |
| `--output` | `-o` | `<input>.html` in same directory | Output path |
| `--theme` | `-t` | `default` | Theme: `default`, `dark`, `github` |
| `--watch` | `-w` | off | Rebuild on every save |

### Examples

```bash
# Basic conversion
md2html --input README.md

# Custom output path
md2html --input docs/guide.md --output dist/guide.html

# Dark theme
md2html --input notes.md --theme dark

# GitHub-style rendering
md2html -i spec.md -t github

# Watch mode (rebuild on save)
md2html --input notes.md --watch
```

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Input file not found / watchdog not installed |
| `2` | Parse or render error |
| `3` | Write permission error |

---

## Themes

| Name | Description |
|------|-------------|
| `default` | Clean light theme with system fonts and subtle borders |
| `dark` | Dark background (`#0d1117`) with light text, GitHub-inspired dark palette |
| `github` | Mirrors GitHub's Markdown rendering style (light) |

---

## Development

```bash
# Install in editable mode with test dependencies
pip install -e ".[watch]"
pip install pytest

# Run tests
pytest
```

---

## Architecture

The tool is organised into small, single-responsibility modules:

```
md2html/
├── __main__.py    # python -m md2html entry point
├── cli.py         # CLI argument parsing (click)
├── reader.py      # reads .md file → string
├── parser.py      # mistune wrapper → HTML fragment
├── renderer.py    # Jinja2 template → full HTML document
├── writer.py      # writes HTML to disk
├── watcher.py     # watchdog loop for --watch mode
└── themes/        # embedded CSS files
    ├── default.css
    ├── dark.css
    └── github.css
```

See `projects/neutral/output/2026-04-07-system-architecture.md` for the full architecture decision record.
