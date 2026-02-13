import json
with open("2980-most-frequent-german-nouns.json", encoding="utf-8") as f:
    d = json.load(f)
entries = d["entries"]
missing = sorted(set(
    (e.get("en") or "").strip().lower()
    for e in entries
    if not (e.get("hi") or "").strip()
    and (e.get("en") or "").strip()
    and (e.get("en") or "").strip() not in ("—", "")
))
with open("missing_hi_words.txt", "w", encoding="utf-8") as out:
    out.write(str(len(missing)) + "\n")
    for w in missing:
        out.write(w + "\n")
print("Missing Hindi count:", len(missing))
