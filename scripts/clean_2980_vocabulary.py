# -*- coding: utf-8 -*-
"""
Clean 2980-most-frequent-german-nouns.json:
- Remove words that exist in A1, A2, or B1 (compare by noun stem).
- Remove duplicates (same article + de).
- Fix broken plural "(usually" and invalid entries (de "—").
- Keep JSON schema; then run HTML embed.
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
JSON_2980 = BASE / "source" / "the-2980-most-frequently-used-german" / "2980-most-frequent-german-nouns.json"
A1_JSON = BASE / "source" / "a1-650" / "a1-vocabulary.json"
A2_JSON = BASE / "source" / "a2" / "a2-vocabulary.json"
B1_JSON = BASE / "source" / "b1" / "b1-vocabulary.json"
BUILD_SCRIPT = BASE / "source" / "the-2980-most-frequently-used-german" / "build_2980_html_embed.py"


def normalize_stem(de):
    """Noun stem for overlap: strip optional article, lowercase."""
    if not de:
        return ""
    s = de.strip().lower()
    for prefix in ("der ", "die ", "das "):
        if s.startswith(prefix):
            return s[len(prefix):].strip().split()[0] if s[len(prefix):].strip() else ""
    return s.split()[0] if s else ""


def collect_words_from_vocab(path):
    """Collect all word stems and tokens from a vocabulary JSON (A1/A2/B1)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    words = set()
    for cat in data.get("categories", []):
        for w in cat.get("words", []):
            de = w.get("de") or ""
            if not de or de.strip() == "":
                continue
            s = de.strip().lower()
            # Full stem (strip article)
            for prefix in ("der ", "die ", "das "):
                if s.startswith(prefix):
                    rest = s[len(prefix):].strip()
                    if rest:
                        words.add(rest.split()[0])
                    break
            else:
                words.add(s.split()[0])
            # All tokens (so "Guten Abend" -> abend in set)
            for token in re.split(r"\s+", s):
                token = re.sub(r"^der$|^die$|^das$", "", token)
                if token:
                    words.add(token)
    return words


def main():
    # Load A1, A2, B1 stems
    a1_words = collect_words_from_vocab(A1_JSON)
    a2_words = collect_words_from_vocab(A2_JSON)
    b1_words = collect_words_from_vocab(B1_JSON)
    overlap = a1_words | a2_words | b1_words

    with open(JSON_2980, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = data.get("entries", [])
    seen_key = set()
    cleaned = []
    removed_overlap = 0
    removed_duplicate = 0
    removed_invalid = 0
    fixed_plural = 0

    for e in entries:
        article = (e.get("article") or "").strip()
        de = (e.get("de") or "").strip()
        plural = (e.get("plural") or "").strip()
        en = (e.get("en") or "").strip()
        hi = (e.get("hi") or "").strip()

        # Remove invalid placeholders
        if not de or de == "—" or de == "-":
            removed_invalid += 1
            continue

        # Overlap: remove if noun stem is in A1/A2/B1
        stem = normalize_stem(de) or de.lower().split()[0]
        if stem in overlap:
            removed_overlap += 1
            continue

        # Dedupe: same article + de -> keep first
        key = (article.lower(), de)
        if key in seen_key:
            removed_duplicate += 1
            continue
        seen_key.add(key)

        # Fix broken plural
        if plural.startswith("(usually") or plural == "(usually":
            plural = "—"
            fixed_plural += 1

        cleaned.append({
            "article": article or "der",
            "de": de,
            "plural": plural if plural else "—",
            "en": en or "—",
            "hi": hi or "—",
        })

    data["entries"] = cleaned
    if "totalWords" in data:
        data["totalWords"] = len(cleaned)
    if "total" in data:
        data["total"] = len(cleaned)

    with open(JSON_2980, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("2980 clean: kept %d entries" % len(cleaned))
    print("  removed (overlap A1/A2/B1): %d" % removed_overlap)
    print("  removed (duplicate): %d" % removed_duplicate)
    print("  removed (invalid/placeholder): %d" % removed_invalid)
    print("  fixed plural: %d" % fixed_plural)

    # Run HTML embed
    import subprocess
    import sys
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(BASE), check=True)


if __name__ == "__main__":
    main()
