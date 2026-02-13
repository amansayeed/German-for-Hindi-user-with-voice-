#!/usr/bin/env python3
"""
Build b1-vocabulary.json from Goethe B1 Wortliste (GitHub), excluding A1/A2 words.
- Fetches: https://raw.githubusercontent.com/kennethsible/goethe-wortliste/main/sorted.txt
- A1 words from source/a1-650/writing-data.json (all "de" values)
- A2 words from source/a2/a2.html (speakGerman('...') arguments)
- EN/HI from 2980 nouns and en_hi_extra where possible
"""
import json
import re
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
GOETHE_B1_URL = "https://raw.githubusercontent.com/kennethsible/goethe-wortliste/main/sorted.txt"
WRITING_DATA = REPO_ROOT / "a1-650" / "writing-data.json"
A2_HTML = REPO_ROOT / "a2" / "a2.html"
NOUNS_2980 = REPO_ROOT / "the-2980-most-frequently-used-german" / "2980-most-frequent-german-nouns.json"
EN_HI_EXTRA = REPO_ROOT / "the-2980-most-frequently-used-german" / "en_hi_extra.json"
OUT_JSON = SCRIPT_DIR / "b1-vocabulary.json"
B1_HTML = SCRIPT_DIR / "b1.html"
EMBED_PATTERN = re.compile(
    r'(<script type="application/json" id="b1-vocabulary-embed">).*?(</script>)',
    re.DOTALL,
)

# Category colors by letter (cycle)
CAT_COLORS = [
    "#e3f2fd", "#e8f5e9", "#fff3e0", "#f3e5f5", "#fce4ec",
    "#e0f7fa", "#f1f8e9", "#ede7f6", "#ffebee", "#e8eaf6",
]


def normalize_key(s):
    """Normalize for duplicate check: lowercase, strip."""
    if not s:
        return ""
    s = s.strip().lower()
    # Optional: strip leading article for noun comparison
    for art in ("der ", "die ", "das "):
        if s.startswith(art):
            return s[len(art):].strip()
    return s


def display_form(line):
    """Goethe line -> display string (before first comma)."""
    line = line.strip()
    if not line:
        return ""
    idx = line.find(",")
    return line[:idx].strip() if idx > 0 else line


def key_from_display(display):
    """One normalized key for display form (for A1/A2/B1 set membership)."""
    k = normalize_key(display)
    # Also add without article for nouns
    for art in ("der ", "die ", "das "):
        if k.startswith(art):
            return k[len(art):].strip()
    return k


def load_a1_words():
    a1 = set()
    if not WRITING_DATA.exists():
        return a1
    with open(WRITING_DATA, "r", encoding="utf-8") as f:
        data = json.load(f)
    for category_entries in data.values():
        for item in category_entries:
            if isinstance(item, dict) and "de" in item:
                d = item["de"].strip()
                if d:
                    a1.add(key_from_display(d))
                    a1.add(normalize_key(d))
    return a1


def load_a2_words():
    a2 = set()
    if not A2_HTML.exists():
        return a2
    with open(A2_HTML, "r", encoding="utf-8") as f:
        text = f.read()
    for m in re.finditer(r"speakGerman\s*\(\s*['\"]([^'\"]+)['\"]", text):
        d = m.group(1).strip()
        if d:
            a2.add(key_from_display(d))
            a2.add(normalize_key(d))
    return a2


def load_goethe_b1():
    """Fetch Goethe B1 sorted list and return list of display forms (no duplicates, no A1/A2)."""
    a1 = load_a1_words()
    a2 = load_a2_words()
    try:
        with urllib.request.urlopen(GOETHE_B1_URL, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except Exception as e:
        # Fallback: local file if present
        local = SCRIPT_DIR / "goethe-b1-sorted.txt"
        if local.exists():
            with open(local, "r", encoding="utf-8") as f:
                raw = f.read()
        else:
            raise SystemExit(f"Could not fetch Goethe B1 list and no local file: {e}")
    seen = set()
    b1_only = []
    for line in raw.splitlines():
        display = display_form(line)
        if not display:
            continue
        key = key_from_display(display)
        if key in seen:
            continue
        if key in a1 or key in a2:
            continue
        seen.add(key)
        b1_only.append(display)
    return b1_only


def load_de_to_en_hi():
    """Build map: normalized German (lowercase, no article) -> { en, hi }."""
    de_map = {}
    if NOUNS_2980.exists():
        with open(NOUNS_2980, "r", encoding="utf-8") as f:
            data = json.load(f)
        for e in data.get("entries", []):
            de = e.get("de") or ""
            en = e.get("en") or ""
            hi = e.get("hi") or ""
            art = (e.get("article") or "").strip()
            if de:
                # "der Mann" and "mann" both map to en, hi
                full = f"{art} {de}".strip() if art else de
                k = normalize_key(full)
                de_map[k] = {"en": en, "hi": hi}
                de_map[de.lower()] = {"en": en, "hi": hi}
    if EN_HI_EXTRA.exists():
        with open(EN_HI_EXTRA, "r", encoding="utf-8") as f:
            en_hi = json.load(f)
        # en_hi is English -> Hindi; we can't map DE -> EN from this alone, so skip for lookup
        pass
    return de_map


def build_categories(b1_words, de_to_en_hi):
    """Build one category with all B1 words (like A1-650 page), not by letter A,B,C."""
    words = []
    for display in b1_words:
        en = ""
        hi = ""
        key = key_from_display(display)
        if key in de_to_en_hi:
            en = de_to_en_hi[key].get("en", "")
            hi = de_to_en_hi[key].get("hi", "")
        if not en:
            en = display  # show German if no translation
        words.append({
            "de": display,
            "pronunciation": "",
            "hi": hi,
            "en": en,
        })
    words.sort(key=lambda w: (w.get("de") or "").lower())
    categories = [
        {
            "id": "B1_Wortliste",
            "name": "B1 Wortliste",
            "nameDe": "Goethe B1 Wortliste",
            "nameHi": "B1 शब्दावली",
            "emoji": "📖",
            "color": CAT_COLORS[0],
            "words": words,
        }
    ]
    return categories


def main():
    print("Loading A1/A2 exclusion sets...")
    b1_words = load_goethe_b1()
    print(f"B1-only words from Goethe list: {len(b1_words)}")
    print("Loading DE->EN/HI from 2980 nouns...")
    de_to_en_hi = load_de_to_en_hi()
    print("Building categories...")
    categories = build_categories(b1_words, de_to_en_hi)
    total = sum(len(c["words"]) for c in categories)
    out = {
        "title": "German B1 Vocabulary",
        "subtitle": "Goethe-Zertifikat B1 Wortliste (excluding A1/A2). Complete list from official source.",
        "totalWords": total,
        "categories": categories,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Wrote {OUT_JSON} with {total} words in {len(categories)} categories.")

    # Embed JSON into b1.html so the page works when opened via file:// (no fetch)
    if B1_HTML.exists():
        json_str = json.dumps(out, ensure_ascii=False, indent=2)
        # Prevent </script> in JSON from closing the script tag in HTML
        json_str = json_str.replace("</", "<\\/")
        with open(B1_HTML, "r", encoding="utf-8") as f:
            html = f.read()
        if EMBED_PATTERN.search(html):
            html = EMBED_PATTERN.sub(r"\1" + json_str + r"\2", html, count=1)
            with open(B1_HTML, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Embedded vocabulary into {B1_HTML}.")
        else:
            print(f"Warning: b1-vocabulary-embed script block not found in {B1_HTML}, skip embed.")


if __name__ == "__main__":
    main()
