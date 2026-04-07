import pytest
from md2html.themes import load, available


def test_load_default():
    css = load("default")
    assert isinstance(css, str)
    assert len(css) > 100


def test_load_dark():
    css = load("dark")
    assert "background" in css


def test_load_github():
    css = load("github")
    assert "font-family" in css


def test_available_returns_three_themes():
    themes = available()
    assert set(themes) == {"default", "dark", "github"}


def test_unknown_theme_raises():
    with pytest.raises(ValueError, match="Unknown theme"):
        load("neon")
