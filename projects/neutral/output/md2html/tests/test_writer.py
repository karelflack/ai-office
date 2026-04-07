import pytest
from pathlib import Path
from md2html.writer import write


def test_writes_file(tmp_path):
    out = tmp_path / "output.html"
    write("<h1>Hi</h1>", out)
    assert out.exists()
    assert out.read_text(encoding="utf-8") == "<h1>Hi</h1>"


def test_creates_parent_directories(tmp_path):
    out = tmp_path / "sub" / "dir" / "output.html"
    write("<p>ok</p>", out)
    assert out.exists()


def test_overwrites_existing_file(tmp_path):
    out = tmp_path / "output.html"
    out.write_text("old content", encoding="utf-8")
    write("new content", out)
    assert out.read_text(encoding="utf-8") == "new content"
