#!/usr/bin/env python3
"""
Finalize B1 vocabulary: ensure every word has non-empty 'en' and 'hi'.
- Uses 2980 nouns + A1 writing-data + en_hi_extra for best mappings.
- If still missing, falls back to English meaning for Hindi (hi = en).
"""
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parent.parent
B1_JSON = SCRIPT_DIR / "b1-vocabulary.json"
NOUNS_2980 = REPO / "the-2980-most-frequently-used-german" / "2980-most-frequent-german-nouns.json"
WRITING_DATA = REPO / "a1-650" / "writing-data.json"
EN_HI_EXTRA = REPO / "the-2980-most-frequently-used-german" / "en_hi_extra.json"


def normalize_key(s: str) -> str:
    if not s:
        return ""
    s = s.strip().lower()
    for art in ("der ", "die ", "das "):
        if s.startswith(art):
            return s[len(art) :].strip()
    return s


def key_from_display(display: str) -> str:
    return normalize_key(display)


def load_de_map():
    de_map = {}
    if NOUNS_2980.exists():
        with open(NOUNS_2980, "r", encoding="utf-8") as f:
            data = json.load(f)
        for e in data.get("entries", []):
            de = (e.get("de") or "").strip()
            en = (e.get("en") or "").strip()
            hi = (e.get("hi") or "").strip()
            if not de:
                continue
            art = (e.get("article") or "").strip()
            full = f"{art} {de}".strip() if art else de
            for key in (normalize_key(full), de.lower(), key_from_display(full)):
                if key and key not in de_map:
                    de_map[key] = {"en": en, "hi": hi}
    if WRITING_DATA.exists():
        with open(WRITING_DATA, "r", encoding="utf-8") as f:
            data = json.load(f)
        for cat_entries in data.values():
            for item in cat_entries:
                if not isinstance(item, dict):
                    continue
                de = (item.get("de") or "").strip()
                en = (item.get("en") or "").strip()
                hi = (item.get("hi") or "").strip()
                if not de:
                    continue
                for key in (normalize_key(de), de.lower(), key_from_display(de)):
                    if not key:
                        continue
                    cur = de_map.get(key, {})
                    if key not in de_map:
                        de_map[key] = {"en": en, "hi": hi}
                    else:
                        if en and not cur.get("en"):
                            cur["en"] = en
                        if hi and not cur.get("hi"):
                            cur["hi"] = hi
                        de_map[key] = cur
    en_hi_extra = {}
    if EN_HI_EXTRA.exists():
        with open(EN_HI_EXTRA, "r", encoding="utf-8") as f:
            en_hi_extra = {k.lower(): v for k, v in json.load(f).items()}
    return de_map, en_hi_extra


def main():
    with open(B1_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    de_map, en_hi_extra = load_de_map()
    changed = 0
    total = 0

    for cat in data.get("categories", []):
        for w in cat.get("words", []):
            total += 1
            de = (w.get("de") or "").strip()
            key = key_from_display(de)
            en = (w.get("en") or "").strip()
            hi = (w.get("hi") or "").strip()
            old_en, old_hi = en, hi

            if key in de_map:
                if de_map[key].get("en"):
                    en = de_map[key]["en"]
                if de_map[key].get("hi"):
                    hi = de_map[key]["hi"]

            if en and not hi and en.lower() in en_hi_extra:
                hi = en_hi_extra[en.lower()]

            if not en:
                en = de
            if not hi:
                # Last fallback: reuse English meaning so field is never empty
                hi = en

            w["en"] = en
            w["hi"] = hi
            if en != old_en or hi != old_hi:
                changed += 1

    with open(B1_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Finalized {B1_JSON}: {changed} of {total} entries updated.")


if __name__ == "__main__":
    main()

