from jinja2 import Environment, BaseLoader

_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ title }}</title>
  <style>
{{ css }}
  </style>
</head>
<body>
  <main class="md-body">
{{ html_fragment }}
  </main>
</body>
</html>
"""

_env = Environment(loader=BaseLoader(), autoescape=False)
_tmpl = _env.from_string(_TEMPLATE)


def render(fragment: str, title: str, css: str) -> str:
    """Assemble a full HTML document from an HTML fragment, page title, and CSS."""
    return _tmpl.render(title=title, css=css, html_fragment=fragment)
