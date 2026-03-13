# -*- coding: utf-8 -*-
"""
Merge all A2 categories except Verbs, Nouns, Pronouns into one "Vocabulary" category.
Clean words (strip, dedupe by German). Output same JSON structure. Run from repo root.
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
A2_JSON = BASE / "source" / "a2" / "a2-vocabulary.json"

KEEP_IDS = {"Verbs", "Nouns", "Pronouns"}
MERGED_ID = "Vocabulary"
MERGED_NAME = "Vocabulary"
MERGED_EMOJI = "📚"
MERGED_COLOR = "#fff8e1"


def _clean(s):
    """Strip and normalize whitespace; remove control chars."""
    if s is None:
        return ""
    s = str(s).strip()
    s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", s)
    return " ".join(s.split())


def _sort_key(de):
    """Sort key for German: case-insensitive, umlauts after base."""
    s = (de or "").strip().lower()
    for a, b in [("\u00e4", "ae"), ("\u00f6", "oe"), ("\u00fc", "ue")]:
        s = s.replace(a, b)
    return s


def _first_letter(de):
    """First letter for A–Z grouping; strip der/die/das if present."""
    s = (de or "").strip()
    for prefix in ("der ", "die ", "das "):
        if s.lower().startswith(prefix):
            s = s[len(prefix) :].strip()
            break
    if not s:
        return "?"
    c = s[0].upper()
    if c in "\u00c4\u00d6\u00dc":
        c = {"\u00c4": "A", "\u00d6": "O", "\u00dc": "U"}.get(c, c)
    return c if c.isalpha() else "?"


def main():
    with open(A2_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    categories = data.get("categories", [])
    keep_cats = []
    merge_words = []

    for cat in categories:
        cid = (cat.get("id") or "").strip()
        if cid in KEEP_IDS:
            keep_cats.append(cat)
            continue
        for w in cat.get("words", []):
            de = _clean(w.get("de", ""))
            en = _clean(w.get("en", ""))
            hi = _clean(w.get("hi", ""))
            if not de:
                continue
            merge_words.append({
                "de": de,
                "pronunciation": _clean(w.get("pronunciation", "")) or "",
                "hi": hi,
                "en": en,
            })

    # Dedupe by German (lowercase), keep first
    seen = set()
    unique = []
    for w in merge_words:
        key = w["de"].lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(w)

    # Sort by German (A–Z)
    unique.sort(key=lambda w: _sort_key(w["de"]))

    vocabulary_cat = {
        "id": MERGED_ID,
        "name": MERGED_NAME,
        "nameDe": "",
        "nameHi": "शब्दावली",
        "emoji": MERGED_EMOJI,
        "color": MERGED_COLOR,
        "words": unique,
    }

    # Order: Verbs, Pronouns, Vocabulary, Nouns
    order_ids = ["Verbs", "Pronouns", MERGED_ID, "Nouns"]
    new_categories = []
    for oid in order_ids:
        for c in keep_cats:
            if (c.get("id") or "").strip() == oid:
                new_categories.append(c)
                break
        if oid == MERGED_ID:
            new_categories.append(vocabulary_cat)

    total = sum(len(c.get("words", [])) for c in new_categories)
    data["categories"] = new_categories
    data["totalWords"] = total

    with open(A2_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Wrote {A2_JSON}")
    print(f"Categories: {[c.get('id') for c in new_categories]}")
    print(f"Vocabulary words: {len(unique)}")
    print(f"Total words: {total}")


if __name__ == "__main__":
    main()
