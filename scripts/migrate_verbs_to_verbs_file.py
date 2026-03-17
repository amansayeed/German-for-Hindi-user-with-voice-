# -*- coding: utf-8 -*-
"""
Extract all verbs from A1, A2, B1, and 2980 nouns file.
Remove those verbs from the source files and add them to verbs-vocabulary.json
organized by level (A1, A2, B1). Dedupe, normalize, update counts.
"""
import json
import re
from pathlib import Path
from collections import OrderedDict

BASE = Path(__file__).resolve().parent.parent
A1_JSON = BASE / "source" / "a1-650" / "a1-vocabulary.json"
A2_JSON = BASE / "source" / "a2" / "a2-vocabulary.json"
B1_JSON = BASE / "source" / "b1" / "b1-vocabulary.json"
NOUNS_2980_JSON = BASE / "source" / "the-2980-most-frequently-used-german" / "2980-most-frequent-german-nouns.json"
VERBS_JSON = BASE / "source" / "verbs" / "verbs-vocabulary.json"

IRREGULAR_INFINITIVES = frozenset({"sein", "haben", "werden", "tun"})


def is_verb_infinitive(de):
    """True if de is a single verb infinitive (or 'sich' + infinitive)."""
    if not de or not isinstance(de, str):
        return False
    s = de.strip()
    if not s:
        return False
    # Reflexive: "sich setzen" -> take "setzen"
    if s.lower().startswith("sich "):
        s = s[5:].strip()
    # Must be single word (no spaces, or we already stripped "sich ")
    if " " in s:
        return False
    w = s.lower()
    if w in IRREGULAR_INFINITIVES:
        return True
    if len(w) < 2:
        return False
    if w.endswith("en") or w.endswith("ern") or w.endswith("eln"):
        return True
    return False


def normalize_verb_de(de):
    """Return canonical infinitive (lowercase) for dedupe; strip 'sich '."""
    if not de:
        return ""
    s = de.strip()
    if s.lower().startswith("sich "):
        s = s[5:].strip()
    return s.lower()


def word_to_verb_entry(w, default_pronunciation=""):
    """Build verb entry: de, pronunciation, hi, en (verbs file order: de, pronunciation, hi, en)."""
    return {
        "de": w.get("de", "").strip(),
        "pronunciation": (w.get("pronunciation") or default_pronunciation).strip(),
        "hi": (w.get("hi") or "").strip(),
        "en": (w.get("en") or "").strip(),
    }


def extract_verbs_from_vocab(path, level, verb_category_ids=None):
    """
    Extract all verb entries from a vocabulary JSON.
    verb_category_ids: if set, only consider entries in these category ids as verbs for removal.
    Otherwise, scan all categories and remove any entry where is_verb_infinitive(de).
    Returns (list of verb entries with level, set of normalized verb stems for removal).
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    verbs_with_level = []
    for cat in data.get("categories", []):
        cid = cat.get("id", "")
        is_verb_category = verb_category_ids and cid in verb_category_ids
        for w in cat.get("words", []):
            de = (w.get("de") or "").strip()
            if not de:
                continue
            if is_verb_infinitive(de):
                verbs_with_level.append((level, word_to_verb_entry(w)))
            elif is_verb_category and de.lower().startswith("sich ") and is_verb_infinitive("sich " + de):
                # already covered
                pass
    return verbs_with_level


def collect_verbs_by_level():
    """Load A1, A2, B1 and collect (level, entry) for every verb."""
    a1_verbs = []
    a2_verbs = []
    b1_verbs = []

    with open(A1_JSON, "r", encoding="utf-8") as f:
        a1 = json.load(f)
    for cat in a1.get("categories", []):
        for w in cat.get("words", []):
            de = (w.get("de") or "").strip()
            if is_verb_infinitive(de):
                a1_verbs.append(word_to_verb_entry(w))

    with open(A2_JSON, "r", encoding="utf-8") as f:
        a2 = json.load(f)
    for cat in a2.get("categories", []):
        for w in cat.get("words", []):
            de = (w.get("de") or "").strip()
            if is_verb_infinitive(de):
                a2_verbs.append(word_to_verb_entry(w))

    with open(B1_JSON, "r", encoding="utf-8") as f:
        b1 = json.load(f)
    for cat in b1.get("categories", []):
        for w in cat.get("words", []):
            de = (w.get("de") or "").strip()
            if is_verb_infinitive(de):
                b1_verbs.append(word_to_verb_entry(w))

    return a1_verbs, a2_verbs, b1_verbs


def remove_verbs_from_vocab(path, verb_stems_to_remove, out_path):
    """Remove entries where normalize_verb_de(de) is in verb_stems_to_remove. Write to out_path."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    new_cats = []
    total = 0
    for cat in data.get("categories", []):
        new_words = []
        for w in cat.get("words", []):
            de = (w.get("de") or "").strip()
            if normalize_verb_de(de) in verb_stems_to_remove:
                continue
            new_words.append(w)
            total += 1
        new_cats.append({**cat, "words": new_words})
    data["categories"] = new_cats
    data["totalWords"] = total
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return total


def remove_verbs_from_2980(verb_stems_to_remove):
    """Remove entries from 2980 where de (lowercase) is in verb_stems_to_remove."""
    with open(NOUNS_2980_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    entries = data.get("entries", [])
    new_entries = [e for e in entries if normalize_verb_de(e.get("de") or "") not in verb_stems_to_remove]
    data["entries"] = new_entries
    with open(NOUNS_2980_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return len(new_entries)


def merge_verbs_into_file(a1_list, a2_list, b1_list):
    """
    Load verbs-vocabulary.json. Merge A1, A2, B1 lists into A1, A2, B1 categories (dedupe by de).
    Keep existing B2, C1, C2. Dedupe: no duplicate de (lowercase) across all levels; first occurrence wins.
    """
    with open(VERBS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    seen = set()
    level_lists = {"A1": [], "A2": [], "B1": []}
    cat_meta = {}

    def add_unique(level, entry):
        de = (entry.get("de") or "").strip()
        key = normalize_verb_de(de)
        if not key or key in seen:
            return
        seen.add(key)
        level_lists[level].append(entry)

    for cat in data.get("categories", []):
        cid = cat.get("id", "")
        cat_meta[cid] = cat
        if cid == "A1":
            for w in cat.get("words", []):
                add_unique("A1", word_to_verb_entry(w))
        elif cid == "A2":
            for w in cat.get("words", []):
                add_unique("A2", word_to_verb_entry(w))
        elif cid == "B1":
            for w in cat.get("words", []):
                add_unique("B1", word_to_verb_entry(w))
    for e in a1_list:
        add_unique("A1", e)
    for e in a2_list:
        add_unique("A2", e)
    for e in b1_list:
        add_unique("B1", e)

    # Rebuild categories: A1, A2, B1 from level_lists; then keep B2, C1, C2 from original
    new_categories = []
    for cat in data.get("categories", []):
        cid = cat.get("id", "")
        if cid == "A1":
            c = cat_meta.get("A1", cat)
            new_categories.append({
                "id": "A1",
                "name": "A1",
                "nameDe": c.get("nameDe", "Anfänger"),
                "nameHi": c.get("nameHi", "शुरुआत"),
                "emoji": c.get("emoji", "🟢"),
                "color": c.get("color", "#c8e6c9"),
                "words": level_lists["A1"],
            })
        elif cid == "A2":
            c = cat_meta.get("A2", cat)
            new_categories.append({
                "id": "A2",
                "name": "A2",
                "nameDe": c.get("nameDe", "Grundstufe"),
                "nameHi": c.get("nameHi", "बुनियादी"),
                "emoji": c.get("emoji", "🟡"),
                "color": c.get("color", "#fff9c4"),
                "words": level_lists["A2"],
            })
        elif cid == "B1":
            c = cat_meta.get("B1", cat)
            new_categories.append({
                "id": "B1",
                "name": "B1",
                "nameDe": c.get("nameDe", "Mittelstufe"),
                "nameHi": c.get("nameHi", "बीच का स्तर"),
                "emoji": c.get("emoji", "🟠"),
                "color": c.get("color", "#ffe0b2"),
                "words": level_lists["B1"],
            })
        else:
            new_categories.append(cat)

    total = sum(len(c.get("words", [])) for c in new_categories)
    data["categories"] = new_categories
    data["totalWords"] = total
    with open(VERBS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return total


def main():
    a1_verbs, a2_verbs, b1_verbs = collect_verbs_by_level()
    all_stems = set()
    for e in a1_verbs + a2_verbs + b1_verbs:
        all_stems.add(normalize_verb_de(e.get("de", "")))
    # Also include stems from existing verbs file so we remove them from 2980
    with open(VERBS_JSON, "r", encoding="utf-8") as f:
        vdata = json.load(f)
    for cat in vdata.get("categories", []):
        for w in cat.get("words", []):
            all_stems.add(normalize_verb_de(w.get("de", "")))

    remove_verbs_from_vocab(A1_JSON, all_stems, A1_JSON)
    remove_verbs_from_vocab(A2_JSON, all_stems, A2_JSON)
    remove_verbs_from_vocab(B1_JSON, all_stems, B1_JSON)
    remove_verbs_from_2980(all_stems)
    merge_verbs_into_file(a1_verbs, a2_verbs, b1_verbs)
    print("Verbs migrated: A1=%d, A2=%d, B1=%d" % (len(a1_verbs), len(a2_verbs), len(b1_verbs)))
    print("All verb stems (for removal): %d" % len(all_stems))


if __name__ == "__main__":
    main()
