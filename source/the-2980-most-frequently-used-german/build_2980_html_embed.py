# -*- coding: utf-8 -*-
"""Embed 2980-most-frequent-german-nouns.json into the HTML so it works when opened from file:// (no server)."""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
JSON_PATH = BASE / "2980-most-frequent-german-nouns.json"
HTML_PATH = BASE / "the-2980-most-frequently-used-german.html"
PLACEHOLDER = "<!-- EMBED_NOUNS_JSON -->"


def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    json_str = json.dumps(data, ensure_ascii=False)
    json_str = json_str.replace("</script>", "<\\/script>")
    embed_block = '<script type="application/json" id="noun-data">\n' + json_str + "\n</script>"
    html = HTML_PATH.read_text(encoding="utf-8")
    # Replace placeholder or existing noun-data script
    if PLACEHOLDER in html:
        html = html.replace(PLACEHOLDER, embed_block + "\n    ")
    else:
        old = re.search(
            r'<script\s+type="application/json"\s+id="noun-data">.*?</script>',
            html, re.DOTALL
        )
        if old:
            html = html[:old.start()] + embed_block + html[old.end():]
        else:
            print("No placeholder or noun-data script found in HTML")
            return
    HTML_PATH.write_text(html, encoding="utf-8")
    print("Embedded %d entries into %s" % (len(data.get("entries", [])), HTML_PATH))


if __name__ == "__main__":
    main()
