"""One-off: embed b1-vocabulary.json into b1.html so the page works without fetch (file://)."""
import json
import re
from pathlib import Path

p = Path(__file__).resolve().parent
with open(p / "b1-vocabulary.json", "r", encoding="utf-8") as f:
    out = json.load(f)
json_str = json.dumps(out, ensure_ascii=False, indent=2).replace("</", "<\\/")
with open(p / "b1.html", "r", encoding="utf-8") as f:
    html = f.read()
pat = re.compile(
    r'(<script type="application/json" id="b1-vocabulary-embed">).*?(</script>)',
    re.DOTALL,
)
if pat.search(html):
    html = pat.sub(r"\1" + json_str + r"\2", html, count=1)
    with open(p / "b1.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Embedded vocabulary into b1.html")
else:
    print("Embed block not found in b1.html")
