import pytest
from pathlib import Path
from md2html.reader import read


def test_read_returns_string(tmp_path):
    f = tmp_path / "sample.md"
    f.write_text("# Hello\n\nWorld", encoding="utf-8")
    result = read(f)
    assert isinstance(result, str)
    assert "# Hello" in result


def test_read_preserves_content(tmp_path):
    content = "# Title\n\nParagraph with **bold** and _italic_.\n"
    f = tmp_path / "doc.md"
    f.write_text(content, encoding="utf-8")
    assert read(f) == content


def test_read_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        read(tmp_path / "nonexistent.md")
