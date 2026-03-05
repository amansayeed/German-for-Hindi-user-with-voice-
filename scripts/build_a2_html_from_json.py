# -*- coding: utf-8 -*-
"""
Generate source/a2/a2.html from source/a2/a2-vocabulary.json ONLY.
Uses same UI structure, table layout, and category grouping as A1 HTML.
Columns: # | German | English | Hindi. No extra columns. Every JSON word appears exactly once.
"""
import html as html_module
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
A2_JSON = BASE / "source" / "a2" / "a2-vocabulary.json"
A2_HTML = BASE / "source" / "a2" / "a2.html"


def escape_attr(s):
    """Escape for HTML attribute (e.g. inside onclick='...')."""
    if s is None:
        return ""
    return (str(s).replace("\\", "\\\\").replace("'", "&#39;"))


def escape_text(s):
    """Escape for HTML text content."""
    if s is None:
        return ""
    return html_module.escape(str(s))


def build_main_content(data):
    """Build h1, subtitle, toc, and category sections from JSON only."""
    total = data.get("totalWords", 0)
    subtitle = data.get("subtitle", "")
    categories = data.get("categories", [])
    categories = sorted(categories, key=lambda c: (c.get("name") or c.get("id") or "").lower())
    # Subtitle from JSON, or fallback with word count
    sub_line = escape_text(subtitle) if subtitle else escape_text(f"{total} A2 words")
    out = [
        f'<h1>🇩🇪 German A2 Vocabulary List</h1>',
        f'<p class="subtitle">{sub_line}</p>',
        '<div class="toc">',
        f'<h2>📑 Categories (विषय) ({len(categories)})</h2>',
        '<div class="toc-grid">',
    ]
    # TOC links: href="#id", emoji, name (count)
    for cat in categories:
        cid = escape_attr(cat.get("id", ""))
        name = escape_text(cat.get("name", ""))
        emoji = cat.get("emoji", "📋")
        n = len(cat.get("words", []))
        out.append(f'<a class="toc-item" href="#{cid}"><span>{emoji}</span> {name} ({n})</a>')
    out.append("</div>")
    out.append("</div>")
    # Category sections
    for cat in categories:
        cid = escape_attr(cat.get("id", ""))
        name = escape_text(cat.get("name", ""))
        emoji = cat.get("emoji", "📋")
        color = cat.get("color", "#e8f5e9")
        color_alpha = color + "20" if len(color) == 7 else color + "20"
        words = cat.get("words", [])
        out.append(f'<div class="category" id="{cid}">')
        out.append(f'<div class="category-header" style="background-color: {color};">')
        out.append(f'<span class="emoji">{emoji}</span>')
        out.append(f'<span>{name}</span>')
        out.append(f'<span class="count">{len(words)} words</span>')
        out.append("</div>")
        out.append("<table>")
        out.append("<thead><tr><th style=\"width:40px\">#</th><th>German</th><th>English</th><th>Hindi</th></tr></thead>")
        out.append("<tbody>")
        for i, w in enumerate(words, 1):
            de = w.get("de", "")
            en = w.get("en", "")
            hi = w.get("hi", "")
            de_attr = escape_attr(de)
            de_text = escape_text(de)
            en_text = escape_text(en)
            hi_text = escape_text(hi)
            out.append(
                f'<tr style="background-color: {color_alpha};">'
                f'<td>{i}</td>'
                f'<td class="german"><span class="audio-btn" onclick="speakGerman(\'{de_attr}\')" title="Click to hear pronunciation">🔊</span>{de_text}</td>'
                f'<td class="english">{en_text}</td>'
                f'<td class="hindi">{hi_text}</td>'
                "</tr>"
            )
        out.append("</tbody>")
        out.append("</table>")
        out.append("</div>")
    return "\n".join(out)


def main():
    with open(A2_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Read template: head + sidebar + footer from current a2.html
    html_path = A2_HTML
    if html_path.exists():
        raw = html_path.read_text(encoding="utf-8")
    else:
        raw = ""
    # Find boundaries: from start to end of </nav>, then from <!-- Inline Scripts --> to end
    nav_end = raw.find("</nav>")
    if nav_end == -1:
        nav_end = 0
    else:
        nav_end += len("</nav>")
    script_start = raw.find("<!-- Inline Scripts for offline use -->")
    if script_start == -1:
        script_start = raw.find("<script>", raw.find("</div>", raw.rfind("</table>")))
    if script_start == -1:
        script_end = len(raw)
        footer = "\n<!-- Inline Scripts for offline use -->\n<script>\n        function speakGerman(word) {\n            if (window.speechSynthesis.speaking) window.speechSynthesis.cancel();\n            const u = new SpeechSynthesisUtterance(word);\n            u.lang = 'de-DE';\n            u.rate = 0.8;\n            const voices = window.speechSynthesis.getVoices();\n            const g = voices.find(v => v.lang.startsWith('de'));\n            if (g) u.voice = g;\n            window.speechSynthesis.speak(u);\n        }\n        function toggleSidebar() {\n            var s = document.getElementById('sidebar');\n            var o = document.querySelector('.sidebar-overlay');\n            if (s && o) { s.classList.toggle('open'); o.classList.toggle('active'); }\n        }\n    </script>\n<script src=\"../../js/theme.js\"></script>\n</body>\n</html>"
    else:
        footer = raw[script_start:]
    header = raw[:nav_end] if nav_end else get_default_header()
    main_content = build_main_content(data)
    full_html = header + "\n" + main_content + "\n" + footer
    A2_HTML.write_text(full_html, encoding="utf-8")
    # Validation
    total_json = data.get("totalWords", 0)
    total_cats = len(data.get("categories", []))
    words_in_json = sum(len(c.get("words", [])) for c in data.get("categories", []))
    print(f"Wrote {A2_HTML}")
    print(f"JSON totalWords: {total_json}, categories: {total_cats}, sum(words): {words_in_json}")
    assert words_in_json == total_json, "totalWords must equal sum of category word counts"
    # Count rows in generated HTML
    row_count = full_html.count('<tr style="background-color:')
    print(f"HTML table rows: {row_count}")
    assert row_count == total_json, "HTML row count must match JSON totalWords"
    print("Validation OK: word count and category count match JSON.")


def get_default_header():
    """Minimal header if no existing file."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes"/>
<title>German A2 Vocabulary - Organized by Themes</title>
<link href="../../css/theme.css" rel="stylesheet"/>
<link href="../../css/navbar.css" rel="stylesheet"/>
</head>
<body>
<nav class="sidebar" id="sidebar"><div class="sidebar-header"><h2>🇩🇪 German Learning</h2></div><div class="sidebar-nav"><a href="../../index.html" class="sidebar-nav-item">Home</a><a href="a2.html" class="sidebar-nav-item active">A2 Vocabulary</a></div></nav>"""


if __name__ == "__main__":
    main()
