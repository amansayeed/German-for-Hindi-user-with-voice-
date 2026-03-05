# -*- coding: utf-8 -*-
"""Update source/a2/a2.html from german_a2_categorized_complete.csv: A1-style view with TOC and one section per category."""
import csv
import html
from pathlib import Path
from collections import OrderedDict

from bs4 import BeautifulSoup

BASE = Path(__file__).resolve().parent.parent
A2_HTML = BASE / "source" / "a2" / "a2.html"
CSV_PATH = BASE / "output" / "german_a2_categorized_complete.csv"

# Pastel header colors (A1-style), cycle per category
CATEGORY_COLORS = [
    "#e8f5e9", "#fce4ec", "#e3f2fd", "#f3e5f5", "#ffccbc",
    "#c8e6c9", "#b2ebf2", "#fff9c4", "#d7ccc8", "#b2dfdb",
    "#e1bee7", "#ffecb3", "#c5e1a5", "#b3e5fc", "#f8bbd0",
    "#d1c4e9", "#b2dfdb", "#ffcc80", "#cfd8dc", "#ffab91",
    "#a5d6a7", "#80deea", "#ce93d8", "#fff59d", "#90caf9",
    "#ef9a9a",
]


def category_to_slug(cat: str) -> str:
    """'👋 Greetings & Basics' -> 'Greetings_&_Basics'; '🏃 Verbs' -> 'Verbs'."""
    parts = cat.split(None, 1)
    name = parts[1] if len(parts) > 1 else (parts[0] if parts else "Other")
    return name.replace(" ", "_")


def slug_for_attr(slug: str) -> str:
    """Escape & for HTML attribute (id, href)."""
    return slug.replace("&", "&amp;")


def get_emoji(cat: str) -> str:
    """Return leading emoji or first character of category string."""
    if not cat:
        return "📋"
    first = cat.strip().split()[0] if cat.strip() else "📋"
    if len(first) == 1:
        return first
    c = cat[0]
    if ord(c) >= 0x1F300 or (0x2600 <= ord(c) <= 0x26FF) or (0x2700 <= ord(c) <= 0x27BF):
        return c
    return "📋"


def get_display_name(cat: str) -> str:
    """Return category name without leading emoji for TOC/header label (e.g. 'Verbs', 'Greetings & Basics')."""
    parts = cat.split(None, 1)
    return parts[1] if len(parts) > 1 else (parts[0] if parts else "Other")


def main():
    rows = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append((
                r.get("Category", "").strip(),
                r.get("German", ""),
                r.get("English", ""),
                r.get("Hindi", ""),
            ))

    # Group by category, preserve order of first occurrence
    groups = OrderedDict()
    for cat, german, english, hindi in rows:
        if cat not in groups:
            groups[cat] = []
        groups[cat].append((german, english, hindi))

    # Build TOC: Categories (विषय) (N) with one toc-item per category
    num_cats = len(groups)
    toc_items = []
    for cat, items in groups.items():
        slug = category_to_slug(cat)
        emoji = get_emoji(cat)
        label = get_display_name(cat)
        count = len(items)
        toc_items.append(
            f'<a href="#{slug_for_attr(slug)}" class="toc-item">'
            f'<span>{html.escape(emoji)}</span> {html.escape(label)} ({count})</a>'
        )
    toc_html = (
        '<div class="toc">\n'
        f'<h2>📑 Categories (विषय) ({num_cats})</h2>\n'
        '<div class="toc-grid">\n'
        + "\n".join(toc_items) + "\n"
        "</div>\n</div>"
    )

    # Build one .category block per category (like A1): header + table (#, German, English, Hindi)
    category_blocks = []
    for idx, (cat, items) in enumerate(groups.items()):
        slug = category_to_slug(cat)
        emoji = get_emoji(cat)
        color = CATEGORY_COLORS[idx % len(CATEGORY_COLORS)]
        color_alpha = color + "20"
        # Category header: emoji, name, count
        label = get_display_name(cat)
        header_html = (
            f'<div class="category" id="{slug_for_attr(slug)}">\n'
            f'<div class="category-header" style="background-color: {color};">\n'
            f'<span class="emoji">{html.escape(emoji)}</span>\n'
            f'<span>{html.escape(label)}</span>\n'
            f'<span class="count">{len(items)} words</span>\n'
            "</div>\n"
            "<table>\n"
            "<thead><tr><th style=\"width:40px\">#</th><th>German</th><th>English</th><th>Hindi</th></tr></thead>\n"
            "<tbody>\n"
        )
        row_lines = []
        for i, (german, english, hindi) in enumerate(items, 1):
            g_attr = german.replace("\\", "\\\\").replace("'", "&#39;")
            g_cell = html.escape(german)
            e_cell = html.escape(english)
            h_cell = html.escape(hindi)
            row_lines.append(
                f'<tr style="background-color: {color_alpha};">'
                f'<td>{i}</td>'
                f'<td class="german"><span class="audio-btn" onclick="speakGerman(\'{g_attr}\')" title="Click to hear pronunciation">🔊</span>{g_cell}</td>'
                f'<td class="english">{e_cell}</td>'
                f'<td class="hindi">{h_cell}</td>'
                "</tr>"
            )
        category_blocks.append(
            header_html + "\n".join(row_lines) + "\n</tbody>\n</table>\n</div>"
        )

    full_new_content = toc_html + "\n" + "\n".join(category_blocks)

    soup = BeautifulSoup(A2_HTML.read_text(encoding="utf-8"), "html.parser")
    toc_div = soup.find("div", class_="toc")
    first_cat_div = soup.find("div", class_="category")
    if not toc_div or not first_cat_div:
        raise SystemExit("Missing .toc or .category in a2.html")

    parsed = BeautifulSoup(full_new_content, "html.parser")
    new_toc = parsed.find("div", class_="toc")
    new_categories = parsed.find_all("div", class_="category")

    toc_div.replace_with(new_toc)
    prev = first_cat_div
    for i, c in enumerate(new_categories):
        if i == 0:
            prev.replace_with(c)
            prev = c
        else:
            prev.insert_after(c)
            prev = c

    # Update subtitle
    for p in soup.find_all("p", class_="subtitle"):
        p.clear()
        p.append(f"{len(rows)} A2 words · categorised & fully translated")
        break

    A2_HTML.write_text(str(soup), encoding="utf-8")
    print(f"Updated {A2_HTML}: TOC with {num_cats} categories, {len(rows)} rows (A1-style sections)")


if __name__ == "__main__":
    main()
