# -*- coding: utf-8 -*-
"""Remove from source/a2/a2-vocabulary.json any word whose 'de' appears in source/a1-650/a1-vocabulary.json."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
A1_JSON = BASE / "source" / "a1-650" / "a1-vocabulary.json"
A2_JSON = BASE / "source" / "a2" / "a2-vocabulary.json"


def main():
    with open(A1_JSON, "r", encoding="utf-8") as f:
        a1 = json.load(f)
    with open(A2_JSON, "r", encoding="utf-8") as f:
        a2 = json.load(f)

    a1_headwords = {
        (w.get("de") or "").strip()
        for c in a1.get("categories", [])
        for w in c.get("words", [])
        if (w.get("de") or "").strip()
    }

    removed_count = 0
    new_categories = []
    for cat in a2.get("categories", []):
        new_words = [
            w for w in cat.get("words", [])
            if (w.get("de") or "").strip() not in a1_headwords
        ]
        dropped = len(cat.get("words", [])) - len(new_words)
        removed_count += dropped
        if new_words:
            new_categories.append({**cat, "words": new_words})

    total = sum(len(c["words"]) for c in new_categories)
    a2["categories"] = new_categories
    a2["totalWords"] = total

    with open(A2_JSON, "w", encoding="utf-8") as f:
        json.dump(a2, f, ensure_ascii=False, indent=2)

    print(f"Removed {removed_count} A1 headwords from A2 JSON.")
    print(f"A2 now has {total} words in {len(new_categories)} categories.")


if __name__ == "__main__":
    main()
