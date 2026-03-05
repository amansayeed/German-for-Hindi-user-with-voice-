# -*- coding: utf-8 -*-
"""Build source/a2/a2-vocabulary.json from german_a2_categorized_complete.csv (same structure as b1-vocabulary.json)."""
import csv
import json
from pathlib import Path
from collections import OrderedDict

BASE = Path(__file__).resolve().parent.parent
CSV_PATH = BASE / "output" / "german_a2_categorized_complete.csv"
OUT_JSON = BASE / "source" / "a2" / "a2-vocabulary.json"

CATEGORY_COLORS = [
    "#e8f5e9", "#fce4ec", "#e3f2fd", "#f3e5f5", "#ffccbc",
    "#c8e6c9", "#b2ebf2", "#fff9c4", "#d7ccc8", "#b2dfdb",
    "#e1bee7", "#ffecb3", "#c5e1a5", "#b3e5fc", "#f8bbd0",
    "#d1c4e9", "#b2dfdb", "#ffcc80", "#cfd8dc", "#ffab91",
    "#a5d6a7", "#80deea", "#ce93d8", "#fff59d", "#90caf9",
    "#ef9a9a",
]


def category_to_slug(cat: str) -> str:
    parts = cat.split(None, 1)
    name = parts[1] if len(parts) > 1 else (parts[0] if parts else "Other")
    return name.replace(" ", "_")


def get_emoji(cat: str) -> str:
    if not cat:
        return "📋"
    first = cat.strip().split()[0] if cat.strip() else "📋"
    if len(first) == 1:
        return first
    c = cat[0]
    if ord(c) >= 0x1F300 or (0x2600 <= ord(c) <= 0x26FF) or (0x2700 <= ord(c) <= 0x27BF):
        return c
    return "📋"


def get_display_name(cat: str) -> str:
    parts = cat.split(None, 1)
    return parts[1] if len(parts) > 1 else (parts[0] if parts else "Other")


def main():
    rows = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append((
                r.get("Category", "").strip(),
                r.get("German", "").strip(),
                r.get("English", "").strip(),
                r.get("Hindi", "").strip(),
            ))

    groups = OrderedDict()
    for cat, german, english, hindi in rows:
        if not german:
            continue
        if cat not in groups:
            groups[cat] = []
        groups[cat].append({"de": german, "en": english, "hi": hindi})

    total_words = sum(len(w) for w in groups.values())
    categories = []
    for idx, (cat, words) in enumerate(groups.items()):
        slug = category_to_slug(cat)
        name = get_display_name(cat)
        emoji = get_emoji(cat)
        color = CATEGORY_COLORS[idx % len(CATEGORY_COLORS)]
        word_entries = []
        for w in words:
            word_entries.append({
                "de": w["de"],
                "pronunciation": "",
                "hi": w["hi"],
                "en": w["en"],
            })
        categories.append({
            "id": slug,
            "name": name,
            "nameDe": "",
            "nameHi": "",
            "emoji": emoji,
            "color": color,
            "words": word_entries,
        })

    out = {
        "title": "German A2 Vocabulary",
        "subtitle": "Goethe-Zertifikat A2 Wortliste. Cleaned, A1 excluded, articles verified. Categorised and fully translated (EN/HI).",
        "totalWords": total_words,
        "categories": categories,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Wrote {OUT_JSON}: {total_words} words in {len(categories)} categories.")


if __name__ == "__main__":
    main()
