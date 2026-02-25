#!/usr/bin/env python3
"""
Extract German–English vocabulary from Einfach gut B1.1 and B1.2 Wortschatzliste Englisch PDFs,
then add new words to b1-vocabulary.json (no duplicates). Run build_b1_themes.py and embed_b1_data.py after.
"""
import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
B1_JSON = SCRIPT_DIR / "b1-vocabulary.json"
PDF_B1_1 = SCRIPT_DIR / "Einfach_gut_B1.1_Wortschatzliste_Englisch.pdf"
PDF_B1_2 = SCRIPT_DIR / "Einfach_gut_B1.2_Wortschatzliste_Englisch.pdf"

# German chars for detection
DE_CHARS = set("äöüßÄÖÜ")


def normalize_key(s):
    if not s:
        return ""
    s = s.strip().lower()
    for art in ("der ", "die ", "das "):
        if s.startswith(art):
            return s[len(art):].strip()
    return s


def looks_german(text):
    if not text or len(text) < 2:
        return False
    t = text.strip()
    if any(c in t for c in DE_CHARS):
        return True
    if t.lower().startswith(("der ", "die ", "das ")):
        return True
    # Capitalized noun (German) or lowercase verb
    if t[0].isupper() or (t.islower() and t.isalpha()):
        return True
    return False


def looks_english(text):
    if not text or len(text) < 1:
        return False
    t = text.strip()
    if any(c in t for c in DE_CHARS):
        return False
    # Mostly ASCII letters and spaces (allow "to" for infinitive)
    if all(c.isalpha() or c.isspace() or c in "-,.'()" for c in t):
        return True
    return False


def token_looks_english(tok):
    """Single token (no spaces) - is it likely English?"""
    if not tok or not tok.isalpha():
        return False
    if any(c in tok for c in DE_CHARS):
        return False
    if "/" in tok:
        return False
    return True


def token_looks_german(tok):
    if not tok:
        return False
    if any(c in tok for c in DE_CHARS):
        return True
    if tok.lower() in ("der", "die", "das"):
        return True
    if "/" in tok:  # der/die, Bewohner/in
        return True
    if tok[0].isupper() or (tok.islower() and len(tok) > 1):
        return True
    return False


def parse_table_line(line):
    """
    Parse a line in format: [Artikel] Deutsch [Plural] Englisch
    e.g. "der Abfall Abfälle rubbish" -> ("der Abfall", "rubbish")
    e.g. "die Anzeigetafel Anzeigetafeln bulletin board" -> ("die Anzeigetafel", "bulletin board")
    e.g. "aktiv active" -> ("aktiv", "active")
    """
    line = line.strip()
    if not line or len(line) < 3:
        return None
    # Skip headers
    lower = line.lower()
    if lower.startswith(("artikel", "deutsch", "plural", "englisch", "beispielsatz", "wortschatz zu lektion", "einfach gut", "telc ", "©")):
        return None
    tokens = line.split()
    if len(tokens) < 2:
        return None

    # Take English from the end: 1–5 tokens that look English (phrases like "certificate of good conduct")
    en_tokens = []
    for i in range(len(tokens) - 1, -1, -1):
        if token_looks_english(tokens[i]):
            en_tokens.append(tokens[i])
            if len(en_tokens) >= 5:
                break
        else:
            break
    en_tokens.reverse()
    if not en_tokens:
        return None
    german_tokens = tokens[: len(tokens) - len(en_tokens)]
    if not german_tokens:
        return None

    # German headword: article + first word, or just first word
    if german_tokens[0].lower() in ("der", "die", "das") and len(german_tokens) >= 2:
        headword = german_tokens[0] + " " + german_tokens[1]
    elif len(german_tokens) >= 2 and "/" in german_tokens[0]:  # der/die
        headword = german_tokens[0] + " " + german_tokens[1]
    else:
        headword = german_tokens[0]

    en_str = " ".join(en_tokens)
    if not headword or not en_str:
        return None
    return (headword.strip(), en_str.strip())


def extract_pairs_from_text(full_text):
    """Parse extracted PDF text into (german, english) pairs. Table layout + fallback strategies."""
    pairs = []
    seen = set()

    def add_pair(de_head, en_part):
        key = normalize_key(de_head)
        if key and key not in seen and looks_german(de_head) and looks_english(en_part) and len(de_head) > 1:
            seen.add(key)
            pairs.append((de_head, en_part))

    lines = [ln.strip() for ln in full_text.splitlines() if ln.strip()]

    # Strategy 1: table layout (Artikel Deutsch [Plural] Englisch)
    for line in lines:
        parsed = parse_table_line(line)
        if parsed:
            add_pair(parsed[0], parsed[1])

    # Strategy 2: same line with separator (tab, 2+ spaces, – , /)
    for line in lines:
        for sep in ["\t", "  ", " – ", " / ", " - "]:
            if sep in line:
                parts = re.split(re.escape(sep), line, maxsplit=1)
                if len(parts) == 2:
                    de_part = parts[0].strip()
                    en_part = parts[1].strip()
                    if not de_part or not en_part:
                        break
                    toks = de_part.split()
                    if toks and toks[0].lower() in ("der", "die", "das") and len(toks) >= 2:
                        de_head = toks[0] + " " + toks[1]
                    else:
                        de_head = toks[0] if toks else de_part
                    add_pair(de_head, en_part)
                break

    # Strategy 3: consecutive line pairs (German line, English line)
    i = 0
    while i + 1 < len(lines):
        a, b = lines[i], lines[i + 1]
        if a.lower().startswith(("deutsch", "englisch", "wort", "lesson", "lektion", "kapitel", "artikel", "einfach", "telc")):
            i += 1
            continue
        if looks_german(a) and looks_english(b):
            toks = a.split()
            if toks and toks[0].lower() in ("der", "die", "das") and len(toks) >= 2:
                de_head = toks[0] + " " + toks[1]
            else:
                de_head = toks[0] if toks else a
            if de_head and len(de_head) > 1:
                add_pair(de_head, b)
            i += 2
            continue
        i += 1

    # Strategy 4: single line, multiple tokens - last token(s) English
    for line in lines:
        if parse_table_line(line):
            continue
        tokens = line.split()
        if len(tokens) >= 2:
            first = tokens[0]
            if first.lower() in ("der", "die", "das") and len(tokens) >= 3:
                de_head = first + " " + tokens[1]
                en_part = " ".join(tokens[2:]).strip()
                if looks_english(en_part):
                    add_pair(de_head, en_part)
            elif looks_german(first) and len(tokens) >= 2 and looks_english(" ".join(tokens[1:])):
                add_pair(first, " ".join(tokens[1:]))

    return pairs


def extract_from_pdf(pdf_path):
    """Extract raw text from PDF and return list of (german, english) pairs."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("Install pypdf: pip install pypdf")
        return []

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return []

    pairs = []
    reader = PdfReader(str(pdf_path))
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pairs.extend(extract_pairs_from_text(text))

    return pairs


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help="Only verify: report PDF coverage, do not write.")
    args = parser.parse_args()

    print("Extracting from Einfach gut B1.1 PDF...")
    pairs_1 = extract_from_pdf(PDF_B1_1)
    print(f"  B1.1: {len(pairs_1)} raw pairs")

    print("Extracting from Einfach gut B1.2 PDF...")
    pairs_2 = extract_from_pdf(PDF_B1_2)
    print(f"  B1.2: {len(pairs_2)} raw pairs")

    # Merge and deduplicate by German (keep first occurrence)
    seen_key = set()
    merged = []
    for de, en in pairs_1 + pairs_2:
        key = normalize_key(de)
        if not key or key in seen_key:
            continue
        seen_key.add(key)
        merged.append((de.strip(), (en or "").strip()))

    print(f"Merged (no duplicate DE): {len(merged)} pairs from both PDFs")

    # Load current vocabulary
    with open(B1_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_keys = set()
    for cat in data["categories"]:
        for w in cat["words"]:
            de = (w.get("de") or "").strip()
            if de:
                existing_keys.add(normalize_key(de))

    # Check coverage: how many PDF words are in vocabulary?
    in_vocab = sum(1 for de, _ in merged if normalize_key(de) in existing_keys)
    missing = [(de, en) for de, en in merged if normalize_key(de) not in existing_keys]

    if missing:
        print(f"  In vocabulary: {in_vocab}/{len(merged)}")
        print(f"  Missing from vocabulary: {len(missing)}")
    else:
        print(f"  All {len(merged)} PDF words are in vocabulary.")

    if args.verify:
        if missing:
            print("Missing words (first 20):")
            for de, en in missing[:20]:
                print(f"  {de!r} -> {en!r}")
        return

    # New words only
    new_entries = []
    for de, en in merged:
        key = normalize_key(de)
        if key not in existing_keys:
            existing_keys.add(key)
            new_entries.append({
                "de": de,
                "pronunciation": "",
                "hi": "",
                "en": en or de,
            })

    if not new_entries:
        print("No new words to add (all from PDFs already in vocabulary).")
        return

    print(f"Adding {len(new_entries)} new words to b1-vocabulary.json")

    # Append to a single category so build_b1_themes can re-categorize
    all_words = []
    for cat in data["categories"]:
        all_words.extend(cat["words"])
    all_words.extend(new_entries)
    all_words.sort(key=lambda w: (w.get("de") or "").lower())

    out = {
        "title": data.get("title", "German B1 Vocabulary"),
        "subtitle": (data.get("subtitle", "") or "").strip() + " + Einfach gut! B1.1 & B1.2 Wortschatzliste.",
        "totalWords": len(all_words),
        "categories": [
            {
                "id": "B1_Wortliste",
                "name": "B1 Wortliste",
                "nameDe": "Goethe B1 + Einfach gut B1",
                "nameHi": "B1 शब्दावली",
                "emoji": "📖",
                "color": "#e3f2fd",
                "words": all_words,
            }
        ],
    }
    with open(B1_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Wrote {B1_JSON} with {len(all_words)} words.")
    print("Next: python build_b1_themes.py  then  python embed_b1_data.py")


if __name__ == "__main__":
    main()
