# -*- coding: utf-8 -*-
"""
Embed word-patterns-vocabulary.json into word-patterns-vocabulary.html
so the page works when opened via file:// (no server needed).
Run: python embed_vocabulary.py
"""
import json
import os
import re

DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(DIR, "word-patterns-vocabulary.json")
HTML_PATH = os.path.join(DIR, "word-patterns-vocabulary.html")

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    # Prevent </script> in JSON from closing the HTML script tag
    json_str = json_str.replace("</script>", "<\\/script>")

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # Replace existing embedded JSON block (script#word-patterns-data)
    pattern = re.compile(
        r'(<script\s+type="application/json"\s+id="word-patterns-data">)\s*\n.*?\n(\s*</script>)',
        re.DOTALL
    )
    embed_block = r'\1\n' + json_str + r'\n\2'
    new_html, n = pattern.subn(embed_block, html, count=1)
    if n == 0:
        # No existing block: insert before theme.js
        old = '    <div id="error" class="error" style="display:none;"></div>\n\n    <script src="../../js/theme.js">'
        new = '    <div id="error" class="error" style="display:none;"></div>\n\n    <script type="application/json" id="word-patterns-data">\n' + json_str + '\n    </script>\n\n    <script src="../../js/theme.js">'
        if old not in html:
            print("Could not find insertion point in HTML.")
            return 1
        new_html = html.replace(old, new)

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("Embedded vocabulary (%d words) into word-patterns-vocabulary.html" % data.get("totalWords", 0))
    return 0

if __name__ == "__main__":
    exit(main())
