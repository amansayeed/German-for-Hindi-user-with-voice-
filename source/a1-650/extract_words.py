import re
import json

with open('a1-650.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find each category block: <div class="category" id="ID"> ... <tbody>...</tbody>
pattern = r'<div class="category" id="([^"]+)"[^>]*>.*?<tbody>(.*?)</tbody>'
matches = re.findall(pattern, html, re.DOTALL)

data = {}
for cat_id, tbody in matches:
    # Each row: <tr...><td>N</td><td class="german">...WORD</td><td class="english">ENG</td><td class="hindi">HI</td></tr>
    row_pattern = r'<td class="german">(?:<span[^>]*>[^<]*</span>)?([^<]*)</td>\s*<td class="english">([^<]*)</td>\s*<td class="hindi">([^<]*)</td>'
    rows = re.findall(row_pattern, tbody)
    data[cat_id] = []
    for de, en, hi in rows:
        de = re.sub(r'^[^\wäöüßÄÖÜ]+', '', de.strip())
        en = en.strip()
        hi = hi.strip()
        if de:
            data[cat_id].append({"de": de, "en": en, "hi": hi})

with open('writing-data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=0)

print("Categories:", len(data))
for k, v in list(data.items())[:5]:
    print(k, len(v))
