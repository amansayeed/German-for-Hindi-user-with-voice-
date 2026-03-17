# -*- coding: utf-8 -*-
"""
1. Extract common-words data from common-words.html (or load common-vocabulary.json if present).
2. Build set of words already in A1, A2, B1, 2980 nouns, verbs.
3. common-vocabulary.json: only entries NOT in those files; no duplicates.
4. Regenerate common-words.html from the JSON.
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
COMMON_DIR = BASE / "source" / "common-words"
COMMON_HTML = COMMON_DIR / "common-words.html"
COMMON_JSON = COMMON_DIR / "common-vocabulary.json"
A1_JSON = BASE / "source" / "a1-650" / "a1-vocabulary.json"
A2_JSON = BASE / "source" / "a2" / "a2-vocabulary.json"
B1_JSON = BASE / "source" / "b1" / "b1-vocabulary.json"
NOUNS_2980 = BASE / "source" / "the-2980-most-frequently-used-german" / "2980-most-frequent-german-nouns.json"
VERBS_JSON = BASE / "source" / "verbs" / "verbs-vocabulary.json"

IRREGULAR_INFINITIVES = frozenset({"sein", "haben", "werden", "tun"})


def is_verb_infinitive(de):
    """True if de is a single verb infinitive."""
    if not de or not isinstance(de, str):
        return False
    s = de.strip()
    if not s or " " in s:
        return False
    w = s.lower()
    if w in IRREGULAR_INFINITIVES:
        return True
    return w.endswith("en") or w.endswith("ern") or w.endswith("eln")


def normalize_stem(de):
    """Single comparable form: strip article, lowercase, first word."""
    if not de:
        return ""
    s = (de or "").strip().lower()
    for prefix in ("der ", "die ", "das "):
        if s.startswith(prefix):
            return s[len(prefix):].strip().split()[0] if s[len(prefix):].strip() else ""
    return s.split()[0] if s else ""


def collect_stems_from_vocab(path):
    """From A1/A2/B1: all stems + all tokens from each 'de'."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    stems = set()
    for cat in data.get("categories", []):
        for w in cat.get("words", []):
            de = (w.get("de") or "").strip()
            if not de:
                continue
            stems.add(normalize_stem(de))
            for token in de.strip().lower().split():
                if token not in ("der", "die", "das"):
                    stems.add(token)
    return stems


def collect_stems_2980(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(normalize_stem(e.get("de") or "") for e in data.get("entries", []))


def collect_stems_verbs(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(normalize_stem(w.get("de") or "") for cat in data.get("categories", []) for w in cat.get("words", []))


def extract_from_html(html_path):
    """Parse common-words.html and return list of (level_id, words)."""
    html = html_path.read_text(encoding="utf-8")
    row_pat = re.compile(
        r'<td class="german">.*?</span>\s*([^<]*)</td>\s*'
        r'<td class="pronunciation">([^<]*)</td>\s*'
        r'<td class="hindi">([^<]*)</td>\s*'
        r'<td class="english">([^<]*)</td>',
        re.DOTALL
    )
    row_pat2 = re.compile(
        r'<td class="german">(.*?)</td>\s*<td class="pronunciation">(.*?)</td>\s*'
        r'<td class="hindi">(.*?)</td>\s*<td class="english">(.*?)</td>',
        re.DOTALL
    )
    out = []
    parts = html.split('<div class="category" id="')
    for part in parts[1:]:
        bracket = part.find('">')
        if bracket == -1:
            continue
        level_id = part[:bracket].strip()
        rest = part[bracket:]
        tstart = rest.find("<tbody>")
        tend = rest.find("</tbody>")
        if tstart == -1 or tend == -1:
            continue
        tbody = rest[tstart + 8 : tend]
        words = []
        for row in row_pat.finditer(tbody):
            de = row.group(1).strip()
            pron = row.group(2).strip()
            hi = row.group(3).strip()
            en = row.group(4).strip()
            if de:
                words.append({"de": de, "pronunciation": pron, "hi": hi, "en": en})
        if not words:
            for row in row_pat2.finditer(tbody):
                de = re.sub(r"<[^>]+>", "", row.group(1)).strip()
                pron = row.group(2).strip()
                hi = row.group(3).strip()
                en = row.group(4).strip()
                if de:
                    words.append({"de": de, "pronunciation": pron, "hi": hi, "en": en})
        out.append((level_id, words))
    return out


def build_common_json():
    # Existing stems from all other files
    existing = set()
    if A1_JSON.exists():
        existing |= collect_stems_from_vocab(A1_JSON)
    if A2_JSON.exists():
        existing |= collect_stems_from_vocab(A2_JSON)
    if B1_JSON.exists():
        existing |= collect_stems_from_vocab(B1_JSON)
    if NOUNS_2980.exists():
        existing |= collect_stems_2980(NOUNS_2980)
    if VERBS_JSON.exists():
        existing |= collect_stems_verbs(VERBS_JSON)

    # Load or extract common data
    if COMMON_JSON.exists():
        with open(COMMON_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        all_entries = []
        for cat in data.get("categories", []):
            cid = cat.get("id", "")
            for w in cat.get("words", []):
                all_entries.append((cid, w))
    else:
        all_entries = []
        for level_id, words in extract_from_html(COMMON_HTML):
            for w in words:
                all_entries.append((level_id, w))

    # Filter: keep only if stem NOT in existing; not a verb; dedupe by stem (keep first)
    seen_stem = set()
    filtered = []
    for level_id, w in all_entries:
        de = (w.get("de") or "").strip()
        if is_verb_infinitive(de):
            continue
        stem = normalize_stem(de)
        if stem in existing:
            continue
        if stem in seen_stem:
            continue
        seen_stem.add(stem)
        filtered.append((level_id, w))

    # Group by level
    by_level = {}
    level_order = ["A1_Level", "A2_Level", "B1_Level", "B2_Level", "C1-C2_Level"]
    for lid in level_order:
        by_level[lid] = []
    for level_id, w in filtered:
        by_level.setdefault(level_id, []).append(w)
    for lid, entries in list(by_level.items()):
        if lid not in level_order:
            level_order.append(lid)

    categories = []
    total = 0
    level_names = {
        "A1_Level": ("A1 Level", "A1 Niveau", "#e8f5e9", "📚"),
        "A2_Level": ("A2 Level", "A2 Niveau", "#fff9c4", "📗"),
        "B1_Level": ("B1 Level", "B1 Niveau", "#ffe0b2", "📘"),
        "B2_Level": ("B2 Level", "B2 Niveau", "#e3f2fd", "📕"),
        "C1-C2_Level": ("C1-C2 Level", "C1-C2 Niveau", "#f3e5f5", "📙"),
    }
    for lid in level_order:
        words = by_level.get(lid, [])
        if not words:
            continue
        name, name_de, color, emoji = level_names.get(lid, (lid, "", "#f5f5f5", "📄"))
        categories.append({
            "id": lid,
            "name": name,
            "nameDe": name_de,
            "nameHi": "",
            "emoji": emoji,
            "color": color,
            "words": words,
        })
        total += len(words)

    data = {
        "title": "Common English–German Cognates",
        "subtitle": "Words not in A1/A2/B1/2980/verbs. German, English, Hindi. Total: %d entries." % total,
        "totalWords": total,
        "categories": categories,
    }
    COMMON_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data, total


def build_common_html(data):
    """Regenerate common-words.html tables from data; keep head/nav/footer."""
    html = COMMON_HTML.read_text(encoding="utf-8")
    total = data.get("totalWords", 0)

    # Replace subtitle total
    html = re.sub(
        r'Total: \d+ entries\.',
        'Total: %d entries.' % total,
        html, count=1
    )
    html = re.sub(
        r'<p class="subtitle">[^<]+<br>[^<]+Total: \d+ entries\.</p>',
        '<p class="subtitle">%s<br>Total: %d entries.</p>' % (
            "Full list with German pronunciation in Hindi script, Hindi meanings, CEFR levels. Only words not in A1/A2/B1/2980/verbs.",
            total
        ),
        html, count=1
    )

    # Find and replace the main content: from first <h1> through <p>Total entries:</p>
    start_marker = "<h1>"
    start_idx = html.find(start_marker)
    end_p = html.find("<p>Total entries:")
    if end_p == -1:
        return
    end_idx = html.find("</p>", end_p) + 4
    if start_idx == -1:
        return

    new_body = []
    new_body.append('    <h1>🇩🇪 Complete English-German Cognates List</h1>')
    new_body.append('    <p class="subtitle">Full list with German pronunciation in Hindi script, Hindi meanings, and CEFR levels.<br>Only words not in A1/A2/B1/2980/verbs. Total: %d entries.</p>' % total)
    row_num = 0
    level_colors = {"A1_Level": "#e8f5e920", "A2_Level": "#fff9c420", "B1_Level": "#ffe0b220", "B2_Level": "#e3f2fd20", "C1-C2_Level": "#f3e5f520"}
    for cat in data.get("categories", []):
        cid = cat.get("id", "")
        name = cat.get("name", cid)
        words = cat.get("words", [])
        if not words:
            continue
        bg = level_colors.get(cid, "#f5f5f520")
        new_body.append('')
        new_body.append('    <div class="category" id="%s">' % cid)
        new_body.append('        <div class="category-header" style="background-color: %s;">' % (cat.get("color", "#f5f5f5")))
        new_body.append('            <span class="emoji">%s</span>' % cat.get("emoji", "📄"))
        new_body.append('            <span>%s</span>' % name)
        new_body.append('            <span class="count">%d words</span>' % len(words))
        new_body.append('        </div>')
        new_body.append('    <table>')
        new_body.append('        <thead>')
        new_body.append('                <tr>')
        new_body.append('                    <th style="width:40px">#</th>')
        new_body.append('                    <th>German</th>')
        new_body.append('                    <th>Pronunciation (Hindi)</th>')
        new_body.append('                    <th>Hindi</th>')
        new_body.append('                    <th>English</th>')
        new_body.append('                </tr>')
        new_body.append('        </thead>')
        new_body.append('        <tbody>')
        for w in words:
            row_num += 1
            de = (w.get("de") or "").replace("'", "&#39;")
            pron = (w.get("pronunciation") or "").replace("'", "&#39;")
            hi = (w.get("hi") or "").replace("'", "&#39;")
            en = (w.get("en") or "").replace("'", "&#39;")
            new_body.append('                <tr style="background-color: %s;">' % bg)
            new_body.append('                    <td>%d</td>' % row_num)
            new_body.append('                    <td class="german"><span class="audio-btn" onclick="speakGerman(\'%s\')" title="Click to hear pronunciation">🔊</span>%s</td>' % (de.replace("\\", "\\\\").replace("'", "\\'"), de))
            new_body.append('                    <td class="pronunciation">%s</td>' % pron)
            new_body.append('                    <td class="hindi">%s</td>' % hi)
            new_body.append('                    <td class="english">%s</td>' % en)
            new_body.append('                </tr>')
        new_body.append('            </tbody>')
        new_body.append('        </table>')
        new_body.append('    </div>')
    new_body.append('')
    new_body.append('    <p>Total entries: %d</p>' % total)

    new_content = "\n".join(new_body)
    html = html[:start_idx] + new_content + "\n\n    " + html[end_idx:]
    COMMON_HTML.write_text(html, encoding="utf-8")


def main():
    data, total = build_common_json()
    print("common-vocabulary.json: %d unique entries (not in A1/A2/B1/2980/verbs)" % total)
    build_common_html(data)
    print("Updated common-words.html")


if __name__ == "__main__":
    main()
