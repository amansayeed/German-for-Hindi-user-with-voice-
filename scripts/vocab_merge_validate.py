# -*- coding: utf-8 -*-
"""
German Vocabulary: Clean, Merge (A1-650 + A2 HTML + A2 PDF), validate articles, output dataset and report.
Columns: German | English | Hindi. No Pronunciation column. No duplicates. No blank values.
"""

import re
import csv
from pathlib import Path
from collections import OrderedDict

from bs4 import BeautifulSoup

# Paths
BASE = Path(__file__).resolve().parent.parent
A2_HTML = BASE / "source" / "a2" / "a2.html"
A1_HTML = BASE / "source" / "a1-650" / "a1-650.html"
PDF_PATH = BASE / "source" / "a2" / "Goethe-Zertifikat_A2_Wortliste.pdf"
OUT_CSV = BASE / "output" / "german_vocabulary_merged.csv"
OUT_REPORT = BASE / "output" / "vocabulary_summary_report.txt"


def strip_html_and_audio(text):
    """Remove HTML tags and audio button content, return plain text."""
    if not text:
        return ""
    # Remove <span class="audio-btn" ...>...</span>
    text = re.sub(r'<span[^>]*class="[^"]*audio-btn[^"]*"[^>]*>.*?</span>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


def normalize_german_key(german):
    """Normalize German for duplicate detection: lowercase, strip article for comparison."""
    s = (german or "").strip()
    s = re.sub(r'^(der|die|das)\s+', '', s, flags=re.I)
    return s.lower().strip()


def parse_a2_html(path):
    """Parse a2.html: columns #, German, [Pronunciation], English, Hindi -> (German, English, Hindi). All tables. Supports both 4 and 5 column layouts."""
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    rows = []
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) >= 5:
                # Legacy: #, German, Pronunciation, Hindi, English
                german = strip_html_and_audio(str(cells[1]))
                hindi = strip_html_and_audio(str(cells[3]))
                english = strip_html_and_audio(str(cells[4]))
                if german:
                    rows.append((german, english or "", hindi or ""))
            elif len(cells) >= 4:
                # Current: #, German, English, Hindi
                german = strip_html_and_audio(str(cells[1]))
                english = strip_html_and_audio(str(cells[2]))
                hindi = strip_html_and_audio(str(cells[3]))
                if german:
                    rows.append((german, english or "", hindi or ""))
    return rows


def parse_a1_html(path):
    """Parse a1-650.html: columns #, German, English, Hindi -> (German, English, Hindi). All tables."""
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    rows = []
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = tr.find_all("td")
            # a1: #, German, English, Hindi -> 4 cells
            if len(cells) >= 4:
                german = strip_html_and_audio(str(cells[1]))
                english = strip_html_and_audio(str(cells[2]))
                hindi = strip_html_and_audio(str(cells[3]))
                if german:
                    rows.append((german, english or "", hindi or ""))
    return rows


def extract_pdf_text(path):
    """Extract raw text from PDF."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def parse_pdf_headwords(pdf_text):
    """
    Parse Goethe A2 PDF word list. Format: headword + spaces + Example sentence (no tab in pypdf output).
    Headwords can be: "der Apfel, ¨-", "die Angst, ¨-e", "anfangen, fängt an,".
    Return set of full headword strings and dict base_word -> (article, full_headword) for nouns.
    """
    headwords = set()
    noun_articles = {}
    lines = pdf_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    for line in lines:
        # Split on 2+ spaces or tab: first part = headword, rest = example
        parts = re.split(r'[\t ]{2,}', line, maxsplit=1)
        if len(parts) < 2:
            continue
        headpart = parts[0].strip()
        if not headpart or len(headpart) < 2:
            continue
        # Clean: remove trailing conjugation/plural hints after comma (e.g. "der Apfel, ¨-" -> "der Apfel")
        if "," in headpart:
            headpart = headpart.split(",")[0].strip()
        # Normalize multiple spaces and fix common PDF encoding (e.g. -> ü)
        headpart = " ".join(headpart.split())
        # Skip page headers / numbers
        if re.match(r'^[\d\s\-–]+$', headpart) or "WORTLISTE" in headpart or "A2_Wortliste" in headpart:
            continue
        if headpart in ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "Z", "ALPHABETISCHER WORTSCHATZ"):
            continue
        if len(headpart) < 2:
            continue
        # Skip known non-word entries (fragments, abbreviations)
        skip = (headpart in ("(Pl.)", "(Sg.)", "z. B.", "z.B.", "(-e", "(-¨e", "-e", "¨-e", "Alphabetischer Wortschatz", "WORTLISTE", "INHALT", "Inhalt") or
                headpart.startswith("(Sg.)") or headpart.startswith("(Pl.)") or
                re.match(r'^\d+\.\d+', headpart) or  # times like 10.15, 3.15
                (headpart.endswith("/") and "(" in headpart))  # fragment like "(bekommen/"
        if skip:
            continue
        if re.match(r'^[\(\-\/\,\s\)]+$', headpart):  # only punctuation/parens
            continue
        headwords.add(headpart)
        m = re.match(r'^(der|die|das)\s+(.+)$', headpart, re.I)
        if m:
            art, rest = m.group(1), m.group(2).strip()
            base = rest.lower()
            noun_articles[base] = (art, headpart)
    return headwords, noun_articles


def normalize_pdf_headword_for_match(h):
    """Normalize PDF headword for matching to HTML entries (lowercase, no comma part)."""
    h = h.strip()
    if "," in h:
        h = h.split(",")[0].strip()
    return h.lower()


def merge_and_deduplicate(a1_rows, a2_rows):
    """Merge rows; deduplicate by normalized German (keep first occurrence)."""
    seen_key = set()
    merged = []
    for german, english, hindi in a1_rows + a2_rows:
        key = normalize_german_key(german)
        if key in seen_key:
            continue
        seen_key.add(key)
        merged.append((german, english or "", hindi or ""))
    return merged


def add_missing_from_pdf(merged_rows, pdf_headwords, noun_articles):
    """Add PDF headwords that are not yet in merged. Use placeholder EN/HI for missing."""
    existing_normalized = {normalize_german_key(g) for g, e, h in merged_rows}
    existing_full = {normalize_pdf_headword_for_match(g) for g, e, h in merged_rows}
    added = []
    for h in sorted(pdf_headwords):
        norm = normalize_pdf_headword_for_match(h)
        key = normalize_german_key(h)
        if key in existing_normalized or norm in existing_full:
            continue
        # Prefer PDF form (with article for nouns)
        english = "To be translated"
        hindi = "अनुवाद किया जाना है"
        added.append((h, english, hindi))
    return merged_rows + added, added


def apply_article_corrections(rows, noun_articles):
    """For nouns, set German to PDF form (der/die/das) when we have it."""
    result = []
    for german, english, hindi in rows:
        g_clean = re.sub(r'^(der|die|das)\s+', '', german, flags=re.I).strip()
        base = g_clean.lower()
        if base in noun_articles:
            art, full_form = noun_articles[base]
            german = full_form
        result.append((german, english, hindi))
    return result


def ensure_no_blanks(rows):
    """Replace any blank English/Hindi with placeholder."""
    out = []
    for g, e, h in rows:
        if not (g or "").strip():
            continue
        out.append((g.strip(), (e or "").strip() or "—", (h or "").strip() or "—"))
    return out


def main():
    BASE.mkdir(exist_ok=True)
    (BASE / "output").mkdir(exist_ok=True)

    # 1) Parse HTML
    a2_rows = parse_a2_html(A2_HTML)
    a1_rows = parse_a1_html(A1_HTML)
    count_a1, count_a2 = len(a1_rows), len(a2_rows)

    # 2) Merge and deduplicate
    merged = merge_and_deduplicate(a1_rows, a2_rows)
    total_after_merge = len(merged)
    duplicates_removed = count_a1 + count_a2 - total_after_merge

    # 3) PDF
    if not PDF_PATH.exists():
        raise SystemExit(f"PDF not found: {PDF_PATH}")
    pdf_text = extract_pdf_text(PDF_PATH)
    pdf_headwords, noun_articles = parse_pdf_headwords(pdf_text)
    merged, added_from_pdf = add_missing_from_pdf(merged, pdf_headwords, noun_articles)

    # 4) Article validation (correct nouns using PDF)
    merged = apply_article_corrections(merged, noun_articles)

    # 5) No blanks
    merged = ensure_no_blanks(merged)

    # Sort by German (case-insensitive)
    merged.sort(key=lambda r: (r[0].lower(), r[0]))

    # Write CSV: German | English | Hindi
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["German", "English", "Hindi"])
        w.writerows(merged)

    # Report
    blank_check = all(bool(r[0] and r[1] and r[2]) for r in merged)
    report = f"""GERMAN VOCABULARY — SUMMARY REPORT
=====================================

Total unique words (final):     {len(merged)}
Words from A1 HTML (raw):       {count_a1}
Words from A2 HTML (raw):       {count_a2}
Duplicates removed:            {duplicates_removed}
Words added from PDF:           {len(added_from_pdf)}
PDF headwords parsed:           {len(pdf_headwords)}

Data quality
------------
No blank values:                {"Yes" if blank_check else "No"}
All entries have German:        Yes
All entries have English:       {"Yes" if blank_check else "No"}
All entries have Hindi:         {"Yes" if blank_check else "No"}

Output
------
CSV: {OUT_CSV}
Columns: German | English | Hindi

Note: Words added from the PDF that were not in the HTML sources have
placeholder English "To be translated" and Hindi "अनुवाद किया जाना है"
until manually translated. No blank or null values remain.
"""
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(f"Done. Total words: {len(merged)}, CSV: {OUT_CSV}, Report: {OUT_REPORT}")


if __name__ == "__main__":
    main()
