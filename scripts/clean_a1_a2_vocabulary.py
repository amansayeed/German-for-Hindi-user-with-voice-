# -*- coding: utf-8 -*-
"""
Deep clean A1 and A2 vocabulary JSON:
- A1: one entry = one item, base forms, pronunciation, no emojis, dedupe, nouns with article.
- A2: remove any word already in A1; phrases to base; fix categories; dedupe.
- Recalculate totalWords; keep JSON schema.
"""
import json
import re
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent
A1_JSON = BASE / "source" / "a1-650" / "a1-vocabulary.json"
A2_JSON = BASE / "source" / "a2" / "a2-vocabulary.json"


def normalize_for_overlap(de):
    """Single key for overlap check: noun stem or lowercased form."""
    if not de:
        return ""
    s = de.strip().lower()
    for prefix in ("der ", "die ", "das "):
        if s.startswith(prefix):
            return s[len(prefix):].strip()
    return s


def simple_pronunciation(de):
    if not de or " " in de:
        return ""
    s = de.replace("ch", "kh").replace("sch", "sh").replace("ä", "eh").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    if len(s) >= 4:
        return (s[:2] + "-" + s[2:]).upper()
    return s.upper()


def strip_emojis(s):
    if not s:
        return s
    s = str(s)
    s = re.sub(r"[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F600-\U0001F64F\U0001F1E0-\U0001F1FF\u2600-\u26FF\u2700-\u27BF\uFE00-\uFE0F]", "", s)
    return re.sub(r"\s+", " ", s).strip()


# ---- A1: sentences/phrases to remove (base form exists elsewhere) ----
A1_REMOVE = frozenset({
    "Es regnet", "Es schneit", "Die Sonne scheint",
    "Das Wetter ist schön", "Das Wetter ist schlecht", "Es ist heiß/kalt", "Es sind 20 Grad",
    "Ich verstehe nicht", "Ich weiß nicht", "Ich verstehe (nicht)", "Ich lerne Deutsch",
    "Das schmeckt gut!", "Es ist lecker!", "Ich bin satt",
    "Das passt mir (nicht)", "Das steht dir gut!", "Langsam, bitte",
})

# A1: conjugated -> infinitive (if any)
A1_CONJUGATED = {"mache": "machen", "macht": "machen", "machst": "machen", "gehe": "gehen", "geht": "gehen", "gehst": "gehen"}

# A1: noun without article
A1_NOUN_ARTICLE = {"Herr": "der Herr", "Frau": "die Frau"}

# A1: (sich) -> sich verb
def a1_normalize_de(de):
    if not de:
        return de
    de = de.strip()
    if de in A1_CONJUGATED:
        return A1_CONJUGATED[de]
    if de in A1_NOUN_ARTICLE:
        return A1_NOUN_ARTICLE[de]
    m = re.match(r"^(.+?)\s*\(sich\)\s*$", de)
    if m:
        return "sich " + m.group(1).strip()
    return de


def clean_a1(data):
    seen = set()
    out_cats = []
    for cat in data.get("categories", []):
        new_words = []
        for w in cat.get("words", []):
            de = (w.get("de") or "").strip()
            if not de or de in A1_REMOVE:
                continue
            de = a1_normalize_de(de)
            if normalize_for_overlap(de) in seen:
                continue
            seen.add(normalize_for_overlap(de))
            en = strip_emojis(w.get("en") or "")
            hi = (w.get("hi") or "").strip()
            pron = w.get("pronunciation") or ""
            if not pron and de and " " not in de:
                pron = simple_pronunciation(de)
            new_words.append({"de": de, "pronunciation": pron or "", "en": en or "—", "hi": hi or "—"})
        out_cats.append({**cat, "words": new_words})
    total = sum(len(c["words"]) for c in out_cats)
    return {"title": data.get("title", "German A1 Vocabulary"), "subtitle": f"A1 vocabulary ({total} words). German, English, Hindi. Goethe A1.", "totalWords": total, "categories": out_cats}


# ---- A2: phrases -> base ----
A2_PHRASE_TO_BASE = {
    "Instrument spielen": "spielen",
    "die Pause machen": "pausieren",
    "schlafen gehen": "schlafen gehen",  # keep as phrase or use "einschlafen"? Keep.
    "schwimmen gehen": "schwimmen gehen",
    "spazieren gehen": "spazieren gehen",
}
# Verbs that must be in Verbs category (move from Pronouns etc.)
A2_VERBS = frozenset({"sein", "haben", "werden", "machen", "können", "müssen", "sollen", "dürfen", "mögen", "wollen", "möchten"})


def clean_a2(data, a1_normalized_set):
    seen = set()
    out_cats = []
    sein_entry = None
    for cat in data.get("categories", []):
        cid = (cat.get("id") or "").strip()
        new_words = []
        for w in cat.get("words", []):
            de = (w.get("de") or "").strip()
            if not de:
                continue
            if cid == "Pronouns" and normalize_for_overlap(de) == "sein":
                sein_entry = {**w, "de": "sein", "pronunciation": w.get("pronunciation") or "ZAI-n", "en": strip_emojis(w.get("en") or "") or "to be", "hi": (w.get("hi") or "").strip() or "होना"}
                continue
            base_de = A2_PHRASE_TO_BASE.get(de, de)
            if base_de != de:
                de = base_de
            norm = normalize_for_overlap(de)
            if norm in a1_normalized_set:
                continue
            if norm in seen:
                continue
            seen.add(norm)
            en = strip_emojis(w.get("en") or "")
            hi = (w.get("hi") or "").strip()
            pron = w.get("pronunciation") or ""
            if not pron and de and " " not in de:
                pron = simple_pronunciation(de)
            new_words.append({"de": de, "pronunciation": pron or "", "en": en or "—", "hi": hi or "—"})
        out_cats.append({**cat, "words": new_words})
    if sein_entry:
        for c in out_cats:
            if (c.get("id") or "") == "Verbs":
                if not any(normalize_for_overlap(w.get("de") or "") == "sein" for w in c["words"]):
                    c["words"].insert(0, sein_entry)
                break
    total = sum(len(c["words"]) for c in out_cats)
    return {"title": data.get("title", "German A2 Vocabulary"), "subtitle": "Goethe-Zertifikat A2. Only words not in A1. Base forms.", "totalWords": total, "categories": out_cats}


def main():
    with open(A1_JSON, "r", encoding="utf-8") as f:
        a1 = json.load(f)
    with open(A2_JSON, "r", encoding="utf-8") as f:
        a2 = json.load(f)

    a1_cleaned = clean_a1(a1)
    a1_norm_set = set()
    for cat in a1_cleaned["categories"]:
        for w in cat["words"]:
            a1_norm_set.add(normalize_for_overlap(w.get("de") or ""))

    a2_cleaned = clean_a2(a2, a1_norm_set)

    with open(A1_JSON, "w", encoding="utf-8") as f:
        json.dump(a1_cleaned, f, ensure_ascii=False, indent=2)
    with open(A2_JSON, "w", encoding="utf-8") as f:
        json.dump(a2_cleaned, f, ensure_ascii=False, indent=2)

    print("A1 totalWords:", a1_cleaned["totalWords"])
    print("A2 totalWords:", a2_cleaned["totalWords"])


if __name__ == "__main__":
    main()
