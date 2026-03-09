# -*- coding: utf-8 -*-
"""
Embed word-patterns-vocabulary.json into word-patterns-vocabulary.html
so the page works when opened via file:// (no server needed).
Run: python embed_vocabulary.py
"""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(DIR, "word-patterns-vocabulary.json")
HTML_PATH = os.path.join(DIR, "word-patterns-vocabulary.html")
MARKER = "    <!-- EMBED_VOCABULARY_JSON -->"

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    # Prevent </script> in JSON from closing the HTML script tag
    json_str = json_str.replace("</script>", "<\\/script>")

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    if MARKER not in html:
        # Insert before theme.js: after error div
        old = "    <div id=\"error\" class=\"error\" style=\"display:none;\"></div>\n\n    <script src=\"../../js/theme.js\">"
        new = "    <div id=\"error\" class=\"error\" style=\"display:none;\"></div>\n\n    <script type=\"application/json\" id=\"word-patterns-data\">\n" + json_str + "\n    </script>\n\n    <script src=\"../../js/theme.js\">"
        if old not in html:
            print("Could not find insertion point in HTML.")
            return 1
        html = html.replace(old, new)
    else:
        # Replace placeholder with embedded JSON
        embed_block = "    <script type=\"application/json\" id=\"word-patterns-data\">\n" + json_str + "\n    </script>"
        html = html.replace(MARKER, embed_block)

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("Embedded vocabulary into word-patterns-vocabulary.html")
    return 0

if __name__ == "__main__":
    exit(main())
