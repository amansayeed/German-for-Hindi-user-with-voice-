#!/usr/bin/env python3
"""
Fill empty 'hi' in b1-vocabulary.json with simple, everyday Hindi.
Uses English -> Hindi translation (simpler than DE->HI) and an override map
for common terms so normal people can understand (no expert/shard Hindi).
"""
import json
import re
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
B1_JSON = SCRIPT_DIR / "b1-vocabulary.json"
CACHE_JSON = SCRIPT_DIR / "b1_empty_hi_cache.json"

# Simple Hindi overrides: German -> normal Hindi (avoid heavy Sanskrit)
# Use common words a normal person understands.
SIMPLE_HI_OVERRIDE = {
    "anfahren": "टकराना (गाड़ी से)",
    "ausparken": "पीछे निकलना",
    "das Autorennen": "कार रेस",
    "das Autoteil": "कार का पुर्ज़ा",
    "das Büromaterial": "ऑफिस का सामान",
    "das Elektroauto": "इलेक्ट्रिक कार",
    "das Gepäckband": "सामान की पट्टी",
    "das Handgepäck": "हाथ का सामान",
    "das Stipendium": "छात्रवृत्ति",
    "der": "(लेख का हिस्सा)",
    "der Abflug": "उड़ान का समय",
    "der Abstellplatz": "पार्किंग की जगह",
    "der Auszug": "निकाला हुआ हिस्सा",
    "der Bankeinzug": "बैंक कटौती",
    "der Fluggast": "यात्री",
    "der Freundeskreis": "दोस्तों का घेरा",
    "der Kofferraum": "कार की डिक्की",
    "der Milchkarton": "दूध का डिब्बा",
    "der Oldtimer": "पुरानी कार",
    "der Paketbote": "पार्सल वाला",
    "der Reiseplan": "यात्रा की योजना",
    "der Skisport": "स्की खेल",
    "der Sportwagen": "स्पोर्ट्स कार",
    "der Straßenrand": "सड़क का किनारा",
    "der Straßenverkehr": "ट्रैफिक",
    "der Versand": "माल भेजना",
    "der Wohnwagen": "कैरावैन",
    "der Zeitungsbericht": "अख़बार की खबर",
    "die Automarke": "कार का ब्रांड",
    "die Autoversicherung": "कार इंश्योरेंस",
    "die Berufserfahrung": "नौकरी का अनुभव",
    "die Betriebswirtschaft": "व्यापार प्रबंधन",
    "die Dienstreise": "काम की यात्रा",
    "die Fahrerseite": "ड्राइवर की तरफ",
    "die Fluggesellschaft": "एयरलाइन",
    "die Gepäckausgabe": "सामान लेने की जगह",
    "die Pappe": "गत्ता",
    "die Parklücke": "पार्किंग की जगह",
    "die Passkontrolle": "पासपोर्ट चेक",
    "die Pflegekraft": "देखभाल करने वाला",
    "die Reiseplanung": "यात्रा की योजना",
    "die Umschulung": "नई ट्रेनिंग",
    "die Unfallgefahr": "दुर्घटना का खतरा",
    "die Versandkosten": "भेजने का खर्च",
    "die Versandkostenpauschale": "तय भेजने का खर्च",
    "einparken": "गाड़ी पार्क करना",
    "versandkostenfrei": "मुफ़्त डिलीवरी",
    "verärgert": "नाराज़",
    "wegfahren": "गाड़ी लेकर जाना",
    "zugeben": "मान लेना",
    "zurückfahren": "वापस जाना",
    "zügig": "तेज़",
    "anstreichen": "रंगना",
    "befestigen": "मजबूत करना",
    "das Gesundheitszeugnis": "स्वास्थ्य प्रमाणपत्र",
    "der Bezahlvorgang": "भुगतान की प्रक्रिया",
    "geduldig": "सब्र वाला",
    "ungeduldig": "बेसब्र",
    "ungesund": "अनहेल्दी",
    "ärztlich": "डॉक्टर का",
    "übergeben": "उल्टी करना",
    "anprobieren": "पहन कर देखना",
    "aufkommen": "भुगतान करना",
    "das Onlineshopping": "ऑनलाइन खरीदारी",
    "das Shopping": "खरीदारी",
    "der Kaufvertrag": "खरीद का अनुबंध",
    "der Onlineeinkauf": "ऑनलाइन खरीदारी",
    "der Onlineshop": "ऑनलाइन दुकान",
    "der/die Gemüsehändler/in": "सब्ज़ी वाला",
    "der/die Geschäftsführer/in": "मैनेजिंग डायरेक्टर",
    "der/die Käufer/in": "खरीदार",
    "die Geschäftsführung": "प्रबंधन",
    "die Kaufbestätigung": "खरीद की पुष्टि",
    "die Moderation": "संचालन",
    "die Modernisierung": "आधुनिकीकरण",
    "lohnen": "फायदेमंद होना",
    "anstatt": "बजाय",
    "atmungsaktiv": "हवादार",
    "ausprobieren": "आज़माना",
    "das Fertiggericht": "तैयार खाना",
    "das Kochbuch": "रसोई की किताब",
    "das Meerschweinchen": "गिनी पिग",
    "das Trinkwasser": "पीने का पानी",
    "der Biergarten": "बियर गार्डन",
    "der Hartweizen": "मोटा गेहूं",
    "der Kaffeefilter": "कॉफी फिल्टर",
    "der Milchzucker": "दूध वाली चीनी",
    "der Spielfilm": "फ़िल्म",
    "der/die": "कॉफी फिल्टर",
    "die Atmung": "सांस लेना",
    "die Erstellung": "बनाना",
    "die Gemeinsamkeit": "समान बात",
    "die Heizkosten": "गर्मी का खर्च",
    "die Niederlage": "हार",
    "die Obstschale": "फलों की कटोरी",
    "die Speise": "खाना",
    "die Teamfähigkeit": "टीम के साथ काम करना",
    "fleischfrei": "बिना मांस",
    "fleischlos": "शाकाहारी",
    "grundsätzlich": "बुनियादी तौर पर",
    "hämmern": "हथौड़ा मारना",
    "das Eintrittsdatum": "शुरू की तारीख",
    "das Führungszeugnis": "चरित्र प्रमाणपत्र",
    "das Jahrhundert": "सदी",
    "das Jahrzehnt": "दशक",
    "der Büroalltag": "ऑफिस की रोज़मर्रा",
    "der Urlaubstag": "छुट्टी का दिन",
    "der Werktag": "काम का दिन",
    "der Zeitmangel": "समय की कमी",
    "der Zeitraum": "समय सीमा",
    "die Arbeitszeit": "काम के घंटे",
    "die Bürozeit": "ऑफिस के घंटे",
    "die Einsteigezeit": "चढ़ने का समय",
    "die Euroeinführung": "यूरो का चलन",
    "die Festanstellung": "पक्की नौकरी",
    "die Lieblingsbeschäftigung": "पसंदीदा शौक",
    "die Nachkriegszeit": "युद्ध के बाद का समय",
    "die Probezeit": "ट्रायल पीरियड",
    "die Ruhezeit": "आराम का समय",
    "die Zeitverschwendung": "समय बर्बाद",
    "jahrelang": "सालों तक",
    "mehrmals": "कई बार",
    "zeitlich": "समय के हिसाब से",
    "berufen": "नियुक्त करना",
    "das Berufsleben": "नौकरी की ज़िंदगी",
    "das Bewerbungsschreiben": "नौकरी के लिए अर्ज़ी",
    "das Steuerberatungsbüro": "टैक्स सलाह की दुकान",
    "das Vertragsende": "अनुबंध खत्म",
    "das Übersetzungsbüro": "अनुवाद एजेंसी",
    "der Büroraum": "ऑफिस का कमरा",
    "der Firmensitz": "कंपनी का मुख्यालय",
    "der Mietvertrag": "किराए का अनुबंध",
    "der Reinigungsvertrag": "सफाई का अनुबंध",
    "der/die Büroassistent/in": "ऑफिस असिस्टेंट",
    "die Anstellung": "नौकरी",
    "die Arbeitskraft": "कामगार",
    "die Arbeitsweise": "काम करने का तरीका",
    "die Auftragsnummer": "ऑर्डर नंबर",
    "die Bearbeitung": "प्रोसेसिंग",
    "die Begleitperson": "साथ जाने वाला",
    "die Berufsbezeichnung": "नौकरी का नाम",
    "die Berufstätigkeit": "नौकरी",
    "die Gehaltsvorstellung": "वेतन की उम्मीद",
    "die Jobbezeichnung": "जॉब का नाम",
    "die Kundenbefragung": "ग्राहक सर्वे",
    "die Reinigungsfirma": "सफाई कंपनी",
    "die Stellenanzeige": "नौकरी का विज्ञापन",
    "die Vertragsnummer": "अनुबंध नंबर",
    "kundenfreundlich": "ग्राहक के लिए अच्छा",
    "vertragen": "बर्दाश्त करना",
    "zusammenarbeiten": "साथ काम करना",
}


def clean_en_for_translate(en):
    """Take the main part of en (e.g. first phrase before parenthesis)."""
    if not en:
        return ""
    en = en.strip()
    # Remove trailing parenthetical like (Pl.) or (DZ)
    en = re.sub(r"\s*\([^)]*\)\s*$", "", en).strip()
    # Use first part if multiple meanings
    if " " in en and any(
        en.startswith(p) for p in ("to ", "the ", "der ", "die ", "das ")
    ):
        return en
    return en


def main():
    with open(B1_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    cache = {}
    if CACHE_JSON.exists():
        try:
            with open(CACHE_JSON, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            pass

    try:
        from deep_translator import GoogleTranslator
        trans_hi = GoogleTranslator(source="en", target="hi")
        has_translator = True
    except ImportError:
        has_translator = False
        print("Install: pip install deep-translator (for remaining words)")

    updated = 0
    for ci, cat in enumerate(data.get("categories", [])):
        for wi, w in enumerate(cat.get("words", [])):
            if w.get("hi"):
                continue
            de = (w.get("de") or "").strip()
            en = (w.get("en") or "").strip()

            hi = ""
            if de in SIMPLE_HI_OVERRIDE:
                hi = SIMPLE_HI_OVERRIDE[de]
            elif de in cache:
                hi = (cache.get(de) or "").strip()
            elif has_translator and en:
                en_clean = clean_en_for_translate(en)
                if not en_clean:
                    en_clean = en
                # Skip if en looks like German (e.g. "der Abflug departure")
                if en_clean and len(en_clean) > 2 and en_clean.lower() not in (
                    "der", "die", "das", "general", "agb"
                ):
                    try:
                        hi = (trans_hi.translate(en_clean) or "").strip()
                        cache[de] = hi
                        time.sleep(0.12)
                    except Exception as e:
                        print(f"  skip {de!r}: {e}")
                        cache[de] = ""

            if hi:
                data["categories"][ci]["words"][wi]["hi"] = hi
                updated += 1

    with open(B1_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if cache and has_translator:
        with open(CACHE_JSON, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    print(f"Filled {updated} empty Hindi entries. Total cache: {len(cache)}.")


if __name__ == "__main__":
    main()
