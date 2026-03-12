# -*- coding: utf-8 -*-
"""
Generate source/verbs/verbs.html from source/verbs/verbs-vocabulary.json.
Style like a1-650.html. Organized by level (A1, A2, B1, B2, C1, C2); within each
level verbs are in alphabetical order with letter sections A–Z and numbering 01, 02, ...
(zero-padded per letter section).
"""
import html as html_module
import json
from itertools import groupby
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
VERBS_JSON = BASE / "source" / "verbs" / "verbs-vocabulary.json"
VERBS_HTML = BASE / "source" / "verbs" / "verbs.html"
A1_HTML = BASE / "source" / "a1-650" / "a1-650.html"

VERB_COLOR_ALPHA = "#a5d6a720"


def escape_attr(s):
    if s is None:
        return ""
    return (str(s).replace("\\", "\\\\").replace("'", "&#39;"))


def escape_text(s):
    if s is None:
        return ""
    return html_module.escape(str(s))


def first_letter(de):
    """First letter for grouping (A–Z). Ä->A, Ö->O, Ü->U."""
    if not de:
        return "?"
    c = (de.strip() or "?")[0].upper()
    for old, new in [("Ä", "A"), ("Ö", "O"), ("Ü", "U")]:
        if c == old:
            return new
    return c if c.isalpha() else "?"


def sort_key(w):
    s = (w.get("de") or "").strip().lower()
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    return s


def build_content(data):
    lines = []
    lines.append('<h1>🇩🇪 Top 1000 German Verbs (A1–C2)</h1>')
    lines.append(f'<p class="subtitle">{escape_text(data.get("subtitle", ""))}</p>')

    # TOC: Levels A1, A2, B1, B2, C1, C2
    lines.append('<div class="toc">')
    lines.append('<h2>📑 Levels (स्तर)</h2>')
    lines.append('<div class="toc-grid" id="toc-grid">')
    for cat in data.get("categories", []):
        cid = escape_attr(cat.get("id", ""))
        n = len(cat.get("words", []))
        emoji = cat.get("emoji", "🟢")
        name = escape_text(cat.get("name", cid))
        lines.append(f'<a href="#level-{cid}" class="toc-item"><span>{emoji} {name}</span> ({n})</a>')
    lines.append('</div>')
    lines.append('</div>')
    lines.append('<div id="content">')
    lines.append('<style>.letter-section { margin-top: 20px; } .letter-header { margin: 16px 0 8px 0; font-size: 1.2rem; color: var(--accent, #1565c0); } .level-block .name-hi { margin-left: 8px; font-weight: normal; opacity: 0.9; }</style>')

    total = 0
    for cat in data.get("categories", []):
        cid = cat.get("id", "")
        words = list(cat.get("words", []))
        words.sort(key=sort_key)
        color = cat.get("color", "#a5d6a7")
        emoji = cat.get("emoji", "🟢")
        name = cat.get("name", cid)
        name_hi = cat.get("nameHi", "")

        # Level block anchor
        lines.append(f'<div class="category level-block" id="level-{escape_attr(cid)}">')
        lines.append(f'<div class="category-header" style="background-color: {color};">')
        lines.append(f'<span class="emoji">{emoji}</span>')
        lines.append(f'<span>{escape_text(name)}</span>')
        if name_hi:
            lines.append(f'<span class="name-hi">({escape_text(name_hi)})</span>')
        lines.append(f'<span class="count">{len(words)} verbs</span>')
        lines.append('</div>')

        # Letter groups within this level
        letter_groups = []
        for letter, group in groupby(words, key=lambda w: first_letter(w.get("de", ""))):
            letter_groups.append((letter, list(group)))
        letter_groups.sort(key=lambda x: x[0])

        for letter, letter_words in letter_groups:
            lid = escape_attr(letter)
            section_id = f"level-{escape_attr(cid)}-letter-{lid}"
            lines.append(f'<div class="letter-section" id="{section_id}">')
            lines.append(f'<h3 class="letter-header">🔤 {letter}</h3>')
            lines.append('<table>')
            lines.append('<thead><tr><th style="width:50px">#</th><th>German</th><th>English</th><th>Hindi</th></tr></thead>')
            lines.append('<tbody>')
            width = 3 if len(letter_words) >= 100 else 2
            for i, w in enumerate(letter_words, 1):
                num = str(i).zfill(width)
                de = w.get("de", "")
                en = w.get("en", "")
                hi = w.get("hi", "")
                de_attr = escape_attr(de)
                de_t = escape_text(de)
                en_t = escape_text(en)
                hi_t = escape_text(hi)
                lines.append(
                    f'<tr style="background-color: {VERB_COLOR_ALPHA};">'
                    f'<td>{num}</td>'
                    f'<td class="german"><span class="audio-btn" onclick="speakGerman(\'{de_attr}\')" title="Click to hear">🔊</span>{de_t}</td>'
                    f'<td class="english">{en_t}</td>'
                    f'<td class="hindi">{hi_t}</td>'
                    '</tr>'
                )
            lines.append('</tbody>')
            lines.append('</table>')
            lines.append('</div>')

        lines.append('</div>')
        total += len(words)

    lines.append('</div>')
    lines.append('')
    lines.append('<div style="text-align: center; padding: 30px; margin: 20px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">')
    lines.append(f'  <h2 style="color: white; margin: 0; font-size: 28px;">📊 Total Verbs: <strong style="font-size: 36px;">{total}</strong></h2>')
    lines.append(f'  <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">कुल क्रिया: {total} · A1–C2</p>')
    lines.append('</div>')
    return "\n".join(lines)


def main():
    with open(VERBS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Use a1-650.html as template: up to and including </nav>
    if A1_HTML.exists():
        raw = A1_HTML.read_text(encoding="utf-8")
        nav_end = raw.find("</nav>")
        if nav_end != -1:
            nav_end += len("</nav>")
            header = raw[:nav_end]
            header = header.replace("<title>German A1 Vocabulary", "<title>Top 1000 German Verbs", 1)
            # Links in sidebar are from a1-650 folder; rewrite for verbs folder
            header = header.replace('href="a1-650.html"', 'href="../a1-650/a1-650.html"')
            header = header.replace('href="grammar.html"', 'href="../a1-650/grammar.html"')
            header = header.replace('href="writing.html"', 'href="../a1-650/writing.html"')
            header = header.replace('href="sentence-practice.html"', 'href="../a1-650/sentence-practice.html"')
            # Remove active from A1 650, add Verbs as active
            header = header.replace(
                '<a href="../a1-650/a1-650.html" class="sidebar-nav-item active"><span class="emoji">📖</span> A1 Vocabulary (650)</a>',
                '<a href="../a1-650/a1-650.html" class="sidebar-nav-item"><span class="emoji">📖</span> A1 Vocabulary (650)</a>',
                1,
            )
            if "verbs/verbs.html" not in header:
                header = header.replace(
                    '<a href="../numbers/numbers.html" class="sidebar-nav-item"><span class="emoji">🔢</span> German Numbers</a>',
                    '<a href="../verbs/verbs.html" class="sidebar-nav-item active"><span class="emoji">🏃</span> Verbs (1000)</a>\n            <a href="../numbers/numbers.html" class="sidebar-nav-item"><span class="emoji">🔢</span> German Numbers</a>',
                    1,
                )
        else:
            header = get_default_header()
    else:
        header = get_default_header()

    footer = """
    <p class="note">💡 Top 1000 German verbs in alphabetical order. Each section numbered 01, 02, …</p>
    <!-- Inline Scripts for offline use -->
    <script src="../../js/theme.js"></script>
    <script>
        function speakGerman(word) {
            if (window.speechSynthesis.speaking) window.speechSynthesis.cancel();
            var u = new SpeechSynthesisUtterance(word);
            u.lang = 'de-DE';
            u.rate = 0.8;
            var voices = window.speechSynthesis.getVoices();
            var g = voices.find(function(v) { return v.lang.startsWith('de'); });
            if (g) u.voice = g;
            window.speechSynthesis.speak(u);
        }
        function toggleSidebar() {
            var s = document.getElementById('sidebar');
            var o = document.querySelector('.sidebar-overlay');
            if (s && o) { s.classList.toggle('open'); o.classList.toggle('active'); }
        }
    </script>
</body>
</html>"""

    main_content = build_content(data)
    full = header + "\n" + main_content + "\n" + footer

    VERBS_HTML.parent.mkdir(parents=True, exist_ok=True)
    VERBS_HTML.write_text(full, encoding="utf-8")
    print(f"Wrote {VERBS_HTML}. Total verbs: {data.get('totalWords', 0)}.")


def get_default_header():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes"/>
<title>Top 1000 German Verbs - A1 to C2</title>
<link rel="stylesheet" href="../../css/theme.css">
<link rel="stylesheet" href="../../css/navbar.css">
<style>
body{font-family:'Segoe UI',Arial,sans-serif;margin:20px;margin-left:280px;background:#f5f5f5;color:#333;line-height:1.6;}
.sidebar{position:fixed;left:0;top:0;width:260px;height:100vh;background:linear-gradient(180deg,#2d3748 0%,#1a202c 100%);z-index:1000;overflow-y:auto;}
.sidebar-header{padding:20px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;text-align:center;}
.sidebar-nav-item{display:block;padding:14px 20px;color:#e2e8f0;text-decoration:none;}
.sidebar-nav-item:hover{background:rgba(102,126,234,0.2);color:#fff;}
h1{text-align:center;color:#1565c0;}
.subtitle{text-align:center;color:#666;margin-bottom:30px;}
.category{margin-bottom:30px;background:#fff;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.1);overflow:hidden;}
.category-header{padding:15px 20px;font-size:20px;font-weight:bold;display:flex;align-items:center;gap:10px;}
.category-header .count{margin-left:auto;font-weight:normal;color:#666;}
table{width:100%;border-collapse:collapse;}
th{background:#0d47a1;color:white;padding:14px;text-align:left;}
td{padding:14px;border-bottom:1px solid #ddd;}
.german{font-weight:900;color:#0d47a1;font-size:20px;}
.english{color:#1b5e20;font-weight:700;}
.hindi{color:#4a148c;font-weight:700;}
.audio-btn{margin-right:8px;cursor:pointer;font-size:18px;}
.toc{background:#fff;padding:20px;border-radius:10px;margin-bottom:30px;box-shadow:0 2px 8px rgba(0,0,0,0.1);}
.toc h2{margin-top:0;color:#1565c0;}
.toc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(80px,1fr));gap:10px;}
.toc-item{padding:8px 12px;background:#f5f5f5;border-radius:5px;text-decoration:none;color:#333;text-align:center;}
.toc-item:hover{background:#e3f2fd;}
</style>
</head>
<body>
<nav class="sidebar" id="sidebar">
<div class="sidebar-header"><h2>🇩🇪 German Learning</h2></div>
<div class="sidebar-nav">
<a href="../../index.html" class="sidebar-nav-item">🏠 Home</a>
<a href="../a1-650/a1-650.html" class="sidebar-nav-item">📖 A1 Vocabulary</a>
<a href="../a2/a2.html" class="sidebar-nav-item">📘 A2 Vocabulary</a>
<a href="../b1/b1.html" class="sidebar-nav-item">📗 B1 Vocabulary</a>
<a href="verbs.html" class="sidebar-nav-item active">🏃 Verbs (1000)</a>
</div>
</nav>"""


if __name__ == "__main__":
    main()
