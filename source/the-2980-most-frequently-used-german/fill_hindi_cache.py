#!/usr/bin/env python3
"""Fill en_hi_cache.json with Hindi for all words in missing_hi_words.txt using googletrans."""
import json
import os
import time

BASE = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(BASE, "en_hi_cache.json")
MISSING_PATH = os.path.join(BASE, "missing_hi_words.txt")

def main():
    cache = {}
    if os.path.isfile(CACHE_PATH):
        try:
            with open(CACHE_PATH, encoding="utf-8") as f:
                cache = json.load(f)
            print(f"Loaded cache: {len(cache)} entries")
        except Exception as e:
            print("Cache load failed:", e)
    with open(MISSING_PATH, encoding="utf-8") as f:
        lines = f.readlines()
    count_line = lines[0].strip()
    try:
        n = int(count_line)
        words = [w.strip().lower() for w in lines[1:1+n] if w.strip()]
    except ValueError:
        words = [w.strip().lower() for w in lines[1:] if w.strip()]
    need = [w for w in words if w and w not in cache]
    print(f"Words needing translation: {len(need)}")
    if not need:
        print("Cache complete.")
        return
    try:
        from googletrans import Translator
        translator = Translator()
        for i, en in enumerate(need):
            try:
                r = translator.translate(en, src="en", dest="hi")
                if r and r.text:
                    cache[en] = r.text
                if (i + 1) % 50 == 0:
                    with open(CACHE_PATH, "w", encoding="utf-8") as f:
                        json.dump(cache, f, ensure_ascii=False, indent=0)
                    print(f"  {i + 1}/{len(need)} done, cache saved")
                time.sleep(0.25)
            except Exception as e:
                print(f"  skip {en}: {e}")
                time.sleep(1)
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=0)
        print(f"Saved cache: {len(cache)} entries")
    except ImportError:
        print("Install: pip install googletrans==4.0.0-rc1")

if __name__ == "__main__":
    main()
