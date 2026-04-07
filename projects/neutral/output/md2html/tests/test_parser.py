from md2html.parser import parse


def test_heading_becomes_h1():
    html = parse("# Hello")
    assert "<h1>" in html
    assert "Hello" in html


def test_bold_text():
    html = parse("**bold**")
    assert "<strong>bold</strong>" in html


def test_italic_text():
    html = parse("_italic_")
    assert "<em>italic</em>" in html


def test_link():
    html = parse("[click](https://example.com)")
    assert 'href="https://example.com"' in html
    assert "click" in html


def test_code_inline():
    html = parse("`code`")
    assert "<code>" in html
    assert "code" in html


def test_code_block():
    html = parse("```python\nx = 1\n```")
    assert "<pre>" in html
    assert "x = 1" in html


def test_unordered_list():
    html = parse("- item one\n- item two")
    assert "<ul>" in html
    assert "item one" in html


def test_ordered_list():
    html = parse("1. first\n2. second")
    assert "<ol>" in html
    assert "first" in html


def test_blockquote():
    html = parse("> quoted text")
    assert "<blockquote>" in html
    assert "quoted text" in html


def test_table():
    md = "| A | B |\n|---|---|\n| 1 | 2 |"
    html = parse(md)
    assert "<table>" in html
    assert "<th>" in html or "<thead>" in html


def test_strikethrough():
    html = parse("~~crossed~~")
    assert "crossed" in html
    assert "<del>" in html


def test_returns_string():
    assert isinstance(parse("hello"), str)


def test_empty_string():
    result = parse("")
    assert isinstance(result, str)
