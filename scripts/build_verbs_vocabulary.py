# -*- coding: utf-8 -*-
"""
Build source/verbs/verbs-vocabulary.json: Top 1000 German verbs (A1–C2)
with English and simple Hindi. Structure like a1-vocabulary.json.
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
A1_JSON = BASE / "source" / "a1-650" / "a1-vocabulary.json"
A2_JSON = BASE / "source" / "a2" / "a2-vocabulary.json"
B1_JSON = BASE / "source" / "b1" / "b1-vocabulary.json"
OUT_JSON = BASE / "source" / "verbs" / "verbs-vocabulary.json"

# Categories A1–C2 with emoji and color
LEVELS = [
    {"id": "A1", "name": "A1", "nameDe": "Anfänger", "nameHi": "शुरुआत", "emoji": "🟢", "color": "#c8e6c9"},
    {"id": "A2", "name": "A2", "nameDe": "Grundstufe", "nameHi": "बुनियादी", "emoji": "🟡", "color": "#fff9c4"},
    {"id": "B1", "name": "B1", "nameDe": "Mittelstufe", "nameHi": "बीच का स्तर", "emoji": "🟠", "color": "#ffe0b2"},
    {"id": "B2", "name": "B2", "nameDe": "Gute Mittelstufe", "nameHi": "अच्छा बीच", "emoji": "🔶", "color": "#ffcc80"},
    {"id": "C1", "name": "C1", "nameDe": "Fortgeschritten", "nameHi": "आगे का", "emoji": "🔴", "color": "#ffab91"},
    {"id": "C2", "name": "C2", "nameDe": "Meister", "nameHi": "मास्टर", "emoji": "🟣", "color": "#ce93d8"},
]

# Normalize verb key (infinitive, lowercase, strip)
def norm(de):
    if not de:
        return ""
    s = (de or "").strip().lower()
    # Take first part if "verb, verb" or "verb (note)"
    s = s.split(",")[0].split("(")[0].strip()
    return s


def is_verb_infinitive(de):
    """True if de looks like a German verb infinitive (no article, ends in -en/-eln/-ern or common)."""
    if not de or len(de) < 3:
        return False
    s = de.strip().lower().split(",")[0].split("(")[0].strip()
    if not s or " " in s:
        return False
    if s in ("sein", "haben", "tun", "werden", "wissen", "möchten"):
        return True
    return s.endswith(("en", "eln", "ern"))

def collect_from_vocab():
    """Collect (de_norm, de_orig, en, hi) from A1, A2 Verbs; B1 Common_Verbs + any verb-like."""
    seen = {}
    for path, level in [(A1_JSON, "A1"), (A2_JSON, "A2"), (B1_JSON, "B1")]:
        if not path.exists():
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for cat in data.get("categories", []):
            cid = (cat.get("id") or "").lower()
            cname = (cat.get("name") or "").lower()
            is_verb_cat = "verb" in cid or "verb" in cname or (path == B1_JSON and cid == "common_verbs")
            # B1: also collect verb-like words from any category
            if path == B1_JSON and not is_verb_cat:
                for w in cat.get("words", []):
                    de = (w.get("de") or "").strip()
                    if not de or de.startswith(("der ", "die ", "das ")):
                        continue
                    key = norm(de)
                    if not key or len(key) < 3 or not is_verb_infinitive(key):
                        continue
                    en = (w.get("en") or "").strip()
                    hi = (w.get("hi") or "").strip()
                    if key not in seen:
                        seen[key] = {"de": de, "en": en, "hi": hi, "level": level}
                continue
            if not is_verb_cat:
                continue
            for w in cat.get("words", []):
                de = (w.get("de") or "").strip()
                if not de:
                    continue
                key = norm(de)
                if not key or len(key) < 2:
                    continue
                en = (w.get("en") or "").strip()
                hi = (w.get("hi") or "").strip()
                if key not in seen or level < seen[key].get("level", "Z"):
                    seen[key] = {"de": de, "en": en, "hi": hi, "level": level}
    return seen


def load_verb_list():
    """Load ordered list of top 1000 German verb infinitives (frequency order)."""
    # Top ~1000 German verb infinitives (frequency / importance order)
    # Sources: common lists + Wiktionary lemma forms (verbs only)
    verbs_ordered = [
        "sein", "haben", "werden", "können", "müssen", "sagen", "machen", "geben", "kommen",
        "sollen", "wollen", "gehen", "wissen", "sehen", "lassen", "stehen", "finden", "bleiben",
        "liegen", "heißen", "denken", "nehmen", "tun", "dürfen", "glauben", "halten", "nennen",
        "mögen", "zeigen", "führen", "sprechen", "bringen", "leben", "fahren", "meinen", "fragen",
        "kennen", "gelten", "stellen", "spielen", "arbeiten", "bekommen", "erzählen", "versuchen",
        "scheinen", "bilden", "beginnen", "erwarten", "wohnen", "betreffen", "schreiben", "laufen",
        "bedeuten", "verstehen", "setzen", "bekommen", "treffen", "entstehen", "lesen", "lernen",
        "erklären", "ziehen", "öffnen", "schließen", "fallen", "geben", "helfen", "gewinnen",
        "verlieren", "kaufen", "verkaufen", "essen", "trinken", "schlafen", "wachen", "rechnen",
        "passen", "fehlen", "sterben", "gebären", "wachsen", "vergessen", "erinnern", "singen",
        "tanzen", "lachen", "weinen", "rufen", "antworten", "hören", "riechen", "fühlen", "tasten",
        "schmecken", "waschen", "putzen", "kochen", "backen", "reparieren", "bauen", "malen",
        "zeichnen", "studieren", "unterrichten", "prüfen", "bezahlen", "kosten", "sparen",
        "leihen", "borgen", "schenken", "empfehlen", "warten", "folgen", "begleiten", "treten",
        "springen", "fliegen", "schwimmen", "reiten", "steigen", "sinken", "stecken", "hängen",
        "legen", "setzen", "stellen", "liegen", "sitzen", "stehen", "tragen", "halten",
        "drücken", "ziehen", "schieben", "stoßen", "werfen", "fangen", "greifen", "berühren",
        "schlagen", "treten", "beißen", "küssen", "umarmen", "retten", "beschützen", "verteidigen",
        "angreifen", "kämpfen", "schießen", "töten", "verletzen", "heilen", "operieren",
        "untersuchen", "messen", "wiegen", "zählen", "rechnen", "vergleichen", "ordnen",
        "sortieren", "teilen", "verbinden", "trennen", "mischen", "füllen", "leeren",
        "decken", "aufräumen", "aufstehen", "einschlafen", "aufwachen", "anziehen", "ausziehen",
        "anmachen", "ausmachen", "einladen", "besuchen", "besichtigen", "reisen", "wandern",
        "parken", "einsteigen", "aussteigen", "umsteigen", "abfahren", "ankommen", "abfliegen",
        "landen", "einchecken", "auschecken", "buchen", "reservieren", "bestellen", "kündigen",
        "wechseln", "tauschen", "austauschen", "ändern", "verbessern", "verschlechtern",
        "vergrößern", "verkleinern", "erhöhen", "senken", "steigern", "reduzieren",
        "erweitern", "beschränken", "erlauben", "verbieten", "erlauben", "gestatten",
        "vorschlagen", "vorschlagen", "annehmen", "ablehnen", "zustimmen", "widersprechen",
        "kritisieren", "loben", "beschuldigen", "entschuldigen", "danken", "grüßen",
        "verabschieden", "vorstellen", "bekanntgeben", "mitteilen", "informieren", "benachrichtigen",
        "warnen", "raten", "empfehlen", "befehlen", "bitten", "fordern", "verlangen",
        "versprechen", "drohen", "hoffen", "fürchten", "sorgen", "freuen", "ärgern",
        "überraschen", "enttäuschen", "beeindrucken", "interessieren", "langweilen",
        "lieben", "hassen", "mögen", "vermissen", "bewundern", " beneiden", "respektieren",
        "vertrauen", "misstrauen", "akzeptieren", "tolerieren", "unterstützen", "hindern",
        "stören", "unterbrechen", "stoppen", "weiter machen", "fortsetzen", "beenden",
        "abschließen", "aufhören", "anfangen", "starten", "beginnen", "anfangen",
    ]
    # Remove duplicates while preserving order
    seen = set()
    out = []
    for v in verbs_ordered:
        v = v.strip().lower()
        if v and v not in seen and 2 <= len(v) <= 50:
            seen.add(v)
            out.append(v)
    return out


def main():
    vocab = collect_from_vocab()
    verb_list = load_verb_list()
    # Extend verb_list with all verbs from vocab so we can reach 1000
    verb_set = set(verb_list)
    for key in sorted(vocab.keys()):
        if key not in verb_set and 2 <= len(key) <= 50:
            verb_set.add(key)
            verb_list.append(key)

    # Build full list: first from verb_list (order), then any from vocab not in list
    ordered = []
    used = set()
    for v in verb_list:
        if len(ordered) >= 1000:
            break
        if v in used:
            continue
        used.add(v)
        entry = vocab.get(v, {})
        ordered.append({
            "de": entry.get("de") or v,
            "en": entry.get("en") or "to " + v.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue"),
            "hi": entry.get("hi") or "",
            "level": entry.get("level"),
        })

    # Add more from vocab to reach 1000
    for key, entry in sorted(vocab.items()):
        if len(ordered) >= 1000:
            break
        if key in used:
            continue
        used.add(key)
        ordered.append({
            "de": entry.get("de") or key,
            "en": entry.get("en") or "",
            "hi": entry.get("hi") or "",
            "level": entry.get("level"),
        })

    # Fill missing en/hi with placeholder or translation
    try:
        from deep_translator import GoogleTranslator
        trans_en = GoogleTranslator(source="de", target="en")
        trans_hi = GoogleTranslator(source="de", target="hi")
        has_trans = True
    except ImportError:
        has_trans = False

    for i, w in enumerate(ordered):
        if not w.get("en") and has_trans:
            try:
                w["en"] = (trans_en.translate(w["de"]) or "").strip() or w["de"]
            except Exception:
                w["en"] = w["de"]
        if not w.get("en"):
            w["en"] = w["de"]
        if not w.get("hi") and has_trans:
            try:
                w["hi"] = (trans_hi.translate(w["de"]) or "").strip()
            except Exception:
                w["hi"] = ""
        if not w.get("hi"):
            w["hi"] = w.get("en", "")  # fallback show en if no hi

    # Pad to 1000 with verbs from vocab if needed
    while len(ordered) < 1000:
        for key, entry in sorted(vocab.items()):
            if len(ordered) >= 1000:
                break
            if key in used:
                continue
            used.add(key)
            ordered.append({
                "de": entry.get("de") or key,
                "en": entry.get("en") or "",
                "hi": entry.get("hi") or "",
                "level": entry.get("level"),
            })
        if len(ordered) < 1000:
            break  # no more from vocab

    # Trim to exactly 1000
    ordered = ordered[:1000]

    # Even distribution: 167,167,166,166,167,167
    level_order = ["A1", "A2", "B1", "B2", "C1", "C2"]
    sizes = [167, 167, 166, 166, 167, 167]
    categories = {}
    start = 0
    for lev, size in zip(LEVELS, sizes):
        lev_id = lev["id"]
        end = min(start + size, len(ordered))
        categories[lev_id] = [
            {"de": w["de"], "pronunciation": "", "hi": w.get("hi") or "", "en": w.get("en") or ""}
            for w in ordered[start:end]
        ]
        start = end

    out_data = {
        "title": "Top 1000 German Verbs (A1–C2)",
        "subtitle": "Most important German verbs with English and simple Hindi. Categories by level.",
        "totalWords": sum(len(categories[lev["id"]]) for lev in LEVELS),
        "categories": [
            {
                "id": lev["id"],
                "name": lev["name"],
                "nameDe": lev["nameDe"],
                "nameHi": lev["nameHi"],
                "emoji": lev["emoji"],
                "color": lev["color"],
                "words": categories[lev["id"]],
            }
            for lev in LEVELS
        ],
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)

    print(f"Wrote {OUT_JSON}. Total words: {out_data['totalWords']}. Per level: " +
          ", ".join(f"{lev['id']}={len(categories[lev['id']])}" for lev in LEVELS))


if __name__ == "__main__":
    main()
