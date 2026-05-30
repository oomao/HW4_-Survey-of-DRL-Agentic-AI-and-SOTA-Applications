"""
Render report.md to a self-contained report.html that prints cleanly to PDF.
Mirrors A_DRL_Survey/report/build_html.py in style for visual consistency.
"""

from __future__ import annotations

import re
from pathlib import Path

import markdown


HERE = Path(__file__).resolve().parent
SRC = HERE / "report.md"
OUT = HERE / "report.html"


CSS = r"""
:root {
  --fg: #0f172a;
  --muted: #64748b;
  --bg: #ffffff;
  --accent: #0ea5e9;
  --border: #cbd5e1;
  --code-bg: #f1f5f9;
}
html { scroll-behavior: smooth; }
body {
  font-family: "Times New Roman", "Songti TC", "PMingLiU", "Microsoft JhengHei", serif;
  font-size: 11pt;
  line-height: 1.55;
  color: var(--fg);
  background: var(--bg);
  max-width: 850px;
  margin: 2em auto;
  padding: 0 1.5em 4em;
}
h1 { font-size: 1.9em; margin-top: 1.4em; border-bottom: 2px solid var(--accent); padding-bottom: .2em; }
h2 { font-size: 1.35em; margin-top: 1.8em; color: var(--accent); }
h3 { font-size: 1.1em; margin-top: 1.4em; }
h4 { font-size: 1.0em; margin-top: 1.2em; color: var(--muted); }
p, li { text-align: justify; }
ul, ol { padding-left: 1.4em; }
strong { color: #0c4a6e; }
code {
  font-family: "Consolas", "Menlo", "Courier New", monospace;
  background: var(--code-bg);
  padding: 0.15em 0.4em;
  border-radius: 3px;
  font-size: 0.93em;
}
pre {
  background: var(--code-bg);
  padding: 0.8em 1em;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.86em;
  line-height: 1.4;
  border-left: 3px solid var(--accent);
}
pre code { background: transparent; padding: 0; }
table { border-collapse: collapse; margin: 1em 0; width: 100%; font-size: 0.92em; }
th, td { border: 1px solid var(--border); padding: 6px 10px; vertical-align: top; text-align: left; }
th { background: #f8fafc; }
hr { border: none; border-top: 1px solid var(--border); margin: 2em 0; }
blockquote {
  border-left: 4px solid var(--accent);
  margin: 1em 0; padding: 0.4em 1em;
  color: var(--muted); background: var(--code-bg);
  border-radius: 0 6px 6px 0;
}
img { max-width: 100%; height: auto; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
@media print {
  body { margin: 0; max-width: none; padding: 0.6cm 0.9cm; font-size: 9pt; line-height: 1.3; }
  h1 { font-size: 1.5em; margin-top: 0.5em; }
  h2 { font-size: 1.18em; margin-top: 0.9em; page-break-after: avoid; }
  h3 { font-size: 1.02em; margin-top: 0.6em; page-break-after: avoid; }
  h4 { margin-top: 0.5em; }
  p, li { margin: 0.2em 0; }
  ul, ol { margin: 0.3em 0; }
  pre { font-size: 0.78em; padding: 0.5em 0.7em; line-height: 1.3; }
  table { font-size: 0.82em; }
  table, pre, blockquote { page-break-inside: avoid; }
  blockquote { margin: 0.5em 0; padding: 0.3em 0.8em; }
  a { color: var(--fg); text-decoration: none; }
}
"""


HTML = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>HW4-B · AI Harness — DRL Research Assistant</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""


def main():
    text = SRC.read_text(encoding="utf-8")
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    md = markdown.Markdown(
        extensions=["extra", "tables", "fenced_code", "footnotes", "toc", "sane_lists"],
        extension_configs={"toc": {"title": "Table of Contents", "toc_depth": "2-3"}},
    )
    body = md.convert(text)
    OUT.write_text(HTML.format(css=CSS, body=body), encoding="utf-8")
    print(f"Wrote -> {OUT}")


if __name__ == "__main__":
    main()
