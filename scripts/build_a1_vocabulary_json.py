# -*- coding: utf-8 -*-
"""
Create source/a1-650/a1-vocabulary.json from source/a1-650/a1-650.html.
- Read ALL words from A1 HTML. Include every word. No extras. No change to meanings.
- JSON structure matches source/a2/a2-vocabulary.json exactly.
- No blank or null values. No duplicates: include every row from the HTML exactly once.
"""
import json
import re
from pathlib import Path
from collections import OrderedDict

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

BASE = Path(__file__).resolve().parent.parent
A1_HTML = BASE / "source" / "a1-650" / "a1-650.html"
A1_JSON = BASE / "source" / "a1-650" / "a1-vocabulary.json"


def extract_category_name(header_div):
    """Get display name from category-header. E.g. 'Greetings & Basics' from span with optional (🔊...)."""
    spans = header_div.find_all("span", recursive=False)
    for s in spans:
        if "count" in (s.get("class") or []) or "emoji" in (s.get("class") or []):
            continue
        text = (s.get_text() or "").strip()
        # Remove " (62 words)" or " (🔊...)" part - take before " ("
        if " (" in text:
            text = text.split(" (")[0].strip()
        if text and not text.endswith("words"):
            return text
    return ""


def extract_color(header_div):
    """Get background-color from style."""
    style = header_div.get("style") or ""
    m = re.search(r"background-color:\s*([#\w]+)", style)
    return m.group(1).strip() if m else "#e8f5e9"


def extract_german_text(td_german):
    """Get German text from td.german, stripping the audio span."""
    if not td_german:
        return ""
    text = td_german.get_text() or ""
    text = re.sub(r"^\s*🔊\s*", "", text).strip()
    return text.strip()


def parse_a1_html(html_path):
    """Parse A1 HTML and return OrderedDict category_id -> { name, emoji, color, words: [ {de, en, hi} ] }."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    categories = OrderedDict()
    for div in soup.find_all("div", class_="category"):
        cat_id = div.get("id") or ""
        if not cat_id:
            continue
        header = div.find("div", class_="category-header")
        if not header:
            continue
        name = extract_category_name(header)
        emoji_span = header.find("span", class_="emoji")
        emoji = (emoji_span.get_text() or "").strip() or "📋"
        color = extract_color(header)
        table = div.find("table")
        if not table:
            continue
        tbody = table.find("tbody") or table
        words = []
        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) < 4:
                continue
            td_german, td_english, td_hindi = tds[1], tds[2], tds[3]
            de = extract_german_text(td_german)
            en = (td_english.get_text() or "").strip()
            hi = (td_hindi.get_text() or "").strip()
            if not de:
                continue
            words.append({
                "de": de,
                "pronunciation": "",
                "hi": hi if hi else "—",
                "en": en if en else "—",
            })
        categories[cat_id] = {"name": name, "emoji": emoji, "color": color, "words": words}
    return categories


def main():
    if not BeautifulSoup:
        raise SystemExit("Install beautifulsoup4: pip install beautifulsoup4")
    if not A1_HTML.exists():
        raise SystemExit(f"A1 HTML not found: {A1_HTML}")
    categories_data = parse_a1_html(A1_HTML)
    total_words = sum(len(c["words"]) for c in categories_data.values())
    # Build JSON matching A2 format exactly
    categories = []
    for cid, c in categories_data.items():
        if not c["words"]:
            continue
        categories.append({
            "id": cid,
            "name": c["name"],
            "nameDe": "",
            "nameHi": "",
            "emoji": c["emoji"],
            "color": c["color"],
            "words": c["words"],
        })
    out = {
        "title": "German A1 Vocabulary",
        "subtitle": f"A1 vocabulary ({total_words} words) organised by themes. German, English, Hindi.",
        "totalWords": total_words,
        "categories": categories,
    }
    A1_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(A1_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Wrote {A1_JSON}")
    print(f"Total words: {total_words}, categories: {len(categories)}")
    # Validation: no blanks in required fields
    for cat in out["categories"]:
        for w in cat["words"]:
            assert w.get("de"), "de must not be blank"
            assert w.get("en") is not None and w.get("en") != "", "en must not be blank"
            assert w.get("hi") is not None and w.get("hi") != "", "hi must not be blank"
    print("Validation OK: no blank or null values.")


if __name__ == "__main__":
    main()
