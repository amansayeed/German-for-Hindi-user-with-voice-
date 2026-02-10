"""
Build sentence-practice-vocab.json from writing-data.json.
Output: flat array of { "de", "en", "hi" } for all German vocabulary.
"""
import json

with open('writing-data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

flat = []
for cat_entries in data.values():
    for item in cat_entries:
        de = (item.get('de') or '').strip()
        if not de:
            continue
        flat.append({
            "de": de,
            "en": (item.get('en') or '').strip(),
            "hi": (item.get('hi') or '').strip()
        })

with open('sentence-practice-vocab.json', 'w', encoding='utf-8') as f:
    json.dump(flat, f, ensure_ascii=False, indent=2)

print(f"Written {len(flat)} entries to sentence-practice-vocab.json")
