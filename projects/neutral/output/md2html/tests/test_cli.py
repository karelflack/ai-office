import pytest
from pathlib import Path
from click.testing import CliRunner
from md2html.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_md(tmp_path):
    f = tmp_path / "sample.md"
    f.write_text("# Hello\n\nThis is a **test**.\n", encoding="utf-8")
    return f


def test_basic_conversion(runner, sample_md):
    result = runner.invoke(main, ["--input", str(sample_md)])
    assert result.exit_code == 0
    out = sample_md.with_suffix(".html")
    assert out.exists()
    html = out.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html
    assert "<h1>" in html
    assert "Hello" in html


def test_explicit_output_path(runner, sample_md, tmp_path):
    out = tmp_path / "custom.html"
    result = runner.invoke(main, ["--input", str(sample_md), "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_theme_default(runner, sample_md):
    result = runner.invoke(main, ["--input", str(sample_md), "--theme", "default"])
    assert result.exit_code == 0


def test_theme_dark(runner, sample_md):
    result = runner.invoke(main, ["--input", str(sample_md), "--theme", "dark"])
    assert result.exit_code == 0
    out = sample_md.with_suffix(".html")
    html = out.read_text(encoding="utf-8")
    assert "background" in html


def test_theme_github(runner, sample_md):
    result = runner.invoke(main, ["--input", str(sample_md), "--theme", "github"])
    assert result.exit_code == 0


def test_invalid_theme(runner, sample_md):
    result = runner.invoke(main, ["--input", str(sample_md), "--theme", "neon"])
    assert result.exit_code != 0


def test_missing_input_file(runner, tmp_path):
    result = runner.invoke(main, ["--input", str(tmp_path / "missing.md")])
    assert result.exit_code != 0


def test_output_filename_printed(runner, sample_md):
    result = runner.invoke(main, ["--input", str(sample_md)])
    assert "[built]" in result.output
    assert ".html" in result.output


def test_default_output_same_dir_as_input(runner, sample_md):
    runner.invoke(main, ["--input", str(sample_md)])
    expected = sample_md.with_suffix(".html")
    assert expected.exists()


def test_short_flags(runner, sample_md, tmp_path):
    out = tmp_path / "out.html"
    result = runner.invoke(main, ["-i", str(sample_md), "-o", str(out), "-t", "dark"])
    assert result.exit_code == 0
    assert out.exists()


def test_html_is_self_contained(runner, sample_md):
    runner.invoke(main, ["--input", str(sample_md)])
    html = sample_md.with_suffix(".html").read_text(encoding="utf-8")
    assert "<style>" in html
    assert "</style>" in html
    # No external stylesheet links
    assert 'rel="stylesheet"' not in html
