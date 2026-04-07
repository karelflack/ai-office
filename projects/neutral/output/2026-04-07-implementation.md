# Implementation — Markdown-to-HTML Converter CLI

**Agent:** arve  
**Date:** 2026-04-07  
**Project:** neutral

---

## Upstream outputs read

- `projects/neutral/output/2026-04-07-system-architecture.md` (bjorn)

---

## What was built

Full implementation of the `md2html` CLI tool, following bjorn's architecture spec exactly.

### Deliverable

`projects/neutral/output/md2html/` — complete, runnable Python package.

```
md2html/
├── pyproject.toml
├── README.md
├── md2html/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── reader.py
│   ├── parser.py
│   ├── renderer.py
│   ├── writer.py
│   ├── watcher.py
│   └── themes/
│       ├── __init__.py
│       ├── default.css
│       ├── dark.css
│       └── github.css
└── tests/
    ├── test_cli.py         (11 tests)
    ├── test_parser.py      (13 tests)
    ├── test_reader.py      (3 tests)
    ├── test_renderer.py    (5 tests)
    ├── test_themes.py      (5 tests)
    └── test_writer.py      (3 tests)
```

### Test results

```
40 passed in 0.08s
```

All 40 tests pass on Python 3.14.3.

---

## Key implementation decisions

### Theme loading via `importlib.resources`

Themes are plain `.css` files inside the `md2html/themes/` package directory, loaded with `importlib.resources.files()`. No path hacks, no `__file__` manipulation — works correctly when installed as a wheel.

### Title derived from filename

The `--output` flag defaults to `{input_stem}.html` in the input file's directory (not cwd). The `<title>` tag in the output HTML is derived from the input filename — hyphens and underscores replaced with spaces, title-cased. No metadata parsing needed.

### Watch mode isolation

`watcher.py` only imports `watchdog` inside the `watch()` function body, so importing the module doesn't fail if watchdog is absent. The CLI catches `ImportError` from watchdog and emits a clean install instruction.

### mistune plugins enabled

Parser enables `strikethrough`, `table`, `url`, and `task_lists` plugins — covering the most common GFM features without any non-stdlib dependencies beyond mistune itself.

---

## How to run

```bash
# Install
pip install -e ".[watch]"

# Convert
md2html --input README.md

# With dark theme
md2html --input notes.md --theme dark

# Watch mode
md2html --input notes.md --watch

# Run tests
pytest
```
