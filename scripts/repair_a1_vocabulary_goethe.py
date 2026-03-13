# -*- coding: utf-8 -*-
"""
Repair A1 vocabulary JSON: one entry = one vocab item, correct forms,
no sentences (convert to verb/noun/adj), strip emojis from en, add pronunciation,
deduplicate, add article for naked nouns. Keep schema and categories.
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
A1_JSON = BASE / "source" / "a1-650" / "a1-vocabulary.json"

# Sentence/phrase entries to REMOVE (we have or add the single-word form)
REMOVE_DE = frozenset({
    "Es regnet", "Es schneit", "Die Sonne scheint",
    "Das Wetter ist schön", "Das Wetter ist schlecht", "Es ist heiß/kalt", "Es sind 20 Grad",
    "Ich verstehe nicht", "Ich weiß nicht", "Ich verstehe (nicht)", "Ich lerne Deutsch",
    "Das schmeckt gut!", "Es ist lecker!", "Ich bin satt",
    "Das passt mir (nicht)", "Das steht dir gut!",
    "Langsam, bitte",  # → single word "langsam" exists
})

# Optional: keep some as expressions in Greetings (Mir geht es gut, Es geht, Danke gut, etc.)
# We do NOT remove: "Mir geht es gut", "Es geht", "Danke, gut", "Es tut mir leid", "Was ist los?", etc.

# Words to normalize: (sich) → sich verb
def normalize_de(de):
    if not de:
        return de
    de = de.strip()
    m = re.match(r"^(.+?)\s*\(sich\)\s*$", de)
    if m:
        return "sich " + m.group(1).strip()
    return de

# Nouns without article → with article
NOUN_ARTICLE = {"Herr": "der Herr", "Frau": "die Frau"}

# Add missing verb when we remove a sentence
ADD_VERB = {"scheinen": ("to shine", "चमकना")}  # from "Die Sonne scheint"

def simple_pronunciation(de):
    if not de or " " in de:
        return ""
    s = de
    s = s.replace("ch", "kh").replace("sch", "sh").replace("ä", "eh").replace("ö", "oe").replace("ü", "ue")
    s = s.replace("ß", "ss")
    if len(s) >= 4:
        return (s[:2] + "-" + s[2:]).upper()
    return s.upper()

# Remove emojis from string (common ranges)
def strip_emojis(s):
    if not s:
        return s
    s = str(s)
    # Remove emoji (symbols, pictographs, etc.)
    s = re.sub(r"[\U0001F300-\U0001F9FF]", "", s)  # Misc Symbols and Pictographs
    s = re.sub(r"[\U00002600-\U000027BF]", "", s)  # Misc symbols
    s = re.sub(r"[\U0001F600-\U0001F64F]", "", s)  # Emoticons
    s = re.sub(r"[\U0001F1E0-\U0001F1FF]", "", s)  # Flags
    s = re.sub(r"[\u2600-\u26FF]", "", s)
    s = re.sub(r"[\u2700-\u27BF]", "", s)
    s = re.sub(r"[\uFE00-\uFE0F]", "", s)  # Variation selectors
    s = re.sub(r"\s+", " ", s).strip()
    return s


def main():
    with open(A1_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    seen_global = set()
    total_added = 0
    verbs_cat_id = "Verbs_(Actions)"

    for cat in data.get("categories", []):
        words = cat.get("words", [])
        new_words = []
        for w in words:
            de = (w.get("de") or "").strip()
            if not de:
                continue
            if de in REMOVE_DE:
                continue
            de = normalize_de(de)
            if de in NOUN_ARTICLE:
                de = NOUN_ARTICLE[de]
            en = strip_emojis(w.get("en") or "")
            hi = (w.get("hi") or "").strip()
            if de in seen_global:
                continue
            seen_global.add(de)
            pron = simple_pronunciation(de) if de and " " not in de else ""
            new_words.append({
                "de": de,
                "pronunciation": pron,
                "en": en or "—",
                "hi": hi or "—",
            })
        cat["words"] = new_words

    # Add missing verb "scheinen" to Verbs_(Actions) if not present
    if "scheinen" not in seen_global and ADD_VERB:
        for cat in data.get("categories", []):
            if (cat.get("id") or "") == verbs_cat_id:
                en, hi = ADD_VERB["scheinen"]
                cat["words"].append({
                    "de": "scheinen",
                    "pronunciation": "SHAI-nen",
                    "en": en,
                    "hi": hi,
                })
                total_added += 1
                break

    total_words = sum(len(c.get("words", [])) for c in data.get("categories", []))
    data["totalWords"] = total_words
    data["subtitle"] = f"A1 vocabulary ({total_words} words). German, English, Hindi. Goethe A1."

    with open(A1_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Repair done. Total words:", total_words)
    print("Added (e.g. scheinen):", total_added)


if __name__ == "__main__":
    main()
