#!/usr/bin/env python3
"""
Reorganize B1 vocabulary into thematic categories like A2.
Reads b1-vocabulary.json (single category), assigns each word to a theme by keywords,
writes back with multiple categories. Run embed_b1_data.py after this.
"""
import json
import re
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent
B1_JSON = SCRIPT_DIR / "b1-vocabulary.json"

# Theme order and metadata (match A2). Last is "Other" for unmatched words.
THEMES = [
    {
        "id": "Travel_&_Transport",
        "name": "Travel & Transport",
        "nameDe": "Reisen & Verkehr",
        "nameHi": "राइज़ेन & फेरकेर",
        "emoji": "🚗",
        "color": "#b2dfdb",
        "keywords_de": "reise richtung bahn zug fahrt flug flugzeug auto bus fahrrad straße verkehr ticket hotel koffer gepäck abfahrt ankunft haltestelle flughafen bahnhof schiff fähre führerschein tankstelle reisen fahren fliegen abfahren ankommen park parken fahrkarte reisepass fahr reis flugzeug reisebüro boot motorrad kennzeichen tourismus tourist strand stadtplan route".split(),
        "keywords_en": "travel transport direction train journey flight car bus bicycle street road ticket hotel luggage departure arrival station airport port ship ferry drive petrol park ticket passport".split(),
    },
    {
        "id": "Health_&_Wellness",
        "name": "Health & Wellness",
        "nameDe": "Gesundheit & Wellness",
        "nameHi": "गेज़ुंटहाइट & वेलनेस",
        "emoji": "🏥",
        "color": "#ffebee",
        "keywords_de": "gesund krank arzt medizin krankenhaus apotheke schmerz behandlung therapie fitness wellness patient krankheit heilen schmerzen erkältung blut finger bein magen körper organ zahn gesicht".split(),
        "keywords_en": "health wellness sick doctor medicine hospital pharmacy pain treatment therapy fitness patient illness cure cold blood".split(),
    },
    {
        "id": "Shopping_&_Fashion",
        "name": "Shopping & Fashion",
        "nameDe": "Einkaufen & Mode",
        "nameHi": "आइनकाउफेन & मोडे",
        "emoji": "🛍️",
        "color": "#fff59d",
        "keywords_de": "einkauf kauf mode kleidung kleid jacke hose schuhe laden geschäft preis bezahl verkauf einkaufen kaufen verkaufen anprobieren größe angebot sonderangebot handel händler inserat umtausch abonnement".split(),
        "keywords_en": "shop shopping fashion clothes dress jacket trousers shoes store price pay sell buy size".split(),
    },
    {
        "id": "Food_&_Restaurant",
        "name": "Food & Restaurant",
        "nameDe": "Essen & Restaurant",
        "nameHi": "एसेन & रेस्टोरां",
        "emoji": "🍽️",
        "color": "#c8e6c9",
        "keywords_de": "essen restaurant küche mahlzeit frühstück mittag abendessen kochen gericht getränk kaffee tee wein bier brot fleisch gemüse obst salat suppe fett essig mineralwasser rind kloß zucker schinken".split(),
        "keywords_en": "food eat restaurant kitchen meal breakfast lunch dinner cook dish drink coffee tea wine beer bread meat vegetable fruit salad soup".split(),
    },
    {
        "id": "Time_&_Calendar",
        "name": "Time & Calendar",
        "nameDe": "Zeit & Kalender",
        "nameHi": "त्साइट & कालेंडर",
        "emoji": "📅",
        "color": "#e1bee7",
        "keywords_de": "zeit kalender tag woche monat jahr stunde minute uhr termin datum wann dann heute morgen gestern tage wochen monate jahre stunden minuten täglich wöchentlich jährlich zeitpunkt".split(),
        "keywords_en": "time calendar day week month year hour minute o'clock date appointment when then today tomorrow yesterday".split(),
    },
    {
        "id": "Work_&_Career",
        "name": "Work & Career",
        "nameDe": "Arbeit & Karriere",
        "nameHi": "आर्बाइट & कारिएरे",
        "emoji": "💼",
        "color": "#cfd8dc",
        "keywords_de": "arbeit beruf karriere firma büro chef kollege gehalt arbeitsplatz bewerbung angestellte arbeiten beruf betrieb direktor handwerker ingenieur mechaniker kunde lebenslauf lehrling praktikant vertrag auftrag vertreter unternehmer".split(),
        "keywords_en": "work job career company office boss colleague salary employment application employee".split(),
    },
    {
        "id": "Education_&_Learning",
        "name": "Education & Learning",
        "nameDe": "Bildung & Lernen",
        "nameHi": "बिल्डुंग & लेर्नेन",
        "emoji": "📚",
        "color": "#bbdefb",
        "keywords_de": "bildung lernen schule universität studium kurs prüfung lehrer student unterricht studieren ausbildung seminar institut lexikon".split(),
        "keywords_en": "education learn school university study course exam teacher student lesson".split(),
    },
    {
        "id": "Home_&_Household",
        "name": "Home & Household",
        "nameDe": "Haus & Haushalt",
        "nameHi": "हाउस & हाउसहाल्ट",
        "emoji": "🏠",
        "color": "#fff9c4",
        "keywords_de": "haus haushalt wohnung zimmer möbel küche bad tür fenster wohnen wohnung wohn gebäude eingang herd kühlschrank schrank gang raum empfang".split(),
        "keywords_en": "house home household apartment room furniture kitchen bathroom door window live".split(),
    },
    {
        "id": "Environment_&_Nature",
        "name": "Environment & Nature",
        "nameDe": "Umwelt & Natur",
        "nameHi": "उमवेल्ट & नाटूर",
        "emoji": "🌿",
        "color": "#dcedc8",
        "keywords_de": "umwelt natur wald baum pflanze fluss berg landschaft natürlich strand sand ozean mond".split(),
        "keywords_en": "environment nature forest tree plant river mountain landscape".split(),
    },
    {
        "id": "Hobbies_&_Leisure",
        "name": "Hobbies & Leisure",
        "nameDe": "Hobbys & Freizeit",
        "nameHi": "होबीज़ & फ्राइत्साइट",
        "emoji": "🎮",
        "color": "#b2ebf2",
        "keywords_de": "hobby freizeit spiel spielen lesen buch".split(),
        "keywords_en": "hobby leisure game play read book".split(),
    },
    {
        "id": "Feelings_&_Emotions",
        "name": "Feelings & Emotions",
        "nameDe": "Gefühle & Emotionen",
        "nameHi": "गेफ्यूले & एमोत्सियोनेन",
        "emoji": "💭",
        "color": "#f8bbd9",
        "keywords_de": "gefühl emotion liebe angst freude traurig wütend glücklich hoffnung glück humor dank".split(),
        "keywords_en": "feeling emotion love fear joy sad angry happy hope".split(),
    },
    {
        "id": "Family_&_Relationships",
        "name": "Family & Relationships",
        "nameDe": "Familie & Beziehungen",
        "nameHi": "फामीली & बेत्सीउंगेन",
        "emoji": "👨‍👩‍👧",
        "color": "#e3f2fd",
        "keywords_de": "familie mutter vater kind beziehung eltern ehe partner enkel cousin".split(),
        "keywords_en": "family mother father child relationship parent marriage partner".split(),
    },
    {
        "id": "Celebrations_&_Events",
        "name": "Celebrations & Events",
        "nameDe": "Feiern & Veranstaltungen",
        "nameHi": "फाइर्न & फेरांश्टाल्टुंगेन",
        "emoji": "🎉",
        "color": "#ffe082",
        "keywords_de": "feier veranstaltung fest party feiern feiertag gruß glückwunsch".split(),
        "keywords_en": "celebration event party festival".split(),
    },
    {
        "id": "Communication_&_Technology",
        "name": "Communication & Technology",
        "nameDe": "Kommunikation & Technologie",
        "nameHi": "कोम्युनिकात्सियोन & टेक्नोलोगी",
        "emoji": "📱",
        "color": "#d1c4e9",
        "keywords_de": "kommunikation technologie computer internet telefon mail nachricht senden technik gespräch antwort anruf interview anklicken ausdrucken forum thema kontakt drucker".split(),
        "keywords_en": "communication technology computer internet phone email message send".split(),
    },
    {
        "id": "Banking_&_Finance",
        "name": "Banking & Finance",
        "nameDe": "Bank & Finanzen",
        "nameHi": "बैंक & फिनांत्सेन",
        "emoji": "🏦",
        "color": "#ffccbc",
        "keywords_de": "bank finanz geld kredit zahlen konto bezahlen preis kosten gewinn vertrag anspruch zinsen".split(),
        "keywords_en": "bank finance money credit pay account price cost".split(),
    },
    {
        "id": "Media_&_Entertainment",
        "name": "Media & Entertainment",
        "nameDe": "Medien & Unterhaltung",
        "nameHi": "मेडीएन & उंटरहाल्टुंग",
        "emoji": "📺",
        "color": "#c5cae9",
        "keywords_de": "medien unterhaltung film fernsehen sendung kino magazin foto".split(),
        "keywords_en": "media entertainment film television show".split(),
    },
    {
        "id": "Society_&_Politics",
        "name": "Society & Politics",
        "nameDe": "Gesellschaft & Politik",
        "nameHi": "गेज़ेलशाफ्ट & पोलिटिक",
        "emoji": "🌍",
        "color": "#eceff1",
        "keywords_de": "gesellschaft politik staat recht regierung wahl demokratie gesetz mensch migrant konsulat land verein nachbar mitglied".split(),
        "keywords_en": "society politics state law government election democracy".split(),
    },
    {
        "id": "Music_&_Arts",
        "name": "Music & Arts",
        "nameDe": "Musik & Kunst",
        "nameHi": "मूज़ीक & कुंस्ट",
        "emoji": "🎵",
        "color": "#ffcc80",
        "keywords_de": "musik kunst malen theater konzert lied sänger publikum instrument".split(),
        "keywords_en": "music art paint theatre concert".split(),
    },
    {
        "id": "Daily_Routine",
        "name": "Daily Routine",
        "nameDe": "Tagesablauf",
        "nameHi": "टागेसआब्लाउफ",
        "emoji": "⏰",
        "color": "#80deea",
        "keywords_de": "tagesablauf morgen abend wachen schlafen aufstehen duschen frühstück schlaf wach".split(),
        "keywords_en": "daily routine morning evening wake sleep get up shower breakfast".split(),
    },
    {
        "id": "Animals_&_Wildlife",
        "name": "Animals & Wildlife",
        "nameDe": "Tiere & Tierwelt",
        "nameHi": "टीरे & टीरवेल्ट",
        "emoji": "🐾",
        "color": "#ffe0b2",
        "keywords_de": "tier vogel hund katze pferd fisch".split(),
        "keywords_en": "animal bird dog cat horse fish".split(),
    },
    {
        "id": "Weather_&_Climate",
        "name": "Weather & Climate",
        "nameDe": "Wetter & Klima",
        "nameHi": "वेटर & क्लीमा",
        "emoji": "🌤️",
        "color": "#81d4fa",
        "keywords_de": "wetter klima sonne regen schnee wind gewitter donner blitz neblig".split(),
        "keywords_en": "weather climate sun rain snow wind".split(),
    },
    {
        "id": "Sports_&_Activities",
        "name": "Sports & Activities",
        "nameDe": "Sport & Aktivitäten",
        "nameHi": "श्पोर्ट & आक्टिविटेटेन",
        "emoji": "⚽",
        "color": "#ffab91",
        "keywords_de": "sport aktivität spielen ball laufen sieg sieger wettbewerb trainer".split(),
        "keywords_en": "sport activity play ball run".split(),
    },
    # Categories for words that don't fit the themes above (split "Other" by word type)
    {
        "id": "Adverbs_&_Connectors",
        "name": "Adverbs & Connectors",
        "nameDe": "Adverbien & Konnektoren",
        "nameHi": "क्रिया विशेषण और संयोजक",
        "emoji": "🔗",
        "color": "#b39ddb",
        "keywords_de": "weil dass wenn obwohl deshalb trotzdem aber oder sondern also daher deshalb danach dabei davon dazu zwar entweder weder jedoch zwar immer schon noch oft manchmal vielleicht gern lieber sehr ganz nur sogar besonders eigentlich vielleicht bald beinahe nun nämlich plötzlich bestimmt andererseits bevor dagegen damit".split(),
        "keywords_en": "because that if although therefore however but or so then after there perhaps often sometimes maybe rather very only especially actually".split(),
    },
    {
        "id": "Prepositions_&_Particles",
        "name": "Prepositions & Particles",
        "nameDe": "Präpositionen & Partikeln",
        "nameHi": "संबंधबोधक और कण",
        "emoji": "📍",
        "color": "#90a4ae",
        "keywords_de": "während gegenüber innerhalb anstatt trotz wegen zwischen neben hinter oberhalb unterhalb beiderseits seitlich".split(),
        "keywords_en": "during opposite within instead despite because between next behind above below".split(),
        "exact_words_de": "auf aus bei mit nach von zu in an um für gegen über unter ohne bis seit".split(),
    },
    {
        "id": "Adjectives_&_Descriptors",
        "name": "Adjectives & Descriptors",
        "nameDe": "Adjektive & Beschreibungen",
        "nameHi": "विशेषण और विवरण",
        "emoji": "✨",
        "color": "#ffcc80",
        "keywords_de": "gut neu schnell langsam wichtig möglich richtig falsch alt jung groß klein viel wenig ganz halb einfach schwer klar deutlich sicher möglich angenehm anstrengend bequem nützlich notwendig nötig ausgezeichnet aufmerksam anwesend ausreichend befriedigend nervös nett niedrig offen ordentlich perfekt praktisch positiv realistisch".split(),
        "keywords_en": "good new fast slow important possible right wrong old young big small much little whole half easy hard clear sure possible".split(),
    },
    {
        "id": "Common_Verbs",
        "name": "Common Verbs",
        "nameDe": "Häufige Verben",
        "nameHi": "सामान्य क्रियाएं",
        "emoji": "🏃",
        "color": "#a5d6a7",
        "keywords_de": "machen gehen kommen sagen geben nehmen wissen denken finden halten stehen liegen setzen lassen bleiben werden haben sein anfangen aufhören beenden ändern verbessern anwenden bestätigen antworten anbieten aufpassen aufräumen ausfüllen bringen vergleichen ersetzen prüfen analysieren beantragen".split(),
        "keywords_en": "make go come say give take know think find hold stand lie put let stay become have be".split(),
    },
    {
        "id": "Pronouns_&_Quantifiers",
        "name": "Pronouns & Quantifiers",
        "nameDe": "Pronomen & Mengenangaben",
        "nameHi": "सर्वनाम और परिमाणक",
        "emoji": "👤",
        "color": "#ce93d8",
        "keywords_de": "etwas nichts jemand niemand man alle jeder jede welcher einige mehrere beide".split(),
        "keywords_en": "something nothing someone nobody one all every which some several both".split(),
    },
    {
        "id": "Abstract_&_Concepts",
        "name": "Abstract & Concepts",
        "nameDe": "Abstrakt & Begriffe",
        "nameHi": "अमूर्त और अवधारणाएं",
        "emoji": "💡",
        "color": "#b0bec5",
        "keywords_de": "weise grund teil art fall mal beziehung idee problem lösung bedeutung unterschied vergleich dokument formular gegenstand ding mittel faktor eindruck".split(),
        "keywords_en": "way reason part kind case time relation idea problem solution meaning difference comparison".split(),
    },
    {
        "id": "Negation_&_Particles",
        "name": "Negation & Particles",
        "nameDe": "Verneinung & Partikeln",
        "nameHi": "निषेध और कण",
        "emoji": "🚫",
        "color": "#ef9a9a",
        "keywords_de": "nirgends nirgendwo verneinung".split(),
        "keywords_en": "not never nowhere neither".split(),
        "exact_words_de": "nicht nie nein ob außer".split(),
    },
    {
        "id": "Questions_&_Interrogatives",
        "name": "Questions & Interrogatives",
        "nameDe": "Fragen & Fragewörter",
        "nameHi": "प्रश्न और प्रश्नवाचक",
        "emoji": "❓",
        "color": "#fff59d",
        "keywords_de": "warum wieso welcher welche welches".split(),
        "keywords_en": "why which what when where how who".split(),
        "exact_words_de": "wer was wie wann wo".split(),
    },
    {
        "id": "Location_&_Direction",
        "name": "Location & Direction",
        "nameDe": "Ort & Richtung",
        "nameHi": "स्थान और दिशा",
        "emoji": "🧭",
        "color": "#81c784",
        "keywords_de": "außen innen oben unten nördlich südlich östlich westlich links rechts seitlich quer".split(),
        "keywords_en": "outside inside above below north south east west left right across".split(),
    },
    {
        "id": "Quantity_&_Degree",
        "name": "Quantity & Degree",
        "nameDe": "Menge & Grad",
        "nameHi": "मात्रा और डिग्री",
        "emoji": "📊",
        "color": "#64b5f6",
        "keywords_de": "paar mehrere weniger mehr genug ausreichend zahl menge prozent grad".split(),
        "keywords_en": "couple several less more enough sufficient number amount percent degree".split(),
    },
    {
        "id": "Reflexive_&_Self",
        "name": "Reflexive & Self",
        "nameDe": "Reflexiv & Selbst",
        "nameHi": "निजवाचक और स्वयं",
        "emoji": "🔄",
        "color": "#b2dfdb",
        "keywords_de": "sich ausruhen fürchten trennen verabreden vorstellen waschen verstecken überzeugen verbessern verändern aussuchen schneiden stoßen zwingen".split(),
        "keywords_en": "rest fear separate arrange imagine wash hide convince improve change choose cut bump force oneself".split(),
    },
    {
        "id": "Manner_&_Style",
        "name": "Manner & Style",
        "nameDe": "Art & Stil",
        "nameHi": "ढंग और शैली",
        "emoji": "🎭",
        "color": "#d1c4e9",
        "keywords_de": "elektronisch normalerweise offiziell parallel politisch technisch theoretisch stilistisch vermutlich allgemein individuell endgültig endlich schließlich ursprünglich vorläufig zufällig zusätzlich einerseits ebenfalls überhaupt äußerlich sogenannt".split(),
        "keywords_en": "electronically normally officially parallel politically technically theoretically generally individually finally originally provisionally randomly additionally".split(),
    },
    {
        "id": "Places_&_Structures",
        "name": "Places & Structures",
        "nameDe": "Orte & Strukturen",
        "nameHi": "स्थान और संरचनाएं",
        "emoji": "🏛️",
        "color": "#bcaaa4",
        "keywords_de": "saal halle mauer wand zone galerie grundstück tal balkon tor ausgang eingang zentrum abfalleimer".split(),
        "keywords_en": "hall wall zone gallery valley balcony gate exit entrance center".split(),
    },
    {
        "id": "Emergency_&_Safety",
        "name": "Emergency & Safety",
        "nameDe": "Notfall & Sicherheit",
        "nameHi": "आपातकाल और सुरक्षा",
        "emoji": "🆘",
        "color": "#ff8a80",
        "keywords_de": "notruf notfall unfall not einbrecher einbruch gefängnis".split(),
        "keywords_en": "emergency accident burglar break-in".split(),
    },
    {
        "id": "Reason_&_Proof",
        "name": "Reason & Proof",
        "nameDe": "Begründung & Beweis",
        "nameHi": "कारण और प्रमाण",
        "emoji": "📋",
        "color": "#a5d6a7",
        "keywords_de": "begründen beweisen hinweisen begründung beweis".split(),
        "keywords_en": "justify prove point out reason proof".split(),
    },
    {
        "id": "Body_&_Appearance",
        "name": "Body & Appearance",
        "nameDe": "Körper & Aussehen",
        "nameHi": "शरीर और रूप",
        "emoji": "🧍",
        "color": "#ffccbc",
        "keywords_de": "bart bauch blind blond männlich weiblich".split(),
        "keywords_en": "beard stomach blind blond masculine feminine".split(),
    },
    {
        "id": "Tools_&_Materials",
        "name": "Tools & Materials",
        "nameDe": "Werkzeuge & Materialien",
        "nameHi": "उपकरण और सामग्री",
        "emoji": "🔧",
        "color": "#90a4ae",
        "keywords_de": "werkzeug material apparat gerät".split(),
        "keywords_en": "tool material apparatus device".split(),
    },
    {
        "id": "Start_&_Conclusion",
        "name": "Start & Conclusion",
        "nameDe": "Anfang & Abschluss",
        "nameHi": "शुरुआत और समापन",
        "emoji": "▶️",
        "color": "#80cbc4",
        "keywords_de": "anfang beginn abschluss abschnitt anfangs".split(),
        "keywords_en": "beginning start conclusion section initially".split(),
    },
    {
        "id": "Writing_&_Recording",
        "name": "Writing & Recording",
        "nameDe": "Schreiben & Aufzeichnen",
        "nameHi": "लिखना और रिकॉर्ड करना",
        "emoji": "✍️",
        "color": "#ce93d8",
        "keywords_de": "aufschreiben ausdruck ausstellen schreiben".split(),
        "keywords_en": "write down expression exhibit write".split(),
    },
    {
        "id": "Legal_&_Crime",
        "name": "Legal & Crime",
        "nameDe": "Recht & Kriminalität",
        "nameHi": "कानून और अपराध",
        "emoji": "⚖️",
        "color": "#7986cb",
        "keywords_de": "täter verbrecher verdacht vorwurf konflikt verbrechen urteil zoll".split(),
        "keywords_en": "perpetrator criminal suspicion accusation conflict crime verdict customs".split(),
    },
    {
        "id": "People_&_Roles",
        "name": "People & Roles",
        "nameDe": "Menschen & Rollen",
        "nameHi": "लोग और भूमिकाएं",
        "emoji": "👥",
        "color": "#4db6ac",
        "keywords_de": "könig nachbar praktikant profi sänger trainer unternehmer vertreter übersetzer zuschauer zuhörer empfänger bekannte angehörige verwandte".split(),
        "keywords_en": "king neighbor intern professional singer coach entrepreneur representative translator spectator listener recipient acquaintance relative".split(),
    },
    {
        "id": "Plans_&_Suggestions",
        "name": "Plans & Suggestions",
        "nameDe": "Pläne & Vorschläge",
        "nameHi": "योजनाएं और सुझाव",
        "emoji": "📝",
        "color": "#ffb74d",
        "keywords_de": "plan versuch vorschlag aktion zustand zusammenhang absicht".split(),
        "keywords_en": "plan attempt suggestion action condition connection intention".split(),
    },
    {
        "id": "Feelings_&_Reactions",
        "name": "Feelings & Reactions",
        "nameDe": "Gefühle & Reaktionen",
        "nameHi": "भावनाएं और प्रतिक्रियाएं",
        "emoji": "💬",
        "color": "#f48fb1",
        "keywords_de": "enttäuschen traum wundern freuen".split(),
        "keywords_en": "disappoint dream wonder rejoice".split(),
    },
    {
        "id": "Other_&_General",
        "name": "Other & General",
        "nameDe": "Sonstiges & Allgemein",
        "nameHi": "अन्य और सामान्य",
        "emoji": "📖",
        "color": "#e0e0e0",
        "keywords_de": [],  # catch-all last
        "keywords_en": [],
    },
]


def normalize(s):
    if not s:
        return ""
    s = (s or "").strip().lower()
    for old, new in [("ä", "a"), ("ö", "o"), ("ü", "u"), ("ß", "ss")]:
        s = s.replace(old, new)
    s = re.sub(r"[^\w\s]", " ", s)
    return s


def first_letter_id(de_str):
    """Return Vocabulary_X for words that end up in Other - by first letter."""
    n = normalize(de_str or "")
    n = n.replace(" ", "")
    for c in n:
        if c.isalpha():
            return "Vocabulary_" + c.upper()
    return "Vocabulary_0"


# Letter-based categories for any words not matched by theme (so Other ends up empty)
LETTER_CATEGORIES = []
_colors = ["#e3f2fd", "#e8f5e9", "#fff3e0", "#f3e5f5", "#fce4ec", "#e0f7fa", "#f1f8e9", "#ede7f6"]
for i, letter in enumerate(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["0"]):
    lid = "Vocabulary_" + letter
    LETTER_CATEGORIES.append({
        "id": lid,
        "name": "Vocabulary (" + letter + ")",
        "nameDe": "Wortschatz (" + letter + ")",
        "nameHi": "शब्दावली (" + letter + ")",
        "emoji": "📗",
        "color": _colors[i % len(_colors)],
    })


def assign_theme(word, themes_with_keywords):
    de = normalize(word.get("de") or "")
    en = normalize(word.get("en") or "")
    for t in themes_with_keywords:
        if t["id"] == "Other_&_General":
            return t["id"]
        exact = t.get("exact_words_de") or []
        if exact and de in {normalize(w) for w in exact}:
            return t["id"]
        min_len = 3
        for kw in t["keywords_de"]:
            if len(kw) >= min_len and normalize(kw) in de:
                return t["id"]
        for kw in t["keywords_en"]:
            if len(kw) >= min_len and kw in en:
                return t["id"]
    return "Other_&_General"


def main():
    with open(B1_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Get words from current structure (single category or multiple)
    all_words = []
    for cat in data["categories"]:
        all_words.extend(cat["words"])

    # Assign each word to a theme
    by_theme = defaultdict(list)
    for w in all_words:
        tid = assign_theme(w, THEMES)
        by_theme[tid].append(w)

    # Move all "Other & General" words into letter-based categories so no word remains in Other
    other_words = by_theme.pop("Other_&_General", [])
    for w in other_words:
        lid = first_letter_id(w.get("de") or "")
        by_theme[lid].append(w)

    # Build new categories: thematic first (exclude Other), then letter categories
    categories = []
    for t in THEMES:
        if t["id"] == "Other_&_General":
            continue
        words = by_theme.get(t["id"], [])
        if not words:
            continue
        categories.append({
            "id": t["id"],
            "name": t["name"],
            "nameDe": t["nameDe"],
            "nameHi": t["nameHi"],
            "emoji": t["emoji"],
            "color": t["color"],
            "words": words,
        })
    # Add letter-based categories for remaining words (Vocabulary A, B, C, ...)
    for t in LETTER_CATEGORIES:
        words = by_theme.get(t["id"], [])
        if not words:
            continue
        categories.append({
            "id": t["id"],
            "name": t["name"],
            "nameDe": t["nameDe"],
            "nameHi": t["nameHi"],
            "emoji": t["emoji"],
            "color": t["color"],
            "words": words,
        })

    total = sum(len(c["words"]) for c in categories)
    out = {
        "title": data.get("title", "German B1 Vocabulary"),
        "subtitle": data.get("subtitle", ""),
        "totalWords": total,
        "categories": categories,
    }

    with open(B1_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Wrote {B1_JSON} with {total} words in {len(categories)} categories.")
    for c in categories:
        print(f"  {c['name']}: {len(c['words'])} words")


if __name__ == "__main__":
    main()
