# -*- coding: utf-8 -*-
"""
Clean A2 vocabulary JSON:
1. Remove special/formatting characters from German words (de).
2. Move words into correct categories (nouns with der/die/das -> Nouns; create categories if missing).
3. Update totalWords and write back. Caller should then run build_a2_html_from_json.py.
"""
import json
import re
from pathlib import Path


def remove_surrogates(obj):
    """Replace surrogate characters so UTF-8 encode works."""
    if isinstance(obj, str):
        return obj.encode("utf-8", errors="replace").decode("utf-8")
    if isinstance(obj, dict):
        return {k: remove_surrogates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [remove_surrogates(i) for i in obj]
    return obj


def load_json_safe(path):
    """Load JSON and replace any surrogate chars in decoded strings."""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    # Replace lone surrogates so json.loads doesn't leave them in strings
    raw = raw.encode("utf-8", errors="replace").decode("utf-8")
    return json.loads(raw)

BASE = Path(__file__).resolve().parent.parent
A2_JSON = BASE / "source" / "a2" / "a2-vocabulary.json"


def clean_german_word(de: str) -> str:
    """Remove formatting/special characters from German word. Keep a-z, A-Z, a umlauts, space, hyphen."""
    if not de or not isinstance(de, str):
        return de
    s = de.strip()

    # Remove (Sg.) (Pl.) at end
    s = re.sub(r'\s*\(Sg\.\)\s*$', '', s)
    s = re.sub(r'\s*\(Pl\.\)\s*$', '', s)

    # Pattern (x)/(y)word or (x)-(y)word -> xword, yword
    match = re.match(r'^\(([^)]+)\)\s*/\s*\(([^)]+)\)\s*(.+)$', s)
    if match:
        p1, p2, rest = match.group(1).strip().strip("-"), match.group(2).strip().strip("-"), match.group(3).strip()
        s = "%s%s, %s%s" % (p1, rest, p2, rest)

    # Separable prefix in parens: (ab)fahren -> abfahren
    def replace_prefix(m):
        inner = m.group(1).strip().strip("-")
        if "/" in inner:
            parts = [p.strip().strip("-") for p in inner.split("/") if p.strip()]
            return "".join(parts) if len(parts) <= 1 else inner.replace("/", ", ")
        return inner

    s = re.sub(r'^\(([^)]*)\)\s*', replace_prefix, s)

    # Trailing paren content like (sich), (ab) - remove or keep as note; remove if just "(sich)"
    s = re.sub(r'\s*\(sich\)\s*$', '', s, flags=re.I)
    s = re.sub(r'\s*\(ab\)\s*$', '', s)
    s = re.sub(r'\s*\(aus\)\s*$', '', s)
    s = re.sub(r'\s*\(an/aus\)\s*$', '', s, flags=re.I)

    # Broken leading/trailing parens and slashes
    s = re.sub(r'^\s*[\(\/\-\s]+', '', s)
    s = re.sub(r'[\)\/\-\s]+\s*$', '', s)

    # Multiple slashes between words: -fahren/-gehen/ -> fahren, gehen
    if "/" in s:
        parts = [p.strip().strip("-()") for p in s.split("/") if p.strip()]
        if len(parts) > 1:
            s = ", ".join(parts)

    # Remove remaining parentheses (formatting artifacts)
    s = s.replace("(", "").replace(")", "")

    # Trailing/leading hyphen or slash (formatting)
    s = s.strip(" \t-/")

    # Normalize multiple spaces
    s = re.sub(r'\s+', ' ', s).strip()

    return s


def is_noun(de: str) -> bool:
    """True if word starts with der/die/das (article)."""
    if not de or not isinstance(de, str):
        return False
    t = de.strip()
    return t.startswith("der ") or t.startswith("die ") or t.startswith("das ")


def main():
    data = load_json_safe(A2_JSON)

    categories = data.get("categories", [])
    cat_by_id = {c.get("id"): c for c in categories}

    # Ensure Nouns category exists
    if "Nouns" not in cat_by_id:
        categories.append({
            "id": "Nouns",
            "name": "Nouns",
            "nameDe": "",
            "nameHi": "",
            "emoji": "\U0001f4e6",  # package
            "color": "#e8eaf6",
            "words": []
        })
        cat_by_id["Nouns"] = categories[-1]

    nouns_cat = cat_by_id["Nouns"]
    moved_to_nouns = 0
    cleaned_count = 0

    for cat in categories:
        words = cat.get("words", [])
        new_words = []
        for w in words:
            de = w.get("de", "")
            cleaned = clean_german_word(de)
            if cleaned != de:
                w = dict(w)
                w["de"] = cleaned
                cleaned_count += 1

            if cat.get("id") != "Nouns" and is_noun(cleaned):
                nouns_cat["words"].append(w)
                moved_to_nouns += 1
            else:
                new_words.append(w)

        cat["words"] = new_words

    # Remove empty categories
    data["categories"] = [c for c in categories if c.get("words")]

    total = sum(len(c.get("words", [])) for c in data["categories"])
    data["totalWords"] = total

    data = remove_surrogates(data)
    with open(A2_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Cleaned German field: %d entries" % cleaned_count)
    print("Moved to Nouns: %d" % moved_to_nouns)
    print("Total words: %d" % total)
    print("Categories: %d" % len(data["categories"]))
    print("Wrote: %s" % A2_JSON)


if __name__ == "__main__":
    main()
