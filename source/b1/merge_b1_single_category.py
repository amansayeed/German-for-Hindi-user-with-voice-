#!/usr/bin/env python3
"""Merge all letter-based categories (Goethe_A, Goethe_B, ...) into one category like A1-650."""
import json
from pathlib import Path

p = Path(__file__).resolve().parent
with open(p / "b1-vocabulary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

all_words = []
for cat in data["categories"]:
    all_words.extend(cat["words"])

# Sort by German word (case-insensitive)
all_words.sort(key=lambda w: (w.get("de") or "").lower())

data["categories"] = [
    {
        "id": "B1_Wortliste",
        "name": "B1 Wortliste",
        "nameDe": "Goethe B1 Wortliste",
        "nameHi": "B1 शब्दावली",
        "emoji": "📖",
        "color": "#e3f2fd",
        "words": all_words,
    }
]
data["totalWords"] = len(all_words)

with open(p / "b1-vocabulary.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Merged into one category: B1_Wortliste with {len(all_words)} words.")
