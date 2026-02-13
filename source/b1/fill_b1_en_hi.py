#!/usr/bin/env python3
"""
Fill missing 'en' and 'hi' for all words in b1-vocabulary.json.
1. Build lookup from 2980 nouns, writing-data.json (A1), and en_hi_extra (en->hi).
2. Fill from lookup where possible.
3. For remaining, use googletrans (de->en, en->hi) with cache b1_translation_cache.json.
"""
import json
import re
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parent.parent
B1_JSON = SCRIPT_DIR / "b1-vocabulary.json"
CACHE_JSON = SCRIPT_DIR / "b1_translation_cache.json"
NOUNS_2980 = REPO / "the-2980-most-frequently-used-german" / "2980-most-frequent-german-nouns.json"
WRITING_DATA = REPO / "a1-650" / "writing-data.json"
EN_HI_EXTRA = REPO / "the-2980-most-frequently-used-german" / "en_hi_extra.json"


def normalize_key(s):
    if not s:
        return ""
    s = s.strip().lower()
    for art in ("der ", "die ", "das "):
        if s.startswith(art):
            return s[len(art) :].strip()
    return s


def key_from_display(display):
    k = normalize_key(display)
    for art in ("der ", "die ", "das "):
        if k.startswith(art):
            return k[len(art) :].strip()
    return k


def load_lookup():
    """Build de_key -> { en, hi } from 2980, writing-data, en_hi_extra (en->hi only)."""
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
                    if key and (key not in de_map or not de_map[key].get("hi")):
                        de_map[key] = {"en": en or de_map.get(key, {}).get("en", ""), "hi": hi or de_map.get(key, {}).get("hi", "")}

    en_hi_extra = {}
    if EN_HI_EXTRA.exists():
        with open(EN_HI_EXTRA, "r", encoding="utf-8") as f:
            en_hi_extra = {k.lower(): v for k, v in json.load(f).items()}
    else:
        en_hi_extra = {}

    return de_map, en_hi_extra


def main():
    with open(B1_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    de_map, en_hi_extra = load_lookup()
    cache = {}
    if CACHE_JSON.exists():
        try:
            with open(CACHE_JSON, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            pass

    updated = 0
    need_translate = []  # list of (cat_idx, word_idx, key) for missing en/hi

    for ci, cat in enumerate(data.get("categories", [])):
        for wi, w in enumerate(cat.get("words", [])):
            de = (w.get("de") or "").strip()
            key = key_from_display(de)
            en = (w.get("en") or "").strip()
            hi = (w.get("hi") or "").strip()

            # Prefer lookup
            if key in de_map:
                en2 = (de_map[key].get("en") or "").strip()
                hi2 = (de_map[key].get("hi") or "").strip()
                if en2:
                    en = en2
                if hi2:
                    hi = hi2
            # If we have en but no hi, try en_hi_extra
            if en and not hi and en.lower() in en_hi_extra:
                hi = en_hi_extra[en.lower()]

            # Cache (from previous run)
            if (not en or en == de) and key in cache:
                if cache[key].get("en"):
                    en = cache[key]["en"]
                if cache[key].get("hi"):
                    hi = cache[key]["hi"]

            if not en:
                en = de
            if not hi and en and en.lower() in en_hi_extra:
                hi = en_hi_extra[en.lower()]

            if (not hi or en == de) and key not in cache:
                need_translate.append((ci, wi, key, de))

            old_en, old_hi = w.get("en"), w.get("hi")
            w["en"] = en
            w["hi"] = hi
            if en != old_en or hi != old_hi:
                updated += 1

    # Translate missing via deep-translator (de->en, de->hi)
    n_need = len(need_translate)
    if n_need:
        try:
            from deep_translator import GoogleTranslator
            trans_en = GoogleTranslator(source="de", target="en")
            trans_hi = GoogleTranslator(source="de", target="hi")
            print(f"Translating {n_need} words (de->en, de->hi)...")
            for i, (ci, wi, key, de) in enumerate(need_translate):
                if key in cache:
                    en = (cache[key].get("en") or "").strip()
                    hi = (cache[key].get("hi") or "").strip()
                else:
                    en, hi = "", ""
                    try:
                        en = (trans_en.translate(de) or "").strip()
                        if not en:
                            en = de
                        if en.lower() in en_hi_extra:
                            hi = en_hi_extra[en.lower()]
                        if not hi:
                            hi = (trans_hi.translate(de) or "").strip()
                        cache[key] = {"en": en, "hi": hi or ""}
                    except Exception as e:
                        print(f"  skip {de!r}: {e}")
                        cache[key] = {"en": en or de, "hi": hi or ""}
                    time.sleep(0.15)
                data["categories"][ci]["words"][wi]["en"] = en or data["categories"][ci]["words"][wi]["en"]
                data["categories"][ci]["words"][wi]["hi"] = hi or data["categories"][ci]["words"][wi]["hi"]
                updated += 1
                if (i + 1) % 100 == 0:
                    with open(CACHE_JSON, "w", encoding="utf-8") as f:
                        json.dump(cache, f, ensure_ascii=False, indent=2)
                    with open(B1_JSON, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"  {i + 1}/{n_need} done, saved")
            with open(CACHE_JSON, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except ImportError:
            print("Tip: pip install deep-translator to fill remaining words via translation.")

    with open(B1_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Updated {B1_JSON}. Filled/updated {updated} entries. Cache: {len(cache)} keys.")


if __name__ == "__main__":
    main()
