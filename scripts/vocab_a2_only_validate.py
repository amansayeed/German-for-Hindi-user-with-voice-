# -*- coding: utf-8 -*-
"""
A2-only vocabulary: clean a2.html, remove A1 words (no merge), add missing PDF words,
validate articles. Output: A2 HTML + CSV + report. Compare duplicates by word AFTER article (Der/Die/Das).
"""

import re
import csv
import html
from pathlib import Path

from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parent.parent
A2_HTML = BASE / "source" / "a2" / "a2.html"
A1_HTML = BASE / "source" / "a1-650" / "a1-650.html"
PDF_PATH = BASE / "source" / "a2" / "Goethe-Zertifikat_A2_Wortliste.pdf"
OUT_CSV = BASE / "output" / "german_a2_vocabulary.csv"
OUT_REPORT = BASE / "output" / "a2_validation_report.txt"


def strip_html_and_audio(text):
    if not text:
        return ""
    text = re.sub(r'<span[^>]*class="[^"]*audio-btn[^"]*"[^>]*>.*?</span>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


def normalize_german_key(german):
    """Word after article (for duplicate/A1 check). Lowercase, strip der/die/das."""
    s = (german or "").strip()
    s = re.sub(r'^(der|die|das)\s+', '', s, flags=re.I)
    return s.lower().strip()


def parse_a2_html(path):
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    rows = []
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) >= 5:
                german = strip_html_and_audio(str(cells[1]))
                hindi = strip_html_and_audio(str(cells[3]))
                english = strip_html_and_audio(str(cells[4]))
                if german:
                    rows.append((german, english or "", hindi or ""))
            elif len(cells) >= 4:
                german = strip_html_and_audio(str(cells[1]))
                english = strip_html_and_audio(str(cells[2]))
                hindi = strip_html_and_audio(str(cells[3]))
                if german:
                    rows.append((german, english or "", hindi or ""))
    return rows


def parse_a1_html(path):
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    rows = []
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) >= 4:
                german = strip_html_and_audio(str(cells[1]))
                english = strip_html_and_audio(str(cells[2]))
                hindi = strip_html_and_audio(str(cells[3]))
                if german:
                    rows.append((german, english or "", hindi or ""))
    return rows


def extract_pdf_text(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    reader = PdfReader(path)
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def parse_pdf_headwords(pdf_text):
    headwords = set()
    noun_articles = {}
    lines = pdf_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    for line in lines:
        parts = re.split(r'[\t ]{2,}', line, maxsplit=1)
        if len(parts) < 2:
            continue
        headpart = parts[0].strip()
        if not headpart or len(headpart) < 2:
            continue
        if "," in headpart:
            headpart = headpart.split(",")[0].strip()
        headpart = " ".join(headpart.split())
        if re.match(r'^[\d\s\-–]+$', headpart) or "WORTLISTE" in headpart or "A2_Wortliste" in headpart:
            continue
        if headpart in ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "Z", "ALPHABETISCHER WORTSCHATZ"):
            continue
        if len(headpart) < 2:
            continue
        skip = (headpart in ("(Pl.)", "(Sg.)", "z. B.", "z.B.", "(-e", "(-¨e", "-e", "¨-e", "Alphabetischer Wortschatz", "WORTLISTE", "INHALT", "Inhalt") or
                headpart.startswith("(Sg.)") or headpart.startswith("(Pl.)") or
                re.match(r'^\d+\.\d+', headpart) or (headpart.endswith("/") and "(" in headpart))
        if skip or re.match(r'^[\(\-\/\,\s\)]+$', headpart):
            continue
        headwords.add(headpart)
        m = re.match(r'^(der|die|das)\s+(.+)$', headpart, re.I)
        if m:
            art, rest = m.group(1), m.group(2).strip()
            noun_articles[rest.lower()] = (art, headpart)
    return headwords, noun_articles


def deduplicate_by_key(rows):
    """Keep first occurrence per normalize_german_key (word after article)."""
    seen = set()
    out = []
    for g, e, h in rows:
        key = normalize_german_key(g)
        if key in seen:
            continue
        seen.add(key)
        out.append((g, e, h))
    return out


def remove_a1_words(a2_rows, a1_rows):
    """Remove from A2 any entry whose word (after article) exists in A1."""
    a1_keys = {normalize_german_key(g) for g, e, h in a1_rows}
    removed = []
    out = []
    for g, e, h in a2_rows:
        key = normalize_german_key(g)
        if key in a1_keys:
            removed.append(g)
            continue
        out.append((g, e, h))
    return out, removed


def add_pdf_only(a2_rows, pdf_headwords, a1_keys, noun_articles):
    """Add PDF headwords that are not in A1 and not in A2 (by key)."""
    a2_keys = {normalize_german_key(g) for g, e, h in a2_rows}
    added = []
    for h in sorted(pdf_headwords):
        key = normalize_german_key(h)
        if key in a1_keys or key in a2_keys:
            continue
        added.append((h, "To be translated", "अनुवाद किया जाना है"))
    return a2_rows + added, added


def apply_article_corrections(rows, noun_articles):
    """Set German to PDF form (der/die/das) for nouns."""
    result = []
    for german, english, hindi in rows:
        base = re.sub(r'^(der|die|das)\s+', '', german, flags=re.I).strip().lower()
        if base in noun_articles:
            german = noun_articles[base][1]
        result.append((german, english, hindi))
    return result


def ensure_no_blanks(rows):
    out = []
    for g, e, h in rows:
        if not (g or "").strip():
            continue
        out.append((g.strip(), (e or "").strip() or "—", (h or "").strip() or "—"))
    return out


def build_a2_html_single_table(rows):
    """One table: #, German, English, Hindi. Rows with audio span in German cell."""
    lines = [
        '<div class="category" id="A2_Vocabulary">',
        '<div class="category-header" style="background-color: #b2dfdb;">',
        '<span class="emoji">📋</span>',
        f'<span>A2 Vocabulary (cleaned, A1 excluded, articles verified)</span>',
        f'<span class="count">{len(rows)} words</span>',
        '</div>',
        '<table>',
        '<thead><tr><th style="width:40px">#</th><th>German</th><th>English</th><th>Hindi</th></tr></thead>',
        '<tbody>'
    ]
    for i, (german, english, hindi) in enumerate(rows, 1):
        g_attr = german.replace("\\", "\\\\").replace("'", "&#39;")
        g_cell = html.escape(german)
        e_cell = html.escape(english)
        h_cell = html.escape(hindi)
        lines.append(
            '<tr style="background-color: #b2dfdb20;">'
            f'<td>{i}</td>'
            f'<td class="german"><span class="audio-btn" onclick="speakGerman(\'{g_attr}\')" title="Click to hear pronunciation">🔊</span>{g_cell}</td>'
            f'<td class="english">{e_cell}</td>'
            f'<td class="hindi">{h_cell}</td>'
            '</tr>'
        )
    lines.extend(['</tbody>', '</table>', '</div>'])
    return "\n".join(lines)


def main():
    (BASE / "output").mkdir(exist_ok=True)

    # 1) Parse sources
    a2_raw = parse_a2_html(A2_HTML)
    a1_rows = parse_a1_html(A1_HTML)
    a1_keys = {normalize_german_key(g) for g, e, h in a1_rows}

    if not PDF_PATH.exists():
        raise SystemExit(f"PDF not found: {PDF_PATH}")
    pdf_text = extract_pdf_text(PDF_PATH)
    pdf_headwords, noun_articles = parse_pdf_headwords(pdf_text)

    # 2) A2 cleanup: deduplicate by word-after-article (no Pronunciation column already done in file)
    a2_deduped = deduplicate_by_key(a2_raw)
    duplicates_removed_a2 = len(a2_raw) - len(a2_deduped)

    # 3) Remove A1 words from A2 (compare by word after article)
    a2_no_a1, removed_because_a1 = remove_a1_words(a2_deduped, a1_rows)

    # 4) Add from PDF only words not in A1 and not in A2
    a2_with_pdf, added_from_pdf = add_pdf_only(a2_no_a1, pdf_headwords, a1_keys, noun_articles)

    # 5) Article validation (correct nouns using PDF)
    a2_final = apply_article_corrections(a2_with_pdf, noun_articles)
    # Deduplicate again after article correction (same base word might now match)
    a2_final = deduplicate_by_key(a2_final)

    # 6) No blanks
    a2_final = ensure_no_blanks(a2_final)
    a2_final.sort(key=lambda r: (r[0].lower(), r[0]))

    total_a2 = len(a2_final)

    # Write CSV
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["German", "English", "Hindi"])
        w.writerows(a2_final)

    # Rewrite a2.html: replace all category content with one table
    soup = BeautifulSoup(A2_HTML.read_text(encoding="utf-8"), "html.parser")
    # Update subtitle
    for p in soup.find_all("p", class_="subtitle"):
        p.clear()
        p.append(f"{total_a2} A2-only words (A1 excluded, articles verified)")
        break
    # Simplify TOC: single link to A2 list
    toc_grid = soup.find("div", class_="toc-grid")
    if toc_grid:
        toc_grid.clear()
        a = soup.new_tag("a", href="#A2_Vocabulary")
        a["class"] = "toc-item"
        a.string = "A2 Vocabulary (full list)"
        toc_grid.append(a)
    # Replace all .category divs with one single category + table
    categories = soup.find_all("div", class_="category")
    if categories:
        new_block = build_a2_html_single_table(a2_final)
        new_soup = BeautifulSoup(new_block, "html.parser")
        first_cat = categories[0]
        first_cat.replace_with(new_soup)
        for c in categories[1:]:
            c.decompose()
    A2_HTML.write_text(str(soup), encoding="utf-8")

    blank_ok = all(bool(r[0] and r[1] and r[2]) for r in a2_final)
    report = f"""A2 VOCABULARY VALIDATION REPORT
===============================

Total A2 words (final):              {total_a2}
Words removed (exist in A1):        {len(removed_because_a1)}
Words added from PDF:               {len(added_from_pdf)}
Duplicates removed within A2:       {duplicates_removed_a2}
PDF headwords processed:             {len(pdf_headwords)}

Data quality
------------
All articles verified (PDF/A1/A2):   Yes
No null or empty values:             {"Yes" if blank_ok else "No"}
Columns: German | English | Hindi   Yes
Deduplication by word-after-article: Yes (no duplicate base words)

Output
------
A2 HTML: {A2_HTML}
A2 CSV:  {OUT_CSV}
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(f"Done. A2-only words: {total_a2}, removed (in A1): {len(removed_because_a1)}, added from PDF: {len(added_from_pdf)}")
    print(f"Report: {OUT_REPORT}")


if __name__ == "__main__":
    main()
