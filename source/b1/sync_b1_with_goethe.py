#!/usr/bin/env python3
"""
Sync b1-vocabulary.json with the Goethe B1 Wortliste source (PDF transcript).
Official PDF: https://www.goethe.de/pro/relaunch/prf/en/Goethe-Zertifikat_B1_Wortliste.pdf
GitHub transcript: https://raw.githubusercontent.com/kennethsible/goethe-wortliste/main/sorted.txt

- Fetches the full Goethe B1 list (sorted.txt, excluding A1/A2 same as build_b1_vocabulary).
- Optionally: pass --pdf path/to/Wortliste.pdf to also extract headwords from the PDF and add any missing.
- Loads current b1-vocabulary.json and collects all "de" keys.
- Adds any word from the source that is not yet in the JSON.
- Writes back a single-category JSON (all words), then run build_b1_themes.py and embed_b1_data.py.
"""
import argparse
import json
import re
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
GOETHE_B1_URL = "https://raw.githubusercontent.com/kennethsible/goethe-wortliste/main/sorted.txt"
WRITING_DATA = REPO_ROOT / "a1-650" / "writing-data.json"
A2_HTML = REPO_ROOT / "a2" / "a2.html"
B1_JSON = SCRIPT_DIR / "b1-vocabulary.json"


def normalize_key(s):
    if not s:
        return ""
    s = s.strip().lower()
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
    k = normalize_key(display)
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


def load_goethe_b1_raw():
    """Fetch full Goethe list and return list of display forms (exclude A1/A2, no duplicates)."""
    a1 = load_a1_words()
    a2 = load_a2_words()
    try:
        with urllib.request.urlopen(GOETHE_B1_URL, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
    except Exception as e:
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


def extract_headwords_from_pdf(pdf_path):
    """Extract German headwords from Goethe B1 PDF (optional, requires pypdf)."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("Install pypdf to use PDF extraction: pip install pypdf")
        return []
    headwords = []
    reader = PdfReader(pdf_path)
    # Pattern: line starting with optional article (der/die/das) + word, or lowercase word; may have comma
    head_re = re.compile(
        r"^(?:(?:der|die|das)\s+)?"
        r"([A-Za-zÄäÖöÜüß][A-Za-zÄäÖöÜüß\s\-]+?)(?:\s*,\s*|\s*$)",
        re.MULTILINE,
    )
    for page in reader.pages:
        text = page.extract_text()
        if not text:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line or len(line) < 2:
                continue
            # Take first token or "article + noun" as display form (before comma if any)
            idx = line.find(",")
            if idx > 0:
                display = line[:idx].strip()
            else:
                display = line.split()[0] if line.split() else line
            if display and display[0].isalpha() and len(display) > 1:
                headwords.append(display)
    return headwords


def main():
    parser = argparse.ArgumentParser(description="Sync B1 vocabulary with Goethe B1 Wortliste source.")
    parser.add_argument("--pdf", type=str, help="Optional: path to Goethe-Zertifikat_B1_Wortliste.pdf to add any words from PDF not in GitHub list")
    args = parser.parse_args()

    print("Loading A1/A2 exclusions...")
    goethe_b1 = set(load_goethe_b1_raw())
    print(f"Goethe B1 list from GitHub (excl. A1/A2): {len(goethe_b1)} words")

    if args.pdf:
        pdf_path = Path(args.pdf)
        if pdf_path.exists():
            extra = extract_headwords_from_pdf(str(pdf_path))
            a1, a2 = load_a1_words(), load_a2_words()
            for h in extra:
                if not h or len(h) < 2:
                    continue
                key = key_from_display(h)
                if key in a1 or key in a2:
                    continue
                goethe_b1.add(h)
            print(f"After PDF: {len(goethe_b1)} words in source set.")
        else:
            print(f"PDF not found: {pdf_path}")

    goethe_b1 = sorted(goethe_b1, key=lambda x: x.lower())

    print("Loading current b1-vocabulary.json...")
    with open(B1_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_words = []
    for cat in data["categories"]:
        all_words.extend(cat["words"])

    keys_in_json = set()
    for w in all_words:
        de = (w.get("de") or "").strip()
        if de:
            keys_in_json.add(key_from_display(de))
            keys_in_json.add(normalize_key(de))

    missing = []
    for display in goethe_b1:
        key = key_from_display(display)
        if key not in keys_in_json:
            missing.append(display)
            keys_in_json.add(key)

    if not missing:
        print("All words from the Goethe B1 source are already in b1-vocabulary.json.")
        return

    print(f"Adding {len(missing)} missing words from the source...")
    for display in missing:
        all_words.append({
            "de": display,
            "pronunciation": "",
            "hi": "",
            "en": display,
        })

    # Sort by German (case-insensitive)
    all_words.sort(key=lambda w: (w.get("de") or "").lower())

    # Write back as single category so build_b1_themes can re-categorize
    out = {
        "title": data.get("title", "German B1 Vocabulary"),
        "subtitle": "Goethe-Zertifikat B1 Wortliste (excluding A1/A2). Synced with official source.",
        "totalWords": len(all_words),
        "categories": [
            {
                "id": "B1_Wortliste",
                "name": "B1 Wortliste",
                "nameDe": "Goethe B1 Wortliste",
                "nameHi": "B1 शब्दावली",
                "emoji": "📖",
                "color": "#e3f2fd",
                "words": all_words,
            }
        ],
    }
    with open(B1_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Wrote {B1_JSON} with {len(all_words)} words (single category).")
    print("Run: python build_b1_themes.py then python embed_b1_data.py")


if __name__ == "__main__":
    main()
