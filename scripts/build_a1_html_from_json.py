# -*- coding: utf-8 -*-
"""
Generate source/a1-650/a1-650.html from source/a1-650/a1-vocabulary.json ONLY.
All vocabulary data comes from the JSON. Same layout: h1, subtitle, toc, category sections, note, total box.
Columns: # | German | English | Hindi.
"""
import html as html_module
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
A1_JSON = BASE / "source" / "a1-650" / "a1-vocabulary.json"
A1_HTML = BASE / "source" / "a1-650" / "a1-650.html"


def escape_attr(s):
    if s is None:
        return ""
    return (str(s).replace("\\", "\\\\").replace("'", "&#39;"))


def escape_text(s):
    if s is None:
        return ""
    return html_module.escape(str(s))


def build_main_content(data):
    total = data.get("totalWords", 0)
    subtitle = data.get("subtitle", "")
    categories = data.get("categories", [])
    sub_line = escape_text(subtitle) if subtitle else escape_text(f"{total} A1 words")
    out = [
        '    <h1>🇩🇪 German A1 Vocabulary List</h1>',
        '',
        f'    <p class="subtitle">{sub_line}</p>',
        '',
        '    <div class="toc">',
        f'        <h2>📑 Categories (विषय) ({len(categories)})</h2>',
        '        <div class="toc-grid">',
    ]
    for cat in categories:
        cid = escape_attr(cat.get("id", ""))
        name = escape_text(cat.get("name", ""))
        emoji = cat.get("emoji", "📋")
        n = len(cat.get("words", []))
        out.append(f'            <a href="#{cid}" class="toc-item"><span>{emoji}</span> {name} ({n})</a>')
    out.append('        </div>')
    out.append('    </div>')
    for cat in categories:
        cid = escape_attr(cat.get("id", ""))
        name = escape_text(cat.get("name", ""))
        emoji = cat.get("emoji", "📋")
        color = cat.get("color", "#e8f5e9")
        color_alpha = color + "20" if len(color) == 7 else color + "20"
        words = cat.get("words", [])
        out.append(f'    <div class="category" id="{cid}">')
        out.append(f'        <div class="category-header" style="background-color: {color};">')
        out.append(f'            <span class="emoji">{emoji}</span>')
        out.append(f'            <span>{name}</span>')
        out.append(f'            <span class="count">{len(words)} words</span>')
        out.append('        </div>')
        out.append('        <table>')
        out.append('            <thead>')
        out.append('                <tr>')
        out.append('                    <th style="width:40px">#</th>')
        out.append('                    <th>German</th>')
        out.append('                    <th>English</th>')
        out.append('                    <th>Hindi</th>')
        out.append('                </tr>')
        out.append('            </thead>')
        out.append('            <tbody>')
        for i, w in enumerate(words, 1):
            de = w.get("de", "")
            en = w.get("en", "")
            hi = w.get("hi", "")
            de_attr = escape_attr(de)
            de_text = escape_text(de)
            en_text = escape_text(en)
            hi_text = escape_text(hi)
            out.append(
                f'                <tr style="background-color: {color_alpha};">'
                f'<td>{i}</td>'
                f'<td class="german"><span class="audio-btn" onclick="speakGerman(\'{de_attr}\')" title="Click to hear pronunciation">🔊</span>{de_text}</td>'
                f'<td class="english">{en_text}</td>'
                f'<td class="hindi">{hi_text}</td>'
                '</tr>'
            )
        out.append('            </tbody>')
        out.append('        </table>')
        out.append('    </div>')
    out.append('')
    out.append('    <p class="note">')
    out.append('        💡 <strong>Memory Tip:</strong> Learn related words together! Study one category per day.<br>')
    out.append('        💡 <strong>याद रखने का तरीका:</strong> संबंधित शब्द एक साथ सीखें! प्रतिदिन एक विषय पढ़ें।<br><br>')
    out.append('    </p>')
    out.append('')
    out.append(f'    <div style="text-align: center; padding: 30px; margin: 20px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">')
    out.append(f'        <h2 style="color: white; margin: 0; font-size: 28px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">')
    out.append(f'            📊 Total Words: <span style="font-size: 36px; font-weight: 900;">{total}</span>')
    out.append('        </h2>')
    out.append(f'        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">')
    out.append(f'            कुल शब्द: {total} | Complete A1 German Vocabulary')
    out.append('        </p>')
    out.append('    </div>')
    return "\n".join(out)


def main():
    with open(A1_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    raw = A1_HTML.read_text(encoding="utf-8") if A1_HTML.exists() else ""
    nav_end = raw.find("</nav>")
    if nav_end == -1:
        nav_end = 0
    else:
        nav_end += len("</nav>")
    script_start = raw.find("<!-- Inline Scripts for offline use -->")
    if script_start == -1:
        script_start = raw.find("<script src=\"../../js/theme.js\">")
    if script_start == -1:
        footer = "\n    <!-- Inline Scripts for offline use -->\n    <script src=\"../../js/theme.js\"></script>\n    <script>\n        function speakGerman(word) {\n            if (window.speechSynthesis.speaking) window.speechSynthesis.cancel();\n            const u = new SpeechSynthesisUtterance(word); u.lang = 'de-DE'; u.rate = 0.8;\n            const v = window.speechSynthesis.getVoices().find(v => v.lang.startsWith('de'));\n            if (v) u.voice = v;\n            window.speechSynthesis.speak(u);\n        }\n        function toggleSidebar() {\n            const s = document.getElementById('sidebar'); const o = document.querySelector('.sidebar-overlay');\n            if (s && o) { s.classList.toggle('open'); o.classList.toggle('active'); }\n        }\n    </script>\n</body>\n</html>"
    else:
        footer = raw[script_start:]
    header = raw[:nav_end]
    main_content = build_main_content(data)
    full_html = header + "\n" + main_content + "\n\n" + footer
    A1_HTML.write_text(full_html, encoding="utf-8")
    total = data.get("totalWords", 0)
    row_count = full_html.count('<tr style="background-color:')
    print(f"Wrote {A1_HTML}")
    print(f"JSON totalWords: {total}, HTML rows: {row_count}")
    assert row_count == total, "HTML row count must match JSON totalWords"


if __name__ == "__main__":
    main()
