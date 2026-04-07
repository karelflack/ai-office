from md2html.renderer import render


def test_renders_full_html_document():
    html = render("<p>Hello</p>", title="Test", css="body { color: red; }")
    assert "<!DOCTYPE html>" in html
    assert "<html" in html
    assert "<title>Test</title>" in html
    assert "<p>Hello</p>" in html
    assert "body { color: red; }" in html


def test_title_is_set():
    html = render("", title="My Document", css="")
    assert "<title>My Document</title>" in html


def test_css_is_embedded():
    css = "h1 { font-size: 2rem; }"
    html = render("", title="x", css=css)
    assert css in html


def test_fragment_inside_main():
    html = render("<h1>Hi</h1>", title="T", css="")
    assert "<main" in html
    assert "<h1>Hi</h1>" in html


def test_returns_string():
    assert isinstance(render("", "t", ""), str)
