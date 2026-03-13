# -*- coding: utf-8 -*-
"""
Fix A2 vocabulary JSON as a German teacher:
- Fix incorrect German words (typos, wrong forms)
- Normalize to base form: infinitive for verbs, article+noun for nouns where needed
- Remove duplicate entries (no repeated "de" within each category)
- Remove Perfekt/Präteritum-only entries (hat X, ist X) when the infinitive exists
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
A2_JSON = BASE / "source" / "a2" / "a2-vocabulary.json"

# Typos and wrong words: wrong -> correct
TYPO_FIXES = {
    "sichüber": "sich über",
    "ander": "andere",
    "tschüs": "tschüss",
    "tung": "-ung (Suffix)",
    "wer wen": "wer / wen",
    "an, ausgezogen": "angezogen, ausgezogen",
}

# Conjugated verb (or phrase) -> infinitive / base form (for Verbs/Vocabulary)
CONJUGATED_TO_INFINITIVE = {
    "tauscht": "tauschen",
    "trifft": "treffen",
    "träumt": "träumen",
    "wartet": "warten",
    "zieht": "ziehen",
    "besichtigt": "besichtigen",
    "besteht": "bestehen",
    "bestellt": "bestellen",
    "besucht": "besuchen",
    "bewirbt": "sich bewerben",
    "duscht": "duschen",
    "erinnert": "erinnern",
    "unterhält": "unterhalten",
    "untersucht": "untersuchen",
    "vergisst": "vergessen",
    "verletzt": "verletzen",
    "verliert": "verlieren",
    "versteht": "verstehen",
    "versucht": "versuchen",
    "ärgert": "ärgern",
    "informiert": "informieren",
    "kontrolliert": "kontrollieren",
    "organisiert": "organisieren",
    "reserviert": "reservieren",
    "reservierte": "reservieren",
    "sieht aus": "aussehen",
    "lernt kennen": "kennen lernen",
}


def is_perfekt_or_prateritum(de: str) -> bool:
    """True if entry is a Perfekt (hat/ist + participle) or similar compound form we want to drop."""
    if not de or not isinstance(de, str):
        return False
    s = de.strip()
    if re.match(r"^hat\s+", s) or re.match(r"^ist\s+", s):
        return True
    if re.match(r"^hat,\s*ist\s+", s) or re.match(r"^ist,\s*hat\s+", s):
        return True
    return False


def apply_fixes(de: str) -> str:
    """Apply typo fixes and conjugated -> infinitive."""
    if not de or not isinstance(de, str):
        return de
    s = de.strip()
    s = TYPO_FIXES.get(s, s)
    s = CONJUGATED_TO_INFINITIVE.get(s, s)
    return s


def main():
    with open(A2_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_removed = 0
    total_fixed = 0
    total_dup_removed = 0

    for cat in data.get("categories", []):
        words = cat.get("words", [])
        seen = {}
        new_words = []

        for w in words:
            de = (w.get("de") or "").strip()
            if not de:
                continue

            # Drop Perfekt/Präteritum-only forms (infinitive is the base form)
            if is_perfekt_or_prateritum(de):
                total_removed += 1
                continue

            # Apply typo and conjugated -> infinitive
            fixed_de = apply_fixes(de)
            if fixed_de != de:
                total_fixed += 1
                w = {**w, "de": fixed_de}
                de = fixed_de

            # Deduplicate: keep first occurrence
            key = de
            if key in seen:
                total_dup_removed += 1
                continue
            seen[key] = True
            new_words.append(w)

        cat["words"] = new_words

    # Update totalWords
    total_words = sum(len(c.get("words", [])) for c in data.get("categories", []))
    data["totalWords"] = total_words

    with open(A2_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Done. Removed Perfekt/ist forms:", total_removed)
    print("Fixed (typo/conjugated->infinitive):", total_fixed)
    print("Duplicate entries removed:", total_dup_removed)
    print("Total words now:", total_words)


if __name__ == "__main__":
    main()
