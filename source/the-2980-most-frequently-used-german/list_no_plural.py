import json
with open("2980-most-frequent-german-nouns.json", encoding="utf-8") as f:
    d = json.load(f)
entries = d["entries"]
dash = "\u2014"
no_plural = [
    (e["rank"], e.get("en"), (e.get("de") or "").strip(), e.get("article"))
    for e in entries
    if (e.get("plural") or "").strip() in ("", dash) or e.get("plural") is None
]
# unique de for lookup
seen = set()
for r, en, de, art in no_plural:
    if de and de not in seen:
        seen.add(de)
        print(de)
# also write full list to file for processing
with open("no_plural_list.txt", "w", encoding="utf-8") as out:
    out.write("count: %d\n" % len(no_plural))
    for r, en, de, art in no_plural:
        out.write("%s\t%s\t%s\n" % (de, en, art))
print("total entries:", len(no_plural), "unique de:", len(seen))
