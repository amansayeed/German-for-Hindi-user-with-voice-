# -*- coding: utf-8 -*-
"""
Deep repair of A2 vocabulary JSON per Goethe-Zertifikat A2 standards.
- One word per entry; split combined entries
- Base forms only (infinitive, article+noun, base adjective)
- Correct categories: Verbs, Nouns, Adjectives, Adverbs, Pronouns, Prepositions, Expressions
- Remove fragments, duplicates, conjugated forms
- Add pronunciation; ensure translations
"""
import json
import re
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent
A2_JSON = BASE / "source" / "a2" / "a2-vocabulary.json"

# ---- Entries to remove (fragments, broken, suffix-only, grammatical notes) ----
REMOVE_DE = frozenset({
    "hat, ist", "hin, hin, hin", "her, her, her", "dar Bsp. darauf",
    "der, die", "der, das Blog", "der, das Comic", "der, das Laptop",
    "z. B. Feierabend", "z. B. Infotafel", "z. B. weiter",
    "war fit", "war dabei", "-ung (Suffix)", "wer / wen",
    "Länder und Nationalitäten", "Viertel nach", "Viertel vor",
    "an sein, aus sein", "auf sein", "weg sein",
    "ist fertig", "ist fit gewesen", "ist gültig gewesen",
    "hat, ist gelegen", "hat, ist gestanden", "hat, ist gesurft",
    "angezogen, ausgezogen",
})

def should_remove(de):
    if not de or len(de) < 2:
        return True
    if de in REMOVE_DE:
        return True
    if de.startswith("hat ") or de.startswith("ist "):
        return True
    if re.match(r"^hat,\s*ist\s", de) or re.match(r"^ist,\s*hat\s", de):
        return True
    if re.match(r"^[a-z]-[a-z]\s", de):  # "z. B." style
        return True
    return False

# ---- Split pairs: "word1, word2" -> list of (de, en, hi) ----
# When we split, we need en and hi for each part. Default: use first part of " / " or "; "
SPLIT_PAIRS = [
    ("anziehen, ausziehen", [("anziehen", "to put on", "पहनना"), ("ausziehen", "to take off", "उतारना")]),
    ("haben, machen", [("haben", "to have", "रखना"), ("machen", "to do", "करना")]),
    ("fahren, gehen", [("fahren", "to drive", "गाड़ी चलाना"), ("gehen", "to go", "जाना")]),
    ("laufen, machen", [("laufen", "to run", "दौड़ना"), ("machen", "to do", "करना")]),
    ("nehmen, spielen", [("nehmen", "to take", "लेना"), ("spielen", "to play", "खेलना")]),
    ("geben, sagen", [("geben", "to give", "देना"), ("sagen", "to say", "कहना")]),
    ("machen, helfen", [("machen", "to do", "करना"), ("helfen", "to help", "मदद करना")]),
    ("nehmen, werfen", [("nehmen", "to take", "लेना"), ("werfen", "to throw", "फेंकना")]),
    ("heraus, raus", [("heraus", "out (direction)", "बाहर"), ("raus", "out", "बाहर")]),
    ("herein, rein", [("herein", "in (direction)", "अंदर"), ("rein", "in", "अंदर")]),
    ("leidtun, leid tun", [("leidtun", "to be sorry", "अफ़सोस होना")]),  # one concept
    ("mal, das Mal", [("mal", "once; times", "बार"), ("das Mal", "the time", "बार")]),
]
SPLIT_MAP = {de.strip(): items for de, items in SPLIT_PAIRS}

# ---- Conjugated / wrong form -> base form ----
CONJUGATED_TO_INFINITIVE = {
    "tauscht": "tauschen", "trifft": "treffen", "träumt": "träumen", "wartet": "warten",
    "zieht": "ziehen", "besichtigt": "besichtigen", "besteht": "bestehen", "bestellt": "bestellen",
    "besucht": "besuchen", "bewirbt": "sich bewerben", "duscht": "duschen", "erinnert": "erinnern",
    "unterhält": "unterhalten", "untersucht": "untersuchen", "vergisst": "vergessen",
    "verletzt": "verletzen", "verliert": "verlieren", "versteht": "verstehen", "versucht": "versuchen",
    "ärgert": "ärgern", "informiert": "informieren", "kontrolliert": "kontrollieren",
    "organisiert": "organisieren", "reserviert": "reservieren", "reservierte": "reservieren",
    "sieht aus": "aussehen", "lernt kennen": "kennen lernen",
}

# Noun without article -> with article (A2 common)
NOUN_ARTICLE = {
    "Geburtstag": "der Geburtstag", "Fragment": "das Fragment", "Klub": "der Klub",
    "Abendessen": "das Abendessen", "Achtung": "die Achtung",
    "Vorwort": "das Vorwort", "Wortgruppen": "die Wortgruppen",
}

# ---- Pronouns (closed set) ----
PRONOUNS = frozenset({
    "ich", "du", "er", "sie", "es", "wir", "ihr", "sie", "Sie",
    "mich", "dich", "ihn", "sie", "es", "uns", "euch", "sie", "Sie",
    "mein", "meine", "dein", "deine", "sein", "seine", "ihr", "ihre", "unser", "unsere", "euer", "euere",
    "sich", "sich über", "andere", "etwas", "nichts", "jemand", "niemand",
    "wer", "was", "welcher", "welche", "welches", "wen", "wem",
})

# ---- Prepositions (closed set) ----
PREPOSITIONS = frozenset({
    "in", "auf", "mit", "nach", "zu", "von", "bei", "aus", "für", "gegen", "ohne", "um",
    "seit", "bis", "durch", "über", "unter", "vor", "hinter", "neben", "zwischen",
    "außer", "außerdem", "außerhalb", "pro", "statt", "trotz", "während",
})

# ---- Expressions (multi-word phrases) ----
def is_expression(de):
    if not de:
        return False
    s = de.strip()
    if " " in s and not s.startswith(("der ", "die ", "das ")):
        # "auf jeden Fall", "alles Gute zum Geburtstag", "am liebsten", "am besten"
        if any(x in s for x in [" zum ", " am ", " auf ", " in ", " zum ", "alles ", "recht haben"]):
            return True
        if s in {"auf jeden Fall", "am liebsten", "am besten", "alles Gute zum Geburtstag", "recht haben", "kontaktlos bezahlen"}:
            return True
    return False

# ---- Classification ----
def classify(de, en, hi):
    de = (de or "").strip()
    if not de:
        return None
    if de in PRONOUNS:
        return "Pronouns"
    if de in PREPOSITIONS:
        return "Prepositions"
    if is_expression(de):
        return "Expressions"
    if de.startswith(("der ", "die ", "das ")) and " " in de:
        return "Nouns"
    if de[0].isupper() and " " not in de:
        return "Nouns"
    low = de.lower()
    if " " in de and de.startswith("sich "):
        return "Verbs"
    if low.endswith(("en", "ern", "eln")) and " " not in de:
        if de not in PREPOSITIONS and de not in PRONOUNS:
            return "Verbs"
    if en and ("to " in str(en)[:15] or " to " in str(en) or str(en).startswith("to ")):
        return "Verbs"
    if " gehen" in de or de.endswith(" gehen"):
        return "Verbs"
    if re.search(r"(lich|ig|isch|bar|sam|los|voll|haft|iv)$", low):
        return "Adjectives"
    if low.endswith("weise") or low in ("gern", "oft", "heute", "hier", "dort", "jetzt", "immer", "nie", "schon", "auch", "nur", "sehr", "so", "dann", "deshalb", "darum", "leider", "vielleicht", "natürlich", "plötzlich", "eigentlich", "zurück", "zusammen", "hin", "her", "dorthin", "hierher", "links", "rechts", "oben", "unten", "innen", "außen", "lange", "kurz", "live", "online", "direkt", "erst", "gleich", "besonders", "sogar", "fast", "gar", "noch", "genau", "eben", "ruhig", "bloß", "mal", "denn", "ja", "doch", "ebenfalls"):
        return "Adverbs"
    if low in ("all", "alle", "ein", "eine", "einer", "kein", "keine", "mehr", "weniger", "viel", "wenig", "bisschen", "paar", "etwas", "genug"):
        return "Adjectives"  # determiners / quantifiers as adj
    return "Expressions"

def normalize_de(de, cat):
    de = (de or "").strip()
    de = CONJUGATED_TO_INFINITIVE.get(de, de)
    if cat == "Nouns" and de in NOUN_ARTICLE:
        return NOUN_ARTICLE[de]
    if cat == "Nouns" and de[0].isupper() and not de.startswith(("der ", "die ", "das ")):
        # Add article if we have it
        return NOUN_ARTICLE.get(de, de)
    return de

# ---- Simple pronunciation (stress on first syllable, ch->kh, sch->sh) ----
def simple_pronunciation(de):
    if not de or " " in de:
        return ""
    s = de
    s = s.replace("ch", "kh").replace("sch", "sh").replace("ä", "eh").replace("ö", "oe").replace("ü", "ue")
    s = s.replace("ß", "ss")
    if len(s) >= 4:
        return (s[:2] + "-" + s[2:]).upper()
    return s.upper()

# ---- Main ----
def main():
    with open(A2_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Target categories (7)
    CAT_ORDER = ["Verbs", "Nouns", "Adjectives", "Adverbs", "Pronouns", "Prepositions", "Expressions"]
    cat_emoji = {"Verbs": "🏃", "Nouns": "📦", "Adjectives": "🟢", "Adverbs": "⏱", "Pronouns": "👤", "Prepositions": "📍", "Expressions": "💬"}
    cat_color = {"Verbs": "#e8f5e9", "Nouns": "#e8eaf6", "Adjectives": "#e3f2fd", "Adverbs": "#fff3e0", "Pronouns": "#f3e5f5", "Prepositions": "#fce4ec", "Expressions": "#fff8e1"}
    buckets = defaultdict(list)  # category -> list of word dicts
    seen = defaultdict(set)    # category -> set of "de"

    def is_participle(de):
        """Past participle (ge-...-en/t), not infinitive."""
        if not de or " " in de:
            return False
        low = de.lower()
        return (low.startswith("ge") and (low.endswith("en") or low.endswith("t"))) or low in ("geboren", "gewesen", "angezogen", "ausgezogen")

    def add_entry(de, en, hi, cat, pronunciation=""):
        if not de or not cat:
            return
        if cat == "Vocabulary":
            cat = "Expressions"  # fallback
        if cat == "Verbs" and is_participle(de):
            return
        de = normalize_de(de, cat)
        if de in seen[cat]:
            return
        seen[cat].add(de)
        pron = pronunciation or simple_pronunciation(de) if len(de) <= 20 else ""
        buckets[cat].append({
            "de": de,
            "pronunciation": pron,
            "en": (en or "").strip() or "—",
            "hi": (hi or "").strip() or "—",
        })

    for cat in data.get("categories", []):
        for w in cat.get("words", []):
            de = (w.get("de") or "").strip()
            en = (w.get("en") or "").strip()
            hi = (w.get("hi") or "").strip()
            if not de:
                continue
            if should_remove(de):
                continue
            if de in SPLIT_MAP:
                for part_de, part_en, part_hi in SPLIT_MAP[de]:
                    c = classify(part_de, part_en, part_hi)
                    if not c or c == "Vocabulary":
                        c = "Verbs" if part_de.endswith("en") else "Nouns"
                    add_entry(part_de, part_en, part_hi, c)
                continue
            if ", " in de and not de.startswith(("der ", "die ", "das ")):
                parts = [p.strip() for p in de.split(",", 1)]
                if len(parts) == 2 and len(parts[0]) > 2 and len(parts[1]) > 2:
                    en_parts = (en or "").split("/") or (en or "").split(";") or [en]
                    hi_parts = (hi or "").split("/") or (hi or "").split(";") or [hi]
                    for i, p in enumerate(parts):
                        ep = en_parts[i].strip() if i < len(en_parts) else en
                        hp = hi_parts[i].strip() if i < len(hi_parts) else hi
                        c = classify(p, ep, hp)
                        if not c or c == "Vocabulary":
                            c = "Verbs" if p.endswith("en") else "Expressions"
                        add_entry(p, ep, hp, c)
                    continue
            c = classify(de, en, hi)
            if not c:
                c = "Expressions"
            add_entry(de, en, hi, c)

    # Build output: only the 7 categories
    categories = []
    for cid in CAT_ORDER:
        words = buckets.get(cid, [])
        categories.append({
            "id": cid,
            "name": cid,
            "nameDe": "",
            "nameHi": "",
            "emoji": cat_emoji.get(cid, "📚"),
            "color": cat_color.get(cid, "#fff8e1"),
            "words": words,
        })
    total_words = sum(len(c["words"]) for c in categories)
    out = {
        "title": data.get("title", "German A2 Vocabulary"),
        "subtitle": "Goethe-Zertifikat A2 Wortliste. Cleaned, base forms only, categorised.",
        "totalWords": total_words,
        "categories": categories,
    }
    with open(A2_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("Repair done. Total words:", total_words)
    for c in categories:
        print("  ", c["id"], len(c["words"]))


if __name__ == "__main__":
    main()
