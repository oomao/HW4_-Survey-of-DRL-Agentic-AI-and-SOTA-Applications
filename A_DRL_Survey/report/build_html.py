"""
Render the assembled HW4_DRL_Survey.md to a single self-contained HTML file
that can be opened in any browser and "Print -> Save as PDF" to produce the
final deliverable PDF — without needing pandoc / LaTeX / wkhtmltopdf.
"""

from __future__ import annotations

import re
from pathlib import Path

import markdown


HERE = Path(__file__).resolve().parent
SRC = HERE / "HW4_DRL_Survey.md"
OUT = HERE / "HW4_DRL_Survey.html"


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
  font-size: 0.9em;
  line-height: 1.4;
  border-left: 3px solid var(--accent);
}
pre code { background: transparent; padding: 0; }
table {
  border-collapse: collapse;
  margin: 1em 0;
  width: 100%;
  font-size: 0.92em;
}
th, td {
  border: 1px solid var(--border);
  padding: 6px 10px;
  vertical-align: top;
  text-align: left;
}
th { background: #f8fafc; }
hr { border: none; border-top: 1px solid var(--border); margin: 2em 0; }
blockquote {
  border-left: 4px solid var(--accent);
  margin: 1em 0;
  padding: 0.4em 1em;
  color: var(--muted);
  background: var(--code-bg);
  border-radius: 0 6px 6px 0;
}
img { max-width: 100%; height: auto; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* footnote refs */
sup a { color: var(--accent); font-size: 0.85em; }

/* page-break helpers when printing to PDF */
@media print {
  body { margin: 0; max-width: none; padding: 1cm 1.5cm; font-size: 10.5pt; }
  h1 { page-break-before: auto; }
  h2, h3 { page-break-after: avoid; }
  table, pre, blockquote, figure { page-break-inside: avoid; }
  a { color: var(--fg); text-decoration: none; }
}
.toc { background: #f8fafc; border: 1px solid var(--border); border-radius: 8px; padding: 1em 1.5em; margin: 1em 0; }
.toc h2 { border: none; margin-top: 0; color: var(--fg); font-size: 1.1em; }
"""


HTML_TEMPLATE = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>HW4 — A Survey of Deep Reinforcement Learning, Agentic AI, and SOTA Applications (2024–2026)</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""


def _strip_latex_blocks(text: str) -> str:
    text = re.sub(r"\\begin\{longtable\}\{[^}]*\}", "<table>\n", text)
    text = text.replace(r"\end{longtable}", "\n</table>")
    text = re.sub(r"\\(toprule|midrule|bottomrule)", "", text)
    text = text.replace("\\newpage", "<hr/>")
    text = re.sub(r"\\begin\{abstract\}", "<blockquote><strong>Abstract.</strong>", text)
    text = re.sub(r"\\end\{abstract\}", "</blockquote>", text)
    text = text.replace(r"\noindent", "")
    text = text.replace(r"\vspace{0.5em}", "")
    text = re.sub(r"\\textbf\{([^}]*)\}", r"**\1**", text)

    out_rows = []
    in_table = False
    for line in text.splitlines():
        if "<table>" in line:
            in_table = True
            out_rows.append(line)
            continue
        if "</table>" in line:
            in_table = False
            out_rows.append(line)
            continue
        if in_table and "&" in line:
            cells = [c.strip().rstrip("\\").strip() for c in line.split("&")]
            row = "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"
            out_rows.append(row)
        else:
            out_rows.append(line)
    return "\n".join(out_rows)


def main():
    text = SRC.read_text(encoding="utf-8")

    yaml_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if yaml_match:
        text = text[yaml_match.end():]

    text = _strip_latex_blocks(text)

    md = markdown.Markdown(
        extensions=["extra", "tables", "fenced_code", "footnotes", "toc", "sane_lists"],
        extension_configs={"toc": {"title": "Table of Contents", "toc_depth": "2-3"}},
    )
    body = md.convert(text)

    html = HTML_TEMPLATE.format(css=CSS, body=body)
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote HTML -> {OUT} ({len(html):,} bytes)")
    print("Open in any browser and 'Print -> Save as PDF' to produce the final PDF.")


if __name__ == "__main__":
    main()
