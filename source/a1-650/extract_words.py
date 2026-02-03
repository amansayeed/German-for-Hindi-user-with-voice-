"""
Extract words from a1-650.html, keep A1 only, remove duplicates by German (de).
Output: writing-data.json (deduplicated). Run and then writing-data.js can be regenerated from JSON.
"""
import re
import json

with open('a1-650.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find each category block: <div class="category" id="ID"> ... <tbody>...</tbody>
pattern = r'<div class="category" id="([^"]+)"[^>]*>.*?<tbody>(.*?)</tbody>'
matches = re.findall(pattern, html, re.DOTALL)

row_pattern = r'<td class="german">(?:<span[^>]*>[^<]*</span>)?([^<]*)</td>\s*<td class="english">([^<]*)</td>\s*<td class="hindi">([^<]*)</td>'

seen_de = set()
data = {}
for cat_id, tbody in matches:
    rows = re.findall(row_pattern, tbody)
    data[cat_id] = []
    for de, en, hi in rows:
        de_clean = re.sub(r'^[^\wäöüßÄÖÜ]+', '', de.strip()).strip()
        en_clean = en.strip()
        hi_clean = hi.strip()
        if not de_clean:
            continue
        if de_clean in seen_de:
            continue
        seen_de.add(de_clean)
        data[cat_id].append({"de": de_clean, "en": en_clean, "hi": hi_clean})

with open('writing-data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=0)

# Regenerate writing-data.js from same data (A1 only, no duplicates)
with open('writing-data.js', 'w', encoding='utf-8') as f:
    f.write('window.EMBEDDED_WORDS = ' + json.dumps(data, ensure_ascii=False) + ';')

total = sum(len(v) for v in data.values())
print("Categories:", len(data))
print("Total unique A1 words (duplicates removed):", total)
for k, v in list(data.items())[:5]:
    print(" ", k, len(v))
print("writing-data.json and writing-data.js updated. Use these for A1-only, no-duplicate word lists.")
