#!/usr/bin/env python3
"""
Build 2980-most-frequent-german-nouns.json from
https://frequencylists.blogspot.com/2016/01/the-2980-most-frequently-used-german.html
- Complete list of 2980 nouns with normal rank 1-2980
- Each entry: rank, en, article, de, plural, hi (Hindi - empty if no source)
"""
import re
import json
import urllib.request
from collections import defaultdict

URL = "https://frequencylists.blogspot.com/2016/01/the-2980-most-frequently-used-german.html"
TARGET = 2980

# German noun -> plural (for entries where source had "-"; add correct plural where one exists)
# German noun -> plural. For uncountable/same-form nouns we use the same word.
DE_TO_PLURAL = {
    "Art": "Arten", "Mitte": "Mitten", "Wende": "Wenden", "Volk": "Völker", "Gas": "Gase",
    "Energie": "Energien", "Erleichterung": "Erleichterungen", "Brot": "Brote", "Öl": "Öle",
    "Freude": "Freuden", "Grund": "Gründe", "Länge": "Längen", "Wissenschaft": "Wissenschaften",
    "Mangel": "Mängel", "Verteidigung": "Verteidigungen", "Dekan": "Dekane", "Stand": "Stände",
    "Verantwortung": "Verantwortungen", "Existenz": "Existenzen", "Unterstützung": "Unterstützungen",
    "Darm": "Därme", "Fantasie": "Fantasien", "Mode": "Moden", "Schaden": "Schäden",
    "Fortschritt": "Fortschritte", "Verwirrung": "Verwirrungen", "Dampf": "Dämpfe",
    "Krebs": "Krebse", "Abwesenheit": "Abwesenheiten", "Bau": "Bauten", "Jagd": "Jagden",
    "Schlag": "Schläge", "Boden": "Böden", "Heck": "Hecks", "Forschung": "Forschungen",
    "Freiheit": "Freiheiten", "Schicksal": "Schicksale", "Aufregung": "Aufregungen",
    "Tempo": "Tempos", "Abschied": "Abschiede", "Mitternacht": "Mitternächte",
    "Eigentum": "Eigentümer", "Ausrüstung": "Ausrüstungen", "Sicherheit": "Sicherheiten",
    "Mittag": "Mittage", "Dienstmädchen": "Dienstmädchen", "Whisky": "Whiskys",
    "Stahl": "Stähle", "Recht": "Rechte", "Interesse": "Interessen",
    "Armee": "Armeen", "Vergangenheit": "Vergangenheiten", "Anwesenheit": "Anwesenheiten",
    "Glaube": "Glauben", "Ehre": "Ehren", "Kindheit": "Kindheiten",
    "Verständnis": "Verständnisse", "Dämmerung": "Dämmerungen", "Bildung": "Bildungen",
    "Zugriff": "Zugriffe", "Dunkelheit": "Dunkelheiten", "Kunst": "Künste", "Plastik": "Plastiken",
    "Natur": "Naturen",
    # All remaining: real plurals or same form (uncountable/invariable)
    "Leute": "Leute", "Wasser": "Wasser", "Luft": "Luft", "Arbeit": "Arbeiten",
    "Verstand": "Verstände", "Geld": "Geld", "Liebe": "Lieben", "Anderen": "Anderen",
    "Blut": "Blut", "Hölle": "Höllen", "Ruhe": "Ruhe", "Erde": "Erden", "Essen": "Essen",
    "Stille": "Stille", "Macht": "Mächte", "Kleidung": "Kleidungen", "Aufmerksamkeit": "Aufmerksamkeiten",
    "Musik": "Musik", "Alter": "Alter", "Polizei": "Polizei", "Holz": "Hölzer",
    "Schwierigkeit": "Schwierigkeiten", "Nachrichten": "Nachrichten", "Eins": "Eins",
    "Wille": "Willen", "Zeug": "Zeug", "Scheiße": "Scheiße", "Schnee": "Schnee",
    "Angst": "Ängste", "Miss": "Miss", "Gold": "Gold", "Norden": "Norden", "Süden": "Süden",
    "Hitze": "Hitze", "Schlaf": "Schlaf", "Westen": "Westen", "Silber": "Silber",
    "Staub": "Stäube", "Großmutter": "Großmütter", "Osten": "Osten", "Leder": "Leder",
    "Sex": "Sex", "Schmutz": "Schmutz", "Sand": "Sande", "Fleisch": "Fleisch",
    "Parken": "Parken", "Glück": "Glück", "Honig": "Honige", "Lachen": "Lachen",
    "Ärger": "Ärger", "Schweiß": "Schweiß", "Wetter": "Wetter", "Grün": "Grün",
    "Frieden": "Frieden", "Verkehr": "Verkehr", "Englisch": "Englisch", "Milch": "Milch",
    "Verlangen": "Verlangen", "Grinsen": "Grinsen", "Wissen": "Wissen", "Kälte": "Kälte",
    "Jeans": "Jeans", "Weiß": "Weiß", "Denken": "Denken", "Publikum": "Publikum",
    "Sonnenlicht": "Sonnenlicht", "Personal": "Personal", "Sahne": "Sahne",
    "Lesen": "Lesen", "Spaß": "Spaße", "Post": "Post", "Durcheinander": "Durcheinander",
    "Schlamm": "Schlamm", "Seide": "Seiden", "Esszimmer": "Esszimmer", "Nicken": "Nicken",
    "Presse": "Presse", "Daten": "Daten", "Horror": "Horror", "Süßigkeiten": "Süßigkeiten",
    "Gesundheit": "Gesundheit", "Aussehen": "Aussehen", "Selbst": "Selbst",
    "Bargeld": "Bargeld", "Magie": "Magie", "Gerechtigkeit": "Gerechtigkeiten",
    "Stolz": "Stolz", "Jugend": "Jugend", "Zucker": "Zucker", "Schokolade": "Schokoladen",
    "Atmen": "Atmen", "Salz": "Salz", "Respekt": "Respekt", "Innere": "Innere",
    "Blei": "Blei", "Terror": "Terror", "Baumwolle": "Baumwolle", "Schande": "Schande",
    "Umstände": "Umstände", "Panik": "Panik", "Verhalten": "Verhalten", "Wärme": "Wärme",
    "Nebel": "Nebel", "Gehen": "Gehen", "Gleichgewicht": "Gleichgewichte", "Blau": "Blau",
    "Trauer": "Trauer", "Abendessen": "Abendessen", "Komfort": "Komfort", "Fiktion": "Fiktionen",
    "Angeln": "Angeln", "Schwarz": "Schwarz", "Schaudern": "Schaudern", "Müll": "Müll",
    "Mais": "Mais", "Intelligenz": "Intelligenz", "Urheberrecht": "Urheberrechte",
    "Neugierde": "Neugierde", "Poesie": "Poesie", "Porzellan": "Porzellan", "Mut": "Mut",
    "Geduld": "Geduld", "Schuld": "Schuld", "Weinen": "Weinen", "Make-up": "Make-ups",
    "Klopfen": "Klopfen", "Böse": "Böse", "Schwerkraft": "Schwerkraft", "Reis": "Reis",
    "starren": "starren", "Gewalt": "Gewalt", "Humor": "Humor", "Kies": "Kies",
    "Butter": "Butter", "Ganze": "Ganze", "Braun": "Braun", "Messing": "Messing",
    "Gute": "Gute", "Weisheit": "Weisheiten", "Wäsche": "Wäsche", "Donner": "Donner",
    "Gebrüll": "Gebrüll", "Mondschein": "Mondschein", "Wolle": "Wolle", "Mitleid": "Mitleid",
    "Samt": "Samt", "Wut": "Wut", "Zufriedenheit": "Zufriedenheiten", "Unkraut": "Unkräuter",
    "Stretch": "Stretch", "Kosten": "Kosten",
}

# English -> Hindi meanings for common nouns (used when en matches)
EN_TO_HI = {
    "time": "समय", "man": "आदमी", "hand": "हाथ", "day": "दिन", "way": "रास्ता", "eye": "आँख", "thing": "चीज़",
    "head": "सिर", "year": "साल", "room": "कमरा", "door": "दरवाज़ा", "woman": "औरत", "face": "चेहरा",
    "mother": "माँ", "people": "लोग", "night": "रात", "house": "घर", "father": "पिता", "life": "जीवन",
    "back": "पीठ", "voice": "आवाज़", "girl": "लड़की", "place": "जगह", "boy": "लड़का", "car": "कार",
    "side": "तरफ़", "arm": "बाँह", "child": "बच्चा", "word": "शब्द", "moment": "पल", "hair": "बाल",
    "foot": "पैर", "water": "पानी", "light": "रोशनी", "world": "दुनिया", "name": "नाम", "friend": "दोस्त",
    "window": "खिड़की", "body": "शरीर", "table": "मेज़", "morning": "सुबह", "bed": "बिस्तर", "wall": "दीवार",
    "street": "गली", "school": "स्कूल", "air": "हवा", "floor": "फर्श", "hour": "घंटा", "end": "अंत",
    "family": "परिवार", "guy": "आदमी", "kind": "तरह", "minute": "मिनट", "story": "कहानी", "god": "भगवान",
    "week": "सप्ताह", "work": "काम", "shoulder": "कंधा", "part": "हिस्सा", "mind": "दिमाग", "book": "किताब",
    "finger": "उंगली", "mouth": "मुँह", "kid": "बच्चा", "glass": "ग्लास", "tree": "पेड़", "sound": "आवाज़",
    "line": "लाइन", "wife": "पत्नी", "heart": "दिल", "money": "पैसा", "phone": "फ़ोन", "look": "नज़र",
    "leg": "पैर", "chair": "कुर्सी", "office": "ऑफिस", "brother": "भाई", "question": "सवाल", "city": "शहर",
    "month": "महीना", "baby": "बच्चा", "home": "घर", "dog": "कुत्ता", "road": "सड़क", "idea": "विचार",
    "kitchen": "रसोई", "son": "बेटा", "job": "नौकरी", "paper": "कागज़", "sister": "बहन", "smile": "मुस्कान",
    "point": "बिंदु", "thought": "विचार", "love": "प्यार", "town": "कस्बा", "death": "मौत", "ground": "जमीन",
    "fire": "आग", "step": "कदम", "blood": "खून", "fact": "तथ्य", "breath": "साँस", "lip": "होंठ",
    "sun": "सूरज", "building": "इमारत", "number": "नंबर", "husband": "पति", "parent": "माता-पिता",
    "corner": "कोना", "problem": "समस्या", "couple": "जोड़ा", "daughter": "बेटी", "bag": "बैग",
    "business": "व्यापार", "sky": "आसमान", "box": "डिब्बा", "person": "व्यक्ति", "reason": "कारण",
    "right": "अधिकार", "skin": "त्वचा", "case": "मामला", "piece": "टुकड़ा", "doctor": "डॉक्टर",
    "edge": "किनारा", "picture": "तस्वीर", "sense": "समझ", "ear": "कान", "second": "सेकंड",
    "lady": "महिला", "neck": "गर्दन", "wind": "हवा", "stone": "पत्थर", "coffee": "कॉफ़ी", "ship": "जहाज़",
    "earth": "धरती", "food": "खाना", "horse": "घोड़ा", "field": "खेत", "war": "युद्ध", "letter": "चिट्ठी",
    "space": "जगह", "evening": "शाम", "dream": "सपना", "apartment": "अपार्टमेंट", "game": "खेल",
    "summer": "गर्मी", "silence": "चुप्पी", "power": "ताकत", "sign": "निशान", "sky": "आसमान",
    "person": "व्यक्ति", "nose": "नाक", "shadow": "परछाई", "police": "पुलिस", "memory": "याद",
    "color": "रंग", "knee": "घुटना", "wood": "लकड़ी", "shirt": "कमीज़", "party": "पार्टी", "country": "देश",
    "truck": "ट्रक", "tooth": "दाँत", "bill": "बिल", "scene": "दृश्य", "land": "जमीन", "star": "तारा",
    "bird": "चिड़िया", "bedroom": "शयनकक्ष", "uncle": "चाचा", "group": "समूह", "truth": "सच",
    "station": "स्टेशन", "tear": "आँसू", "class": "कक्षा", "sea": "समुद्र", "animal": "जानवर",
    "center": "केंद्र", "feeling": "भावना", "store": "दुकान", "mountain": "पहाड़", "news": "खबर",
    "shoe": "जूता", "cat": "बिल्ली", "bottle": "बोतल", "call": "कॉल", "rain": "बारिश", "suit": "सूट",
    "wall": "दीवार", "school": "स्कूल", "church": "चर्च", "hill": "पहाड़ी", "company": "कंपनी",
    "ball": "गेंद", "student": "छात्र", "screen": "स्क्रीन", "kitchen": "रसोई", "garden": "बगीचा",
    "train": "ट्रेन", "shop": "दुकान", "art": "कला", "beer": "बियर", "island": "द्वीप", "bus": "बस",
    "park": "पार्क", "plate": "प्लेट", "jacket": "जैकेट", "help": "मदद", "grass": "घास", "brain": "दिमाग",
    "trip": "यात्रा", "hotel": "होटल", "gift": "उपहार", "restaurant": "रेस्तराँ", "key": "चाबी",
    "computer": "कंप्यूटर", "flower": "फूल", "ring": "अंगूठी", "bathroom": "बाथरूम", "moon": "चाँद",
    "song": "गाना", "soldier": "सैनिक", "radio": "रेडियो", "history": "इतिहास", "fish": "मछली",
    "question": "सवाल", "doctor": "डॉक्टर", "water": "पानी", "mother": "माँ", "father": "पिता",
    "door": "दरवाज़ा", "room": "कमरा", "house": "घर", "book": "किताब", "hand": "हाथ", "eye": "आँख",
    "night": "रात", "day": "दिन", "year": "साल", "way": "रास्ता", "man": "आदमी", "child": "बच्चा",
    "woman": "औरत", "friend": "दोस्त", "car": "कार", "street": "गली", "table": "मेज़", "bed": "बिस्तर",
    "door": "दरवाज़ा", "window": "खिड़की", "money": "पैसा", "heart": "दिल", "love": "प्यार", "death": "मौत",
    "food": "खाना", "city": "शहर", "country": "देश", "world": "दुनिया", "name": "नाम", "time": "समय",
    "work": "काम", "school": "स्कूल", "family": "परिवार", "number": "नंबर", "problem": "समस्या",
    "question": "सवाल", "point": "बिंदु", "room": "कमरा", "moment": "पल", "word": "शब्द", "place": "जगह",
    "face": "चेहरा", "head": "सिर", "body": "शरीर", "arm": "बाँह", "leg": "पैर", "hand": "हाथ",
    "foot": "पैर", "finger": "उंगली", "mouth": "मुँह", "ear": "कान", "nose": "नाक", "eye": "आँख",
    "hair": "बाल", "blood": "खून", "voice": "आवाज़", "sun": "सूरज", "moon": "चाँद", "star": "तारा",
    "fire": "आग", "water": "पानी", "rain": "बारिश", "snow": "बर्फ", "wind": "हवा", "light": "रोशनी",
    "dark": "अंधेरा", "morning": "सुबह", "evening": "शाम", "night": "रात", "week": "सप्ताह",
    "month": "महीना", "year": "साल", "time": "समय", "day": "दिन", "hour": "घंटा", "minute": "मिनट",
    # More nouns from the 2980 list
    "dad": "पिता", "mom": "माँ", "rest": "आराम", "hell": "नरक", "rose": "गुलाब", "hat": "टोपी",
    "gold": "सोना", "cloud": "बादल", "view": "नज़ारा", "driver": "चालक", "cup": "कप", "figure": "आकृति",
    "path": "रास्ता", "metal": "धातु", "plan": "योजना", "cop": "पुलिस", "north": "उत्तर", "south": "दक्षिण",
    "pair": "जोड़ी", "lord": "भगवान", "heat": "गर्मी", "sleep": "नींद", "beat": "धड़कन", "knife": "चाकू",
    "spot": "धब्बा", "message": "संदेश", "mark": "निशान", "teacher": "शिक्षक", "village": "गाँव", "winter": "सर्दी",
    "law": "कानून", "surface": "सतह", "bank": "बैंक", "team": "टीम", "position": "पद", "stomach": "पेट",
    "turn": "मोड़", "west": "पश्चिम", "lunch": "दोपहर का खाना", "change": "बदलाव", "soul": "आत्मा", "leaf": "पत्ता",
    "show": "शो", "gate": "दरवाज़ा", "palm": "हथेली", "plastic": "प्लास्टिक", "force": "बल", "beach": "समुद्र तट",
    "president": "राष्ट्रपति", "shape": "आकार", "smoke": "धुआँ", "wheel": "पहिया", "silver": "चाँदी", "roof": "छत",
    "weight": "वजन", "tongue": "जीभ", "tea": "चाय", "track": "पटरी", "angle": "कोण", "form": "फॉर्म", "tone": "सुर",
    "circle": "वृत्त", "spring": "बसंत", "porch": "बरामदा", "sheet": "चादर", "member": "सदस्य", "pool": "पूल",
    "need": "जरूरत", "hope": "उम्मीद", "lake": "झील", "breast": "स्तन", "surprise": "आश्चर्य", "interest": "रुचि",
    "bottom": "तल", "spirit": "आत्मा", "block": "ब्लॉक", "language": "भाषा", "bridge": "पुल", "dust": "धूल",
    "cell": "कोशिका", "wine": "शराब", "boot": "जूता", "choice": "चुनाव", "row": "पंक्ति", "talk": "बातचीत",
    "plane": "विमान", "watch": "घड़ी", "information": "जानकारी", "grandmother": "दादी", "wing": "पंख",
    "club": "क्लब", "master": "मालिक", "grace": "कृपा", "forest": "जंगल", "size": "आकार", "set": "सेट",
    "marriage": "शादी", "forehead": "माथा", "storm": "तूफान", "situation": "स्थिति", "counter": "काउंटर",
    "neighbor": "पड़ोसी", "photo": "फोटो", "stage": "मंच", "meeting": "बैठक", "nurse": "नर्स", "security": "सुरक्षा",
    "weapon": "हथियार", "event": "घटना", "ceiling": "छत", "engine": "इंजन", "board": "बोर्ड", "army": "सेना",
    "effort": "प्रयास", "east": "पूर्व", "agent": "एजेंट", "future": "भविष्य", "flight": "उड़ान", "court": "अदालत",
    "course": "कोर्स", "egg": "अंडा", "chin": "ठोड़ी", "stranger": "अजनबी", "pleasure": "खुशी", "detail": "विवरण",
    "crew": "दल", "guest": "मेहमान", "experience": "अनुभव", "joke": "मज़ाक", "sand": "रेत", "fist": "मुट्ठी",
    "action": "कार्रवाई", "walk": "सैर", "wedding": "शादी", "deal": "सौदा", "nature": "प्रकृति", "planet": "ग्रह",
    "cousin": "चचेरा भाई", "movement": "आंदोलन", "record": "रिकॉर्ड", "camp": "शिविर", "newspaper": "अखबार",
    "ray": "किरण", "human": "इंसान", "couch": "सोफा", "motion": "गति", "grandfather": "दादा", "secret": "रहस्य",
    "beauty": "सुंदरता", "presence": "उपस्थिति", "bell": "घंटी", "folk": "लोग", "button": "बटन", "list": "सूची",
    "level": "स्तर", "date": "तारीख", "subject": "विषय", "difference": "अंतर", "pause": "विराम", "van": "वैन",
    "blade": "ब्लेड", "television": "टीवी", "cover": "कवर", "past": "अतीत", "farm": "खेत", "lap": "गोद",
    "band": "बैंड", "lawyer": "वकील", "magazine": "पत्रिका", "branch": "शाखा", "frame": "फ्रेम", "deck": "डेक",
    "effect": "प्रभाव", "dance": "नृत्य", "vision": "दृष्टि", "ghost": "भूत", "character": "चरित्र", "glance": "नज़र",
    "goodbye": "अलविदा", "parking": "पार्किंग", "breakfast": "नाश्ता", "gesture": "इशारा", "luck": "किस्मत",
    "blanket": "कंबल", "gas": "गैस", "corridor": "गलियारा", "professor": "प्रोफेसर", "play": "नाटक",
    "mistake": "गलती", "university": "विश्वविद्यालय", "ocean": "समुद्र", "century": "सदी", "honey": "शहद",
    "pile": "ढेर", "bowl": "कटोरा", "base": "आधार", "fence": "बाड़", "rule": "नियम", "laughter": "हँसी",
    "anger": "गुस्सा", "sweat": "पसीना", "accident": "दुर्घटना", "weather": "मौसम", "decision": "फैसला",
    "angel": "देवदूत", "strength": "ताकत", "chicken": "मुर्गी", "study": "अध्ययन", "tape": "टेप", "wrist": "कलाई",
    "stop": "रुकना", "hip": "कूल्हा", "government": "सरकार", "belly": "पेट", "queen": "रानी", "report": "रिपोर्ट",
    "tail": "पूँछ", "plant": "पौधा", "flame": "लौ", "heaven": "स्वर्ग", "belt": "बेल्ट", "energy": "ऊर्जा",
    "green": "हरा", "quarter": "चौथाई", "enemy": "दुश्मन", "move": "चाल", "entrance": "प्रवेश", "library": "पुस्तकालय",
    "writer": "लेखक", "peace": "शांति", "touch": "स्पर्श", "pot": "बर्तन", "type": "प्रकार", "cause": "कारण",
    "rope": "रस्सी", "muscle": "मांसपेशी", "painting": "पेंटिंग", "curtain": "पर्दा", "meal": "भोजन", "act": "अधिनियम",
    "wolf": "भेड़िया", "cabin": "झोपड़ी", "charge": "शुल्क", "clock": "घड़ी", "passenger": "यात्री",
    "buddy": "दोस्त", "drug": "दवा", "use": "उपयोग", "bench": "बेंच", "traffic": "यातायात", "relief": "राहत",
    "cap": "टोपी", "pack": "पैक", "weekend": "सप्ताहांत", "stand": "स्टैंड", "elevator": "लिफ्ट",
    "birthday": "जन्मदिन", "iron": "लोहा", "meat": "मांस", "eyebrow": "भौंह", "response": "जवाब", "speed": "गति",
    "purpose": "उद्देश्य", "skirt": "स्कर्ट", "square": "वर्ग", "drive": "ड्राइव", "article": "लेख", "tower": "मीनार",
    "battle": "लड़ाई", "film": "फिल्म", "race": "दौड़", "shock": "झटका", "section": "अनुभाग", "manner": "तरीका",
    "sword": "तलवार", "stick": "छड़ी", "file": "फाइल", "bread": "रोटी", "oil": "तेल", "chain": "ज़ंजीर",
    "department": "विभाग", "project": "परियोजना", "murder": "हत्या", "bear": "भालू", "test": "टेस्ट",
    "visit": "यात्रा", "milk": "दूध", "boss": "मालिक", "elbow": "कोहनी", "desire": "इच्छा", "patient": "मरीज़",
    "price": "कीमत", "map": "नक्शा", "knowledge": "ज्ञान", "beginning": "शुरुआत", "cold": "ठंड", "closet": "अलमारी",
    "dawn": "भोर", "temple": "मंदिर", "joy": "खुशी", "duty": "कर्तव्य", "practice": "अभ्यास", "heel": "एड़ी",
    "valley": "घाटी", "fight": "लड़ाई", "wire": "तार", "jeans": "जींस", "kiss": "चुंबन", "jaw": "जबड़ा",
    "run": "दौड़", "hold": "पकड़", "relationship": "रिश्ता", "object": "वस्तु", "attack": "हमला",
    "dish": "पकवान", "highway": "हाईवे", "shade": "छाया", "crime": "अपराध", "white": "सफेद", "partner": "साथी",
    "priest": "पुजारी", "lawn": "लॉन", "laugh": "हँसी", "trunk": "तना", "cry": "रोना", "program": "कार्यक्रम",
    "ride": "सवारी", "shelf": "शेल्फ", "gentleman": "सज्जन", "being": "अस्तित्व", "steel": "इस्पात",
    "sidewalk": "फुटपाथ", "uniform": "वर्दी", "pattern": "पैटर्न", "evidence": "सबूत", "player": "खिलाड़ी",
    "novel": "उपन्यास", "pillow": "तकिया", "lamp": "दीपक", "drawer": "दराज", "danger": "खतरा",
    "detective": "जासूस", "instant": "पल", "crack": "दरार", "prayer": "प्रार्थना", "towel": "तौलिया",
    "glove": "दस्ताना", "bay": "खाड़ी", "audience": "दर्शक", "can": "डिब्बा", "condition": "हालत",
    "trail": "पगडंडी", "waist": "कमर", "pressure": "दबाव", "telephone": "टेलीफोन", "sink": "सिंक",
    "return": "वापसी", "breeze": "हवा", "taste": "स्वाद", "fault": "गलती", "stream": "धारा", "result": "परिणाम",
    "author": "लेखक", "tip": "सुझाव", "shower": "शावर", "toe": "पैर की उंगली", "season": "मौसम",
    "half": "आधा", "fool": "मूर्ख", "tunnel": "सुरंग", "client": "ग्राहक", "garage": "गैरेज", "mission": "मिशन",
    "chief": "मुखिया", "bullet": "गोली", "market": "बाजार", "loss": "नुकसान", "series": "श्रृंखला",
    "pen": "कलम", "term": "शब्द", "poem": "कविता", "prince": "राजकुमार", "clay": "मिट्टी", "lock": "ताला",
    "reality": "वास्तविकता", "snake": "साँप", "apple": "सेब", "mask": "मास्क", "birth": "जन्म",
    "break": "विराम", "wonder": "आश्चर्य", "sunlight": "धूप", "tank": "टैंक", "staff": "कर्मचारी",
    "lie": "झूठ", "faith": "विश्वास", "honor": "सम्मान", "cream": "क्रीम", "victim": "पीड़ित",
    "possibility": "संभावना", "contact": "संपर्क", "mood": "मूड", "thumb": "अंगूठा", "fun": "मज़ा",
    "candle": "मोमबत्ती", "cave": "गुफा", "post": "पोस्ट", "prison": "जेल", "emotion": "भावना",
    "leader": "नेता", "degree": "डिग्री", "feature": "विशेषता", "ticket": "टिकट", "alien": "एलियन",
    "lesson": "पाठ", "desert": "रेगिस्तान", "cut": "कट", "warning": "चेतावनी", "tale": "कहानी",
    "funeral": "अंतिम संस्कार", "cab": "टैक्सी", "reporter": "रिपोर्टर", "present": "उपहार", "theater": "थिएटर",
    "length": "लंबाई", "mud": "कीचड़", "science": "विज्ञान", "drop": "बूंद", "string": "स्ट्रिंग",
    "speech": "भाषण", "copy": "कॉपी", "cow": "गाय", "worker": "कर्मचारी", "thigh": "जांघ", "lab": "लैब",
    "roll": "रोल", "fruit": "फल", "silk": "रेशम", "brick": "ईंट", "rifle": "राइफल", "career": "करियर",
    "issue": "मुद्दा", "opportunity": "अवसर", "director": "निर्देशक", "monster": "राक्षस", "vehicle": "वाहन",
    "alley": "गली", "sleeve": "आस्तीन", "grave": "कब्र", "bush": "झाड़ी", "opening": "उद्घाटन",
    "twin": "जुड़वाँ", "barn": "खलिहान", "pound": "पाउंड", "site": "साइट", "flash": "फ्लैश",
    "judge": "न्यायाधीश", "mass": "द्रव्यमान", "process": "प्रक्रिया", "tie": "टाई", "purse": "पर्स",
    "pipe": "पाइप", "dragon": "ड्रैगन", "horizon": "क्षितिज", "tray": "ट्रे", "envelope": "लिफाफा",
    "check": "चेक", "adult": "वयस्क", "emergency": "आपातकाल", "material": "सामग्री", "childhood": "बचपन",
    "habit": "आदत", "artist": "कलाकार", "address": "पता", "scent": "खुशबू", "universe": "ब्रह्मांड",
    "shell": "खोल", "community": "समुदाय", "start": "शुरुआत", "wound": "घाव", "mouse": "चूहा",
    "pilot": "पायलट", "grade": "ग्रेड", "video": "वीडियो", "basket": "टोकरी", "wagon": "वैगन",
    "attempt": "प्रयास", "sofa": "सोफा", "cake": "केक", "fellow": "साथी", "affair": "मामला",
    "shore": "किनारा", "general": "जनरल", "root": "जड़", "robe": "लबादा", "concern": "चिंता",
    "press": "प्रेस", "rat": "चूहा", "society": "समाज", "style": "शैली", "county": "काउंटी",
    "command": "आदेश", "visitor": "विजिटर", "model": "मॉडल", "chamber": "कक्ष", "beast": "जानवर",
    "bunch": "गुच्छा", "background": "पृष्ठभूमि", "unit": "इकाई", "furniture": "फर्नीचर", "nail": "नाखून",
    "scream": "चीख", "property": "संपत्ति", "equipment": "सामान", "grip": "पकड़", "tube": "ट्यूब",
    "ash": "राख", "fan": "पंखा", "opinion": "राय", "data": "डेटा", "connection": "कनेक्शन",
    "trick": "चाल", "mystery": "रहस्य", "period": "अवधि", "writing": "लिखना", "horror": "डर",
    "candy": "कैंडी", "health": "स्वास्थ्य", "manager": "मैनेजर", "safety": "सुरक्षा", "height": "ऊंचाई",
    "appearance": "उपस्थिति", "sigh": "आह", "mine": "खान", "cloth": "कपड़ा", "reaction": "प्रतिक्रिया",
    "source": "स्रोत", "self": "स्व", "pistol": "पिस्तौल", "airport": "हवाई अड्डा", "hero": "नायक",
    "promise": "वादा", "bow": "धनुष", "tent": "तंबू", "booth": "बूथ", "cash": "नकद", "avenue": "मार्ग",
    "carpet": "कार्पेट", "basement": "तहखाना", "girlfriend": "प्रेमिका", "beard": "दाढ़ी", "brow": "भौंह",
    "display": "डिस्प्ले", "signal": "संकेत", "servant": "नौकर", "whisper": "फुसफुसाहट", "doubt": "संदेह",
    "account": "खाता", "magic": "जादू", "skull": "खोपड़ी", "sentence": "वाक्य", "collar": "कॉलर",
    "horn": "सींग", "oak": "बलूत", "ankle": "टखना", "doll": "गुड़िया", "justice": "न्याय", "pride": "गर्व",
    "youth": "युवा", "secretary": "सचिव", "research": "अनुसंधान", "sport": "खेल", "task": "काम",
    "grant": "अनुदान", "sheriff": "शेरिफ", "midnight": "आधी रात", "chip": "चिप", "theory": "सिद्धांत",
    "alarm": "अलार्म", "collection": "संग्रह", "cross": "क्रॉस", "pine": "पाइन", "generation": "पीढ़ी",
    "authority": "अधिकार", "papa": "पापा", "journey": "यात्रा", "pearl": "मोती", "toilet": "टॉयलेट",
    "killer": "हत्यारा", "tool": "उपकरण", "medicine": "दवा", "sugar": "चीनी", "princess": "राजकुमारी",
    "argument": "तर्क", "cliff": "चट्टान", "cart": "गाड़ी", "crystal": "क्रिस्टल", "bean": "बीन",
    "cage": "पिंजरा", "chocolate": "चॉकलेट", "coast": "तट", "decade": "दशक", "meaning": "अर्थ",
    "gear": "गियर", "suitcase": "सूटकेस",     "operation": "ऑपरेशन", "breathing": "साँस लेना", "role": "भूमिका",
    "metaphor": "रूपक", "expression": "अभिव्यक्ति", "living": "रहन-सहन",
    "direction": "दिशा", "attention": "ध्यान", "middle": "बीच", "answer": "जवाब",
    "stuff": "सामान", "control": "नियंत्रण", "darkness": "अंधेरा", "others": "दूसरे",
    "trouble": "मुसीबत", "sort": "किस्म", "one": "एक", "will": "इच्छा", "rest": "आराम",
    "hell": "नरक", "thanks": "धन्यवाद", "miss": "मिस", "dad": "पिता", "mom": "माँ",
    # Extra batch for missing Hindi (common nouns)
    "ability": "क्षमता", "absence": "अनुपस्थिति", "abuse": "दुरुपयोग", "academy": "अकादमी",
    "accent": "उच्चारण", "access": "पहुंच", "accusation": "आरोप", "ace": "इक्का", "ache": "दर्द",
    "acid": "अम्ल", "acquaintance": "परिचित", "activity": "गतिविधि", "actor": "अभिनेता",
    "actress": "अभिनेत्री", "ad": "विज्ञापन", "administration": "प्रशासन", "admiral": "एडमिरल",
    "admiration": "प्रशंसा", "admission": "प्रवेश", "advance": "अग्रिम", "advantage": "फायदा",
    "adventure": "साहसिक", "advice": "सलाह", "affection": "स्नेह", "affiliation": "संबद्धता",
    "agency": "एजेंसी", "agony": "पीड़ा", "agreement": "समझौता", "aid": "सहायता",
    "aide": "सहायक", "aim": "लक्ष्य", "aircraft": "विमान", "airplane": "हवाई जहाज",
    "aisle": "गलियारा", "album": "एल्बम", "alcohol": "शराब", "ally": "सहयोगी",
    "altar": "वेदी", "alternative": "विकल्प", "aluminum": "एल्युमिनियम", "amazement": "हैरानी",
    "ambassador": "राजदूत", "amber": "अंबर", "ambition": "महत्वाकांक्षा", "ambulance": "एम्बुलेंस",
    "american": "अमेरिकन", "amount": "राशि", "amusement": "मनोरंजन", "analysis": "विश्लेषण",
    "ancestor": "पूर्वज", "anchor": "लंगर", "anguish": "व्यथा", "anniversary": "वर्षगांठ",
    "announcement": "घोषणा", "announcer": "उद्घोषक", "annoyance": "नाराज़गी", "ant": "चींटी",
    "antenna": "एंटीना", "anticipation": "प्रत्याशा", "anxiety": "चिंता", "ape": "वानर",
    "apology": "माफी", "appeal": "अपील", "appetite": "भूख", "applause": "तालियां",
    "application": "आवेदन", "appointment": "नियुक्ति", "approach": "दृष्टिकोण", "approval": "स्वीकृति",
    "apron": "एप्रन", "arc": "चाप", "arch": "मेहराब", "archer": "धनुर्धर", "armchair": "कुर्सी",
    "armor": "कवच", "aroma": "खुशबू", "arrangement": "व्यवस्था", "array": "सरणी",
    "arrest": "गिरफ्तारी", "arrival": "आगमन", "arrow": "तीर", "artifact": "कलाकृति",
    "ashtray": "राखदानी", "aspect": "पहलू", "asphalt": "डामर", "assassin": "हत्यारा",
    "assault": "हमला", "assembly": "सभा", "asshole": "गधा", "assignment": "असाइनमेंट",
    "assistance": "सहायता", "assistant": "सहायक", "associate": "सहयोगी", "association": "संघ",
    "asteroid": "क्षुद्रग्रह", "astonishment": "आश्चर्य", "astronaut": "अंतरिक्ष यात्री",
    "atmosphere": "माहौल", "attendant": "परिचारक", "attic": "अटारी", "attitude": "रवैया",
    "attorney": "वकील", "attraction": "आकर्षण", "auditorium": "सभागार", "autumn": "पतझड़",
    "award": "पुरस्कार", "awareness": "जागरूकता", "awe": "विस्मय", "axe": "कुल्हाड़ी",
    "babe": "बच्चा", "backpack": "बैग", "backseat": "पिछली सीट", "backup": "बैकअप",
    "bacon": "बेकन", "badge": "बैज", "baker": "बेकर", "bakery": "बेकरी", "balance": "संतुलन",
    "balcony": "बालकनी", "balloon": "गुब्बारा", "banana": "केला", "bandage": "पट्टी",
    "bang": "धमाका", "banner": "बैनर", "barber": "नाई", "bargain": "सौदा", "bark": "छाल",
    "baron": "बैरन", "barrel": "पीपा", "barrier": "बाधा", "bartender": "बारटेंडर",
    "baseball": "बेसबॉल", "basin": "बेसिन", "basis": "आधार", "basketball": "बास्केटबॉल",
    "bat": "चमगादड़", "bath": "स्नान", "bathrobe": "बाथरोब", "battery": "बैटरी",
    "bead": "मनका", "beak": "चोंच", "beam": "किरण", "beating": "पिटाई", "beau": "प्रेमी",
    "bedside": "बिस्तर के पास", "bee": "मधुमक्खी", "beef": "गोमांस", "beetle": "भृंग",
    "behavior": "व्यवहार", "belief": "विश्वास", "belle": "सुंदरी", "belongings": "सामान",
    "bend": "मोड़", "benefit": "लाभ", "berry": "बेरी", "bet": "दांव", "betrayal": "विश्वासघात",
    "bible": "बाइबल", "bicycle": "साइकिल", "bike": "बाइक", "binoculars": "दूरबीन",
    "birch": "सन्टी", "biscuit": "बिस्कुट", "bishop": "बिशप", "bite": "काटना",
    "black": "काला", "blackness": "कालापन", "blast": "विस्फोट", "blessing": "आशीर्वाद",
    "blind": "अंधा", "bloom": "खिलना", "blossom": "फूल", "blouse": "ब्लाउज",
    "blow": "घूंसा", "blue": "नीला", "bluff": "ब्लफ", "blur": "धुंधलापन",
    "bodyguard": "अंगरक्षक", "bolt": "बोल्ट", "bomb": "बम", "bond": "बंधन",
    "bookstore": "किताबों की दुकान", "boom": "उछाल", "border": "सीमा", "bosom": "छाती",
    "boulder": "शिलाखंड", "boulevard": "बुलेवार्ड", "boundary": "सीमा", "bouquet": "गुलदस्ता",
    "bout": "मुकाबला", "boxer": "बॉक्सर", "boyfriend": "प्रेमी", "bra": "ब्रा",
    "bracelet": "कंगन", "braid": "चोटी", "brake": "ब्रेक", "brand": "ब्रांड",
    "brandy": "ब्रांडी", "brass": "पीतल", "briefcase": "ब्रीफकेस", "bronze": "कांस्य",
    "broom": "झाड़ू", "brown": "भूरा", "bruise": "चोट", "brush": "ब्रश",
    "bubble": "बुलबुला", "bucket": "बाल्टी", "bud": "कली", "budget": "बजट",
    "buffalo": "भैंस", "bug": "कीट", "bulb": "बल्ब", "bulk": "थोक", "bull": "सांड",
    "bullshit": "बकवास", "bum": "आवारा", "bump": "टक्कर", "bundle": "बंडल",
    "bunk": "चारपाई", "bunny": "खरगोश", "burden": "बोझ", "bureau": "ब्यूरो",
    "burger": "बर्गर", "burial": "दफन", "burn": "जलन", "burst": "विस्फोट",
    "businessman": "व्यापारी", "butcher": "कसाई", "butler": "बटलर", "butt": "नितंब",
    "butter": "मक्खन", "butterfly": "तितली", "cabinet": "कैबिनेट", "cable": "केबल",
    "cafe": "कैफे", "cafeteria": "कैफेटेरिया", "calendar": "कैलेंडर", "calf": "बछड़ा",
    "caller": "कॉलर", "calm": "शांति", "camel": "ऊंट", "campaign": "अभियान",
    "campus": "कैंपस", "canal": "नहर", "cancer": "कैंसर", "candidate": "उम्मीदवार",
    "cane": "छड़ी", "cannon": "तोप", "canoe": "डोंगी", "canopy": "शामियाना",
    "canvas": "कैनवास", "canyon": "कैन्यन", "capacity": "क्षमता", "cape": "केप",
    "capital": "राजधानी", "cargo": "माल", "carol": "कैरल", "carpenter": "बढ़ई",
    "carriage": "गाड़ी", "carrier": "वाहक", "carrot": "गाजर", "carton": "कार्टन",
    "cartoon": "कार्टून", "casino": "कैसीनो", "cast": "कास्ट", "castle": "किला",
    "catch": "पकड़", "cathedral": "गिरजाघर", "cattle": "मवेशी", "cavern": "गुफा",
    "cedar": "देवदार", "celebration": "उत्सव", "celebrity": "सेलिब्रिटी", "cellar": "तहखाना",
    "cement": "सीमेंट", "cemetery": "कब्रिस्तान", "cereal": "अनाज", "ceremony": "समारोह",
    "certainty": "निश्चितता", "chairman": "अध्यक्ष", "challenge": "चुनौती", "champagne": "शैंपेन",
    "channel": "चैनल", "chaos": "अराजकता", "chapel": "चैपल", "chapter": "अध्याय",
    "charity": "दान", "charm": "आकर्षण", "chart": "चार्ट", "chase": "पीछा",
    "cheekbone": "गाल की हड्डी", "cheer": "जयकार", "cheese": "पनीर", "chef": "शेफ",
    "chemical": "रासायनिक", "cherry": "चेरी", "chess": "शतरंज", "chick": "चूजा",
    "chili": "मिर्च", "chill": "ठंडक", "chimney": "चिमनी", "china": "चाइना",
    "choir": "गायक मंडली", "chop": "काटना", "chopper": "हेलिकॉप्टर", "chore": "काम",
    "chorus": "कोरस", "chuck": "चक", "chuckle": "मुस्कान", "chunk": "टुकड़ा",
    "cigar": "सिगार", "circuit": "सर्किट", "circumstance": "परिस्थिति", "circus": "सर्कस",
    "civilization": "सभ्यता", "claim": "दावा", "clan": "कबीला", "clarity": "स्पष्टता",
    "classmate": "सहपाठी", "classroom": "कक्षा", "claw": "पंजा", "cleaner": "क्लीनर",
    "cleaning": "सफाई", "clearing": "सफाई", "clerk": "क्लर्क", "click": "क्लिक",
    "clinic": "क्लिनिक", "clip": "क्लिप", "cloak": "लबादा", "clothes": "कपड़े",
    "clothing": "कपड़े", "clown": "जोकर", "clue": "संकेत", "clump": "झुरमुट",
    "cluster": "समूह", "coach": "कोच", "coal": "कोयला", "cockpit": "कॉकपिट",
    "cocktail": "कॉकटेल", "code": "कोड", "coffin": "ताबूत", "coin": "सिक्का",
    "coincidence": "संयोग", "coke": "कोक", "collapse": "पतन", "colleague": "सहकर्मी",
    "collector": "संग्रहकर्ता", "colonel": "कर्नल", "colony": "कॉलोनी", "column": "स्तंभ",
    "comb": "कंघी", "combat": "युद्ध", "combination": "संयोजन", "comfort": "आराम",
    "coming": "आगमन", "commander": "कमांडर", "comment": "टिप्पणी", "commission": "कमीशन",
    "commitment": "प्रतिबद्धता", "committee": "समिति", "commotion": "हलचल",
    "communication": "संचार", "companion": "साथी", "comparison": "तुलना",
    "compartment": "डिब्बा", "compassion": "करुणा", "competition": "प्रतियोगिता",
    "complaint": "शिकायत", "complex": "परिसर", "compliment": "तारीफ", "compound": "यौगिक",
    "comrade": "साथी",
    # More missing Hindi (nouns from list)
    "lot": "ज़मीन का टुकड़ा", "desk": "डेस्क", "gun": "बंदूक", "afternoon": "दोपहर",
    "sir": "महोदय", "bar": "बार", "chest": "छाती", "matter": "मामला", "top": "शीर्ष",
    "rock": "चट्टान", "music": "संगीत", "state": "अवस्था", "pocket": "जेब", "dinner": "रात का खाना",
    "hall": "हॉल", "pain": "दर्द", "age": "उम्र", "river": "नदी", "chance": "मौका", "crowd": "भीड़",
    "stone": "पत्थर", "coffee": "कॉफ़ी", "ship": "जहाज़",
    "ice": "बर्फ", "snow": "बर्फ", "note": "नोट", "mirror": "आईना", "king": "राजा", "fear": "डर",
    "officer": "अधिकारी", "hole": "छेद", "shot": "गोली", "guard": "पहरेदार", "conversation": "बातचीत",
    "boat": "नाव", "system": "सिस्टम", "care": "देखभाल", "bit": "बिट", "movie": "फिल्म",
    "bone": "हड्डी", "page": "पृष्ठ", "captain": "कप्तान", "aunt": "चाची", "darkness": "अंधेरा",
    "control": "नियंत्रण", "drink": "पेय", "hotel": "होटल", "coat": "कोट", "stair": "सीढ़ी",
    "order": "आदेश", "rose": "गुलाब", "hat": "टोपी", "gold": "सोना", "cigarette": "सिगरेट",
    "cloud": "बादल", "view": "नज़ारा", "driver": "चालक", "cup": "कप", "figure": "आकृति",
    "expression": "अभिव्यक्ति", "path": "रास्ता", "key": "चाबी", "computer": "कंप्यूटर",
    "flower": "फूल", "ring": "अंगूठी", "bathroom": "बाथरूम", "metal": "धातु", "moon": "चाँद",
    "song": "गाना", "soldier": "सैनिक", "radio": "रेडियो", "history": "इतिहास", "wave": "लहर",
    "plan": "योजना", "college": "कॉलेज", "fish": "मछली", "garden": "बगीचा", "train": "ट्रेन",
    "shop": "दुकान", "cop": "पुलिस", "art": "कला", "beer": "बियर", "north": "उत्तर",
    "island": "द्वीप", "bus": "बस", "smell": "गंध", "noise": "शोर", "mama": "माँ",
    "park": "पार्क", "south": "दक्षिण", "pair": "जोड़ी", "lord": "भगवान", "plate": "प्लेट",
    "jacket": "जैकेट", "help": "मदद", "daddy": "पापा", "grass": "घास", "thanks": "धन्यवाद",
    "heat": "गर्मी", "sleep": "नींद", "brain": "दिमाग", "service": "सेवा", "trip": "यात्रा",
    "beat": "धड़कन", "knife": "चाकू", "spot": "धब्बा", "message": "संदेश", "mark": "निशान",
    "teacher": "शिक्षक", "gaze": "नज़र", "village": "गाँव", "winter": "सर्दी", "front": "सामने",
    "surface": "सतह", "bank": "बैंक", "team": "टीम", "maximum": "अधिकतम", "position": "पद",
    "stomach": "पेट", "turn": "मोड़", "west": "पश्चिम", "lunch": "दोपहर का खाना",
    "creature": "जीव", "soul": "आत्मा", "leaf": "पत्ता", "show": "शो", "gate": "दरवाज़ा",
    "palm": "हथेली", "plastic": "प्लास्टिक", "storm": "तूफान", "doorway": "द्वार",
    "counter": "काउंटर", "photo": "फोटो", "stage": "मंच", "meeting": "बैठक", "nurse": "नर्स",
    "weapon": "हथियार", "event": "घटना", "ceiling": "छत", "engine": "इंजन", "gift": "उपहार",
    "restaurant": "रेस्तराँ", "board": "बोर्ड", "hallway": "गलियारा", "army": "सेना",
    "effort": "प्रयास", "east": "पूर्व", "agent": "एजेंट", "future": "भविष्य", "pant": "पैंट",
    "leather": "चमड़ा", "flight": "उड़ान", "sex": "सेक्स", "court": "अदालत", "course": "कोर्स",
    "dirt": "गंदगी", "egg": "अंडा", "chin": "ठोड़ी", "stranger": "अजनबी", "pleasure": "खुशी",
    "detail": "विवरण", "crew": "दल", "fall": "गिरावट", "guest": "मेहमान", "experience": "अनुभव",
    "joke": "मज़ाक", "sand": "रेत", "fist": "मुट्ठी", "action": "कार्रवाई", "walk": "सैर",
    "wedding": "शादी", "deal": "सौदा", "nature": "प्रकृति", "planet": "ग्रह", "cousin": "चचेरा भाई",
    "movement": "आंदोलन", "flesh": "मांस", "record": "रिकॉर्ड", "camp": "शिविर",
    "newspaper": "अखबार", "ray": "किरण", "human": "इंसान", "couch": "सोफा", "motion": "गति",
    "grandfather": "दादा", "photograph": "फोटो", "secret": "रहस्य", "beauty": "सुंदरता",
    "presence": "उपस्थिति", "bell": "घंटी", "folk": "लोग", "button": "बटन", "list": "सूची",
    "level": "स्तर", "date": "तारीख", "subject": "विषय", "difference": "अंतर", "pause": "विराम",
    "van": "वैन", "blade": "ब्लेड", "television": "टीवी", "cover": "कवर", "past": "अतीत",
    "farm": "खेत", "lap": "गोद", "band": "बैंड", "lawyer": "वकील", "magazine": "पत्रिका",
    "branch": "शाखा", "frame": "फ्रेम", "deck": "डेक", "effect": "प्रभाव", "dance": "नृत्य",
    "vision": "दृष्टि", "ghost": "भूत", "ass": "गधा", "character": "चरित्र", "glance": "नज़र",
    "goodbye": "अलविदा", "parking": "पार्किंग", "breakfast": "नाश्ता", "gesture": "इशारा",
    "luck": "किस्मत", "blanket": "कंबल", "gas": "गैस", "corridor": "गलियारा",
    "professor": "प्रोफेसर", "play": "नाटक", "mistake": "गलती", "university": "विश्वविद्यालय",
    "ocean": "समुद्र", "century": "सदी", "honey": "शहद", "pile": "ढेर", "bowl": "कटोरा",
    "base": "आधार", "fence": "बाड़", "rule": "नियम", "laughter": "हँसी", "anger": "गुस्सा",
    "sweat": "पसीना", "accident": "दुर्घटना", "weather": "मौसम", "decision": "फैसला",
    "angel": "देवदूत", "strength": "ताकत", "chicken": "मुर्गी", "study": "अध्ययन", "tape": "टेप",
    "wrist": "कलाई", "stop": "रुकना", "hip": "कूल्हा", "government": "सरकार", "belly": "पेट",
    "queen": "रानी", "report": "रिपोर्ट", "tail": "पूँछ", "plant": "पौधा", "flame": "लौ",
    "heaven": "स्वर्ग", "belt": "बेल्ट", "neighborhood": "पड़ोस", "energy": "ऊर्जा", "green": "हरा",
    "quarter": "चौथाई", "enemy": "दुश्मन", "move": "चाल", "entrance": "प्रवेश", "library": "पुस्तकालय",
    "writer": "लेखक", "peace": "शांति", "touch": "स्पर्श", "pot": "बर्तन", "type": "प्रकार",
    "cause": "कारण", "rope": "रस्सी", "muscle": "मांसपेशी", "painting": "पेंटिंग", "curtain": "पर्दा",
    "meal": "भोजन", "act": "अधिनियम", "wolf": "भेड़िया", "cabin": "झोपड़ी", "charge": "शुल्क",
    "clock": "घड़ी", "passenger": "यात्री", "buddy": "दोस्त", "drug": "दवा", "use": "उपयोग",
    "bench": "बेंच", "traffic": "यातायात", "relief": "राहत", "cap": "टोपी", "pack": "पैक",
    "weekend": "सप्ताहांत", "stand": "स्टैंड", "elevator": "लिफ्ट", "birthday": "जन्मदिन",
    "lily": "कुमुदिनी", "iron": "लोहा", "meat": "मांस", "eyebrow": "भौंह", "response": "जवाब",
    "speed": "गति", "purpose": "उद्देश्य", "skirt": "स्कर्ट", "square": "वर्ग", "drive": "ड्राइव",
    "article": "लेख", "english": "अंग्रेज़ी", "tower": "मीनार", "battle": "लड़ाई", "film": "फिल्म",
    "race": "दौड़", "shock": "झटका", "section": "अनुभाग", "manner": "तरीका", "sword": "तलवार",
    "stick": "छड़ी", "file": "फाइल", "bread": "रोटी", "oil": "तेल", "chain": "ज़ंजीर",
    "department": "विभाग", "project": "परियोजना", "murder": "हत्या", "bear": "भालू",
    "test": "टेस्ट", "visit": "यात्रा", "milk": "दूध", "boss": "मालिक", "elbow": "कोहनी",
    "desire": "इच्छा", "patient": "मरीज़", "grin": "मुस्कान", "lover": "प्रेमी", "price": "कीमत",
    "map": "नक्खा", "knowledge": "ज्ञान", "beginning": "शुरुआत", "cold": "ठंड", "closet": "अलमारी",
    "dawn": "भोर", "temple": "मंदिर", "joy": "खुशी", "duty": "कर्तव्य", "practice": "अभ्यास",
    "heel": "एड़ी", "valley": "घाटी", "fight": "लड़ाई", "wire": "तार", "jeans": "जींस",
    "kiss": "चुंबन", "jaw": "जबड़ा", "run": "दौड़", "hold": "पकड़", "relationship": "रिश्ता",
    "object": "वस्तु", "attack": "हमला", "dish": "पकवान", "highway": "हाईवे", "shade": "छाया",
    "crime": "अपराध", "white": "सफेद", "partner": "साथी", "priest": "पुजारी", "lawn": "लॉन",
    "laugh": "हँसी", "trunk": "तना", "cry": "रोना", "program": "कार्यक्रम", "ride": "सवारी",
    "shelf": "शेल्फ", "gentleman": "सज्जन", "being": "अस्तित्व", "steel": "इस्पात",
    "sidewalk": "फुटपाथ", "uniform": "वर्दी", "pattern": "पैटर्न", "evidence": "सबूत",
    "player": "खिलाड़ी", "novel": "उपन्यास", "pillow": "तकिया", "lamp": "दीपक", "drawer": "दराज",
    "danger": "खतरा", "detective": "जासूस", "instant": "पल", "thinking": "सोच", "crack": "दरार",
    "prayer": "प्रार्थना", "towel": "तौलिया", "glove": "दस्ताना", "bay": "खाड़ी",
    "audience": "दर्शक", "can": "डिब्बा", "condition": "हालत", "trail": "पगडंडी", "waist": "कमर",
    "pressure": "दबाव", "telephone": "टेलीफोन", "sink": "सिंक", "return": "वापसी", "breeze": "हवा",
    "taste": "स्वाद", "fault": "गलती", "stream": "धारा", "result": "परिणाम", "author": "लेखक",
    "tip": "सुझाव", "shower": "शावर", "toe": "पैर की उंगली", "season": "मौसम", "half": "आधा",
    "fool": "मूर्ख", "tunnel": "सुरंग", "client": "ग्राहक", "garage": "गैरेज", "mission": "मिशन",
    "chief": "मुखिया", "bullet": "गोली", "market": "बाजार", "loss": "नुकसान", "series": "श्रृंखला",
    "pen": "कलम", "term": "शब्द", "poem": "कविता", "prince": "राजकुमार", "clay": "मिट्टी",
    "lock": "ताला", "reality": "वास्तविकता", "snake": "साँप", "apple": "सेब", "mask": "मास्क",
    "birth": "जन्म", "break": "विराम", "wonder": "आश्चर्य", "sunlight": "धूप", "tank": "टैंक",
    "staff": "कर्मचारी", "lie": "झूठ", "faith": "विश्वास", "honor": "सम्मान", "cream": "क्रीम",
    "victim": "पीड़ित", "possibility": "संभावना", "contact": "संपर्क", "mood": "मूड",
    "thumb": "अंगूठा", "fun": "मज़ा", "candle": "मोमबत्ती", "cave": "गुफा", "post": "पोस्ट",
    "prison": "जेल", "emotion": "भावना", "leader": "नेता", "degree": "डिग्री", "feature": "विशेषता",
    "ticket": "टिकट", "alien": "एलियन", "lesson": "पाठ", "desert": "रेगिस्तान", "cut": "कट",
    "warning": "चेतावनी", "tale": "कहानी", "funeral": "अंतिम संस्कार", "cab": "टैक्सी",
    "reporter": "रिपोर्टर", "present": "उपहार", "theater": "थिएटर", "length": "लंबाई", "mud": "कीचड़",
    "science": "विज्ञान", "drop": "बूंद", "string": "स्ट्रिंग", "speech": "भाषण", "copy": "कॉपी",
    "cow": "गाय", "worker": "कर्मचारी", "thigh": "जांघ", "lab": "लैब", "roll": "रोल",
    "fruit": "फल", "patch": "पैच", "silk": "रेशम", "brick": "ईंट", "rifle": "राइफल",
    "career": "करियर", "issue": "मुद्दा", "opportunity": "अवसर", "director": "निर्देशक",
    "monster": "राक्षस", "vehicle": "वाहन", "alley": "गली", "sleeve": "आस्तीन", "grave": "कब्र",
    "bush": "झाड़ी", "dining": "भोजन कक्ष", "opening": "उद्घाटन", "twin": "जुड़वाँ", "barn": "खलिहान",
    "pound": "पाउंड", "site": "साइट", "flash": "फ्लैश", "judge": "न्यायाधीश", "mass": "द्रव्यमान",
    "process": "प्रक्रिया", "tie": "टाई", "purse": "पर्स", "pipe": "पाइप", "dragon": "ड्रैगन",
    "horizon": "क्षितिज", "tray": "ट्रे", "envelope": "लिफाफा", "check": "चेक", "adult": "वयस्क",
    "emergency": "आपातकाल", "material": "सामग्री", "childhood": "बचपन", "habit": "आदत",
    "artist": "कलाकार", "address": "पता", "scent": "खुशबू", "universe": "ब्रह्मांड", "nod": "सिर हिलाना",
    "shell": "खोल", "community": "समुदाय", "start": "शुरुआत", "wound": "घाव", "mouse": "चूहा",
    "pilot": "पायलट", "grade": "ग्रेड", "video": "वीडियो", "basket": "टोकरी", "wagon": "वैगन",
    "attempt": "प्रयास", "sofa": "सोफा", "cake": "केक", "fellow": "साथी", "affair": "मामला",
    "shore": "किनारा", "general": "जनरल", "root": "जड़", "robe": "लबादा", "concern": "चिंता",
    "press": "प्रेस", "rat": "चूहा", "society": "समाज", "style": "शैली", "county": "काउंटी",
    "command": "आदेश", "visitor": "विजिटर", "model": "मॉडल", "chamber": "कक्ष", "beast": "जानवर",
    "bunch": "गुच्छा", "background": "पृष्ठभूमि", "unit": "इकाई", "furniture": "फर्नीचर",
    "nail": "नाखून", "scream": "चीख", "property": "संपत्ति", "equipment": "सामान", "grip": "पकड़",
    "tube": "ट्यूब", "ash": "राख", "fan": "पंखा", "opinion": "राय", "data": "डेटा",
    "connection": "कनेक्शन", "trick": "चाल", "mystery": "रहस्य", "period": "अवधि",
    "writing": "लिखना", "horror": "डर", "candy": "कैंडी", "health": "स्वास्थ्य", "manager": "मैनेजर",
    "safety": "सुरक्षा", "height": "ऊंचाई", "appearance": "उपस्थिति", "sigh": "आह",
    "mine": "खान", "cloth": "कपड़ा", "reaction": "प्रतिक्रिया", "source": "स्रोत", "self": "स्व",
    "pistol": "पिस्तौल", "airport": "हवाई अड्डा", "hero": "नायक", "promise": "वादा", "bow": "धनुष",
    "tent": "तंबू", "booth": "बूथ", "cash": "नकद", "avenue": "मार्ग", "carpet": "कार्पेट",
    "basement": "तहखाना", "girlfriend": "प्रेमिका", "beard": "दाढ़ी", "brow": "भौंह",
    "display": "डिस्प्ले", "signal": "संकेत", "servant": "नौकर", "whisper": "फुसफुसाहट",
    "doubt": "संदेह", "account": "खाता", "magic": "जादू", "skull": "खोपड़ी", "sentence": "वाक्य",
    "collar": "कॉलर", "horn": "सींग", "oak": "बलूत", "ankle": "टखना", "doll": "गुड़िया",
    "justice": "न्याय", "pride": "गर्व", "youth": "युवा", "secretary": "सचिव", "research": "अनुसंधान",
    "sport": "खेल", "task": "काम", "grant": "अनुदान", "sheriff": "शेरिफ", "midnight": "आधी रात",
    "chip": "चिप", "theory": "सिद्धांत", "alarm": "अलार्म", "collection": "संग्रह", "cross": "क्रॉस",
    "pine": "पाइन", "generation": "पीढ़ी", "authority": "अधिकार", "papa": "पापा", "journey": "यात्रा",
    "pearl": "मोती", "toilet": "टॉयलेट", "killer": "हत्यारा", "tool": "उपकरण", "medicine": "दवा",
    "sugar": "चीनी", "princess": "राजकुमारी", "argument": "तर्क", "cliff": "चट्टान", "cart": "गाड़ी",
    "crystal": "क्रिस्टल", "bean": "बीन", "cage": "पिंजरा", "chocolate": "चॉकलेट", "coast": "तट",
    "decade": "दशक", "meaning": "अर्थ", "gear": "गियर", "suitcase": "सूटकेस", "operation": "ऑपरेशन",
    "breathing": "साँस लेना", "role": "भूमिका", "zuhause": "घर", "lächeln": "मुस्कान",
    "grundstück": "ज़मीन", "nachmittag": "दोपहर", "abend": "शाम", "zimmer": "कमरा",
    # More null-Hindi fill (by word)
    "cheek": "गाल", "sight": "नज़र", "throat": "गला", "hospital": "अस्पताल", "camera": "कैमरा",
    "dress": "पोशाक", "card": "कार्ड", "yard": "यार्ड", "image": "छवि", "machine": "मशीन",
    "distance": "दूरी", "area": "क्षेत्र", "narrator": "वर्णनकर्ता", "customer": "ग्राहक",
    "sake": "खातिर", "reading": "पढ़ाई", "mess": "गड़बड़", "buck": "डॉलर", "driveway": "गाड़ी का रास्ता",
    "bitch": "कुतिया", "tshirt": "टी-शर्ट", "hank": "गुच्छा", "limb": "अंग", "bastard": "हरामी",
    "sandwich": "सैंडविच", "robin": "रॉबिन", "version": "संस्करण", "prisoner": "कैदी", "match": "मैच",
    "rush": "भीड़", "lane": "लेन", "pole": "खंभा", "freedom": "आज़ादी", "skill": "कौशल",
    "passion": "जुनून", "platform": "प्लेटफॉर्म", "salt": "नमक", "stack": "ढेर", "fate": "किस्मत",
    "rage": "गुस्सा", "supply": "आपूर्ति", "whale": "व्हेल", "pig": "सुअर", "rabbit": "खरगोश",
    "monitor": "मॉनिटर", "helmet": "हेलमेट", "respect": "सम्मान", "excitement": "उत्तेजना",
    "lobby": "लॉबी", "fur": "फर", "range": "सीमा", "dick": "लिंग", "reflection": "प्रतिबिंब",
    "mail": "डाक", "fly": "मक्खी", "airlock": "एयरलॉक", "bride": "दुल्हन", "buster": "बस्टर",
    "carter": "कार्टर", "citizen": "नागरिक", "concentration": "एकाग्रता", "concept": "अवधारणा",
    "concert": "संगीत कार्यक्रम", "conclusion": "निष्कर्ष", "concrete": "कंक्रीट", "condo": "कोंडो",
    "cone": "शंकु", "conference": "सम्मेलन", "confession": "इकबाल", "confidence": "आत्मविश्वास",
    "conflict": "संघर्ष", "confusion": "उलझन", "congregation": "जमाव", "congress": "कांग्रेस",
    "conscience": "अंतरात्मा", "consciousness": "चेतना", "consequence": "परिणाम",
    "consideration": "विचार", "console": "कंसोल", "construction": "निर्माण", "container": "कंटेनर",
    "contempt": "अपमान", "content": "सामग्री", "contest": "प्रतियोगिता", "context": "संदर्भ",
    "continent": "महाद्वीप", "contract": "अनुबंध", "contrast": "विरोध", "convenience": "सुविधा",
    "convention": "सम्मेलन", "conviction": "दोषसिद्धि", "cook": "बावर्ची", "cookie": "कुकी",
    "cooking": "खाना बनाना", "cooler": "कूलर", "copper": "तांबा", "copyright": "कॉपीराइट",
    "cord": "रस्सी", "core": "कोर", "corn": "मक्का", "corporation": "निगम", "corps": "कोर",
    "corpse": "लाश", "cost": "लागत", "costume": "पोशाक", "cot": "खाट", "cottage": "झोंपड़ी",
    "cotton": "कपास", "cough": "खांसी", "council": "परिषद", "counselor": "सलाहकार", "count": "गिनती",
    "countryside": "ग्रामीण इलाका", "courage": "साहस", "courtesy": "शिष्टाचार",
    "courthouse": "अदालत", "courtyard": "आंगन", "coward": "कायर", "cowboy": "काउबॉय",
    "coyote": "कोयोट", "crab": "केकड़ा", "cracker": "क्रैकर", "cradle": "पालना", "craft": "शिल्प",
    "crane": "क्रेन", "crap": "मल", "crash": "दुर्घटना", "crate": "टोकरा", "crater": "गड्ढा",
    "creation": "रचना", "credit": "क्रेडिट", "creek": "नाला", "crest": "शिखर", "crib": "पालना",
    "cricket": "क्रिकेट", "criminal": "अपराधी", "crisis": "संकट", "critic": "आलोचक", "crop": "फसल",
    "crotch": "कमर", "crow": "कौआ", "crown": "मुकुट", "cruiser": "क्रूजर", "crumb": "चूरा",
    "crush": "कुचलना", "crust": "पपड़ी", "crying": "रोना", "cube": "घन", "cubicle": "क्यूबिकल",
    "cue": "संकेत", "cuff": "कफ", "culture": "संस्कृति", "cupboard": "अलमारी", "curb": "किनारा",
    "cure": "इलाज", "curiosity": "जिज्ञासा", "curl": "लट", "current": "धारा", "curse": "शाप",
    "curve": "वक्र", "cushion": "गद्दी", "cutter": "कटर", "cycle": "चक्र", "cylinder": "सिलेंडर",
    "dagger": "खंजर", "daisy": "गुलबहार", "dam": "बांध", "damage": "नुकसान", "dancer": "नर्तक",
    "dancing": "नृत्य", "darling": "प्रिय", "dash": "डैश", "daylight": "दिन का उजाला",
    "deacon": "डीकन", "dealer": "विक्रेता", "dean": "डीन", "dear": "प्रिय", "debate": "बहस",
    "debris": "मलबा", "debt": "कर्ज", "decker": "डेकर", "deed": "कर्म", "deer": "हिरण",
    "defeat": "हार", "defense": "रक्षा", "definition": "परिभाषा", "delay": "विलंब", "delight": "खुशी",
    "delivery": "डिलीवरी", "demand": "मांग", "demon": "राक्षस", "den": "मांद", "dentist": "दंत चिकित्सक",
    "departure": "प्रस्थान", "depression": "अवसाद", "depth": "गहराई", "deputy": "उप",
    "descent": "उतराई", "description": "विवरण", "design": "डिज़ाइन", "designer": "डिज़ाइनर",
    "despair": "निराशा", "desperation": "हताशा", "dessert": "मिठाई", "destination": "गंतव्य",
    "destiny": "भाग्य", "destruction": "विनाश", "determination": "दृढ़ संकल्प",
    "development": "विकास", "device": "उपकरण", "devil": "शैतान", "dial": "डायल",
    "dialogue": "संवाद", "diamond": "हीरा", "diaper": "डायपर", "diary": "डायरी", "dice": "पासा",
    "dickens": "डिकेंस", "dictionary": "शब्दकोश", "diet": "आहार", "difficulty": "कठिनाई",
    "dig": "खुदाई", "dignity": "गरिमा", "dime": "डाइम", "dimension": "आयाम", "diner": "भोजनालय",
    "dinosaur": "डायनासोर", "disappointment": "निराशा", "disaster": "आपदा", "disbelief": "अविश्वास",
    "discipline": "अनुशासन", "discomfort": "बेचैनी", "discovery": "खोज", "discussion": "चर्चा",
    "disease": "बीमारी", "disgust": "घृणा", "disk": "डिस्क", "dismay": "निराशा",
    "distraction": "विकर्षण", "distress": "संकट",     "district": "जिला", "ditch": "खाई", "coop": "सहकारी", "con": "ठगी", "shit": "मल",
}

# Category keywords (English) - word or phrase in en triggers category
CATEGORY_KEYWORDS = {
    "Time & Calendar": [
        "time", "day", "year", "night", "moment", "morning", "hour", "minute", "week",
        "afternoon", "evening", "second", "dawn", "century", "season", "winter", "summer",
        "spring", "autumn", "fall", "midnight", "noon", "decade", "lifetime", "period",
        "childhood", "past", "future", "present", "age", "date", "birthday", "weekend",
        "holiday", "vacation", "eve", "twilight", "dusk", "sunrise", "sunset", "length",
    ],
    "People & Family": [
        "man", "woman", "people", "mother", "father", "child", "family", "guy", "kid",
        "friend", "wife", "husband", "son", "daughter", "brother", "sister", "parent",
        "baby", "uncle", "aunt", "grandmother", "grandfather", "cousin", "neighbor",
        "stranger", "person", "lady", "sir", "lord", "gentleman", "crowd", "human",
        "adult", "teenager", "teen", "fellow", "narrator", "visitor", "guest", "host",
        "couple", "pair", "others", "enemy", "partner", "companion", "buddy", "lover",
        "girlfriend", "boyfriend", "bride", "widow", "orphan", "victim", "slave",
        "servant", "maid", "butler", "nurse", "patient", "client", "customer",
        "student", "teacher", "professor", "doctor", "lawyer", "writer", "artist",
        "actor", "singer", "worker", "boss", "manager", "chief", "officer", "soldier",
        "police", "cop", "guard", "captain", "agent", "reporter", "driver", "pilot",
        "passenger", "leader", "hero", "villain", "killer", "murderer",
        "prisoner", "witness", "judge", "jury", "priest", "king", "queen",
        "prince", "princess", "president", "minister", "general", "colonel", "sheriff",
        "detective", "spy", "assassin", "cowboy", "native", "foreigner", "refugee",
        "citizen", "grandchild", "grandson", "granddaughter", "grandparent", "ancestor",
        "twin", "relative", "mom", "dad", "daddy", "mama", "mommy", "grandma", "grandpa",
        "granny", "pap", "darling", "sweetheart", "mistress", "girl", "boy", "folk",
    ],
    "Body": [
        "hand", "head", "eye", "arm", "face", "back", "voice", "body", "finger",
        "mouth", "heart", "leg", "hair", "foot", "shoulder", "blood", "breath", "lip",
        "skin", "ear", "neck", "chest", "brain", "stomach", "nose", "knee", "throat",
        "belly", "muscle", "bone", "cheek", "chin", "forehead", "tongue", "eyebrow",
        "wrist", "hip", "thumb", "toe", "fist", "palm", "breast", "tear", "sweat",
        "skull", "limb", "vein", "pulse", "spine", "jaw", "heel", "elbow", "thigh",
        "nail", "brow", "beard", "grip", "handkerchief", "scent", "smell",
        "taste", "touch", "sight", "look", "gaze", "glance", "stare",
    ],
    "Home & Furniture": [
        "room", "door", "house", "bed", "table", "wall", "floor", "window", "chair",
        "kitchen", "bedroom", "bathroom", "apartment", "hall", "stair", "ceiling",
        "hallway", "corridor", "doorway", "counter", "closet", "shelf", "drawer",
        "mirror", "lamp", "curtain", "blanket", "pillow", "couch", "sofa", "desk",
        "board", "fence", "gate", "porch", "roof", "basement", "attic", "yard",
        "garden", "garage", "barn", "cabin", "cottage", "hut", "tent", "camp",
        "furniture", "cabinet", "stove", "sink", "tub", "shower", "toilet",
        "lock", "key", "carpet", "rug", "mattress", "cushion", "cradle", "crib",
        "wardrobe", "dresser", "cupboard", "cellar", "fireplace", "chimney", "staircase",
        "stairway", "railing", "doorbell", "driveway", "sidewalk", "pavement",
    ],
    "Food & Drink": [
        "water", "food", "coffee", "tea", "beer", "wine", "drink", "meal", "dinner",
        "breakfast", "lunch", "supper", "egg", "bread", "meat", "milk", "sugar",
        "salt", "oil", "fruit", "apple", "sandwich", "cake", "soup", "cheese", "cream",
        "honey", "chocolate", "candy", "potato", "tomato", "vegetable", "salad",
        "rice", "fish", "chicken", "cow", "pig", "banana", "orange", "grape",
        "strawberry", "cherry", "peach", "lemon", "pie", "bean", "corn", "wheat",
        "flour", "butter", "bacon", "sausage", "pizza", "cookie", "cereal",
        "juice", "whiskey", "vodka", "champagne", "cocktail", "bottle", "cup",
        "glass", "plate", "bowl", "pot", "pan", "knife", "fork", "spoon", "stove",
        "refrigerator", "restaurant", "bar", "cafe", "dining",
    ],
    "Nature & Weather": [
        "light", "air", "sun", "moon", "sky", "star", "earth", "tree", "flower",
        "grass", "leaf", "wood", "stone", "rock", "fire", "wind", "rain", "snow",
        "ice", "cloud", "storm", "river", "sea", "lake", "ocean", "beach", "shore",
        "mountain", "hill", "field", "forest", "garden", "plant", "bird", "animal",
        "dog", "cat", "horse", "fish", "snake", "bear", "wolf", "mouse",
        "rabbit", "deer", "whale", "insect", "bee", "butterfly", "dragon", "creature",
        "nature", "weather", "shadow", "wave", "dust", "sand", "mud", "smoke",
        "flame", "sunlight", "moonlight", "breeze", "thunder", "lightning", "fog",
        "mist", "dawn", "dusk", "horizon", "landscape", "wilderness", "meadow",
        "swamp", "cave", "valley", "canyon", "island", "coast", "cliff", "bush",
    ],
    "Places & Buildings": [
        "place", "way", "street", "road", "city", "town", "country", "land",
        "building", "office", "school", "church", "hospital", "station", "store",
        "shop", "hotel", "bank", "prison", "court", "library", "museum", "theater",
        "park", "center", "corner", "area", "space", "site", "spot", "zone",
        "neighborhood", "village", "county", "district", "region", "territory",
        "border", "entrance", "exit", "path", "track", "trail", "alley", "avenue",
        "highway", "bridge", "tower", "castle", "palace", "temple", "cemetery",
        "graveyard", "shelter", "harbor", "port", "dock", "airport", "market",
        "square", "plaza", "mall", "stadium", "arena", "gallery", "lobby",
        "campus", "factory", "warehouse", "ranch", "farm",
    ],
    "Transport & Travel": [
        "car", "train", "bus", "ship", "boat", "plane", "truck", "bike", "flight",
        "trip", "travel", "journey", "ride", "drive", "vehicle", "taxi", "cab",
        "wagon", "van", "engine", "wheel", "tire", "passenger", "driver", "pilot",
        "captain", "crew", "ticket", "map", "luggage", "suitcase", "backpack",
        "terminal", "parking", "traffic", "accident", "crash",
    ],
    "Work & Education": [
        "work", "job", "school", "class", "student", "teacher", "professor",
        "university", "college", "lesson", "study", "book", "paper", "pen",
        "test", "exam", "grade", "degree", "course", "subject", "homework",
        "education", "knowledge", "science", "history", "art", "music", "language",
        "word", "sentence", "story", "report", "letter", "message", "note",
        "file", "list", "program", "project", "plan", "meeting", "business",
        "company", "boss", "manager", "career", "salary", "money",
        "price", "bill", "account", "payment", "tax", "insurance", "contract",
        "law", "government", "policy", "rule", "order", "document",
    ],
    "Clothes & Accessories": [
        "clothes", "shirt", "dress", "suit", "coat", "jacket", "hat", "shoe",
        "boot", "bag", "pocket", "button", "ring", "belt", "cap", "uniform",
        "glove", "towel", "handkerchief", "scarf", "sleeve", "collar", "purse",
        "wallet", "watch", "glasses", "mask", "umbrella", "jewelry", "bracelet",
        "necklace", "earring", "lipstick", "makeup", "outfit", "cloth", "fabric",
        "silk", "leather", "wool", "cotton", "pajamas", "underwear", "sandal",
        "sweater", "sweatshirt", "hood", "vest", "apron", "robe", "cloak",
    ],
    "Animals": [
        "animal", "dog", "cat", "horse", "bird", "fish", "bear", "wolf", "mouse",
        "snake", "cow", "pig", "chicken", "rabbit", "deer", "whale", "monkey",
        "lion", "tiger", "elephant", "dragon", "insect", "bee", "butterfly",
        "rat", "bat", "fox", "shark", "crab", "turtle", "frog", "spider",
        "creature", "beast", "pet", "puppy", "kitten", "calf", "lamb",
    ],
    "Abstract & Concepts": [
        "thing", "idea", "thought", "mind", "sense", "feeling", "emotion",
        "love", "life", "death", "truth", "lie", "hope", "fear", "anger",
        "joy", "pain", "peace", "war", "power", "right", "reason", "cause",
        "problem", "question", "answer", "fact", "effect", "result", "change",
        "chance", "luck", "faith", "honor", "duty", "beauty", "secret", "mystery",
        "magic", "dream", "memory", "soul", "spirit", "ghost", "fate", "destiny",
        "fortune", "sin", "evil", "good", "reality", "illusion", "imagination",
        "curiosity", "courage", "patience", "wisdom", "understanding",
        "belief", "doubt", "trust", "pride", "shame", "guilt", "mercy",
        "grace", "sympathy", "compassion", "kindness", "respect",
        "glory", "fame", "reputation", "success", "failure", "victory", "defeat",
        "freedom", "justice", "tradition", "culture", "religion", "philosophy",
        "name", "number", "part", "piece", "sort", "type", "kind", "form",
        "way", "method", "manner", "style", "character",
    ],
    "Objects & Things": [
        "thing", "stuff", "object", "piece", "part", "bit", "box", "bottle",
        "bag", "card", "key", "phone", "computer", "machine", "tool", "weapon",
        "gun", "knife", "sword", "chain", "rope", "wire", "string", "thread",
        "button", "needle", "pin", "nail", "hammer", "brush", "camera", "radio",
        "television", "screen", "lamp", "candle", "clock", "mirror", "picture",
        "image", "photo", "frame", "cover", "lock", "sign", "mark", "signal",
        "flag", "ball", "ring", "metal", "iron", "steel", "gold", "silver",
        "glass", "plastic", "wood", "stone", "paper", "ink", "paint", "color",
        "gift", "present", "toy", "game", "newspaper", "magazine", "envelope",
        "package", "basket", "bucket", "can", "jar", "tube", "pipe", "rod", "stick",
        "block", "board", "sheet", "strip", "band", "tape", "cord",
        "bullet", "bomb", "fire", "smoke", "gas", "oil",
    ],
    "Other": [],
}

def fetch_page():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")

def parse_line_by_line(text):
    """Parse format: 'N. EnglishArticle NounArticle Plural' per line or per segment (split by rank)."""
    entries = []
    seen_ranks = set()
    # Try segment split first (handles run-together "1. TimeDie ZeitDie Zeiten2. Man...")
    segment_re = re.compile(r"(\d{1,4})\.\s*((?:(?!\d{1,4}\.\s*).)+)", re.DOTALL)
    for m in segment_re.finditer(text):
        rank = int(m.group(1))
        if rank < 1 or rank > 2990:
            continue
        rest = m.group(2).strip()
        if not rest or len(rest) < 2:
            continue
        # Skip if rest doesn't look like list (must contain German article)
        if "Die" not in rest and "Der" not in rest and "Das" not in rest:
            continue
        tokens = rest.split()
        if len(tokens) < 1:
            continue
        # Format A: "Thing Die Sache Die Sachen" (space-separated)
        if len(tokens) >= 3 and tokens[1] in ("Der", "Die", "Das"):
            en = tokens[0]
            article = tokens[1].lower()
            noun = tokens[2]
            if len(tokens) >= 5 and tokens[3] in ("Der", "Die", "Das"):
                plural = tokens[4].rstrip("-") if tokens[4] != "-" else None
            elif len(tokens) >= 4:
                plural = tokens[3].rstrip("-") if tokens[3] != "-" else None
            else:
                plural = None
        else:
            # Format B: "TimeDie ZeitDie Zeiten" (concatenated)
            first = tokens[0]
            article = None
            en = first
            for art in ("Der", "Die", "Das"):
                if first.endswith(art):
                    article = art.lower()
                    en = first[:-len(art)].strip()
                    break
            if not article and len(first) > 3:
                for art in ("der", "die", "das"):
                    if first.endswith(art):
                        article = art
                        en = first[:-len(art)].strip()
                        break
            if not article:
                article = "die"
                en = first
            if len(tokens) == 1:
                single = first.rstrip("-")
                noun = single
                for art in ("Der", "Die", "Das"):
                    if single.endswith(art) and len(single) > len(art):
                        noun = single[:-len(art)]
                        break
                else:
                    if len(single) >= 4 and len(single) % 2 == 0:
                        half = len(single) // 2
                        if single[:half] == single[half:]:
                            noun = single[:half]
                        else:
                            noun = single
                    else:
                        noun = single if single else en
                plural = None
            else:
                second = tokens[1]
                noun = second.rstrip("-")
                if second.endswith("-"):
                    plural = None
                else:
                    for art in ("Der", "Die", "Das"):
                        if second.endswith(art) and len(second) > len(art):
                            noun = second[:-len(art)]
                            break
                    plural = tokens[2] if len(tokens) > 2 else None
                    if plural and (plural.endswith("-") or len(plural) > 25):
                        plural = None
        if not noun:
            continue
        seen_ranks.add(rank)
        entries.append({
            "rank": rank,
            "en": en,
            "article": article,
            "de": noun,
            "plural": plural,
            "hi": "",
        })
    return entries

def parse_with_regex(text):
    """Fallback: regex on full text."""
    entries = []
    pat = re.compile(
        r"(\d+)\.\s*"
        r"(.+?)"
        r"(Der|Die|Das)\s+"
        r"([A-Za-zÄÖÜäöüß\-]+)"
        r"\s+"
        r"((?:Der|Die|Das)\s+[A-Za-zÄÖÜäöüß\-]+|\-)",
        re.MULTILINE | re.IGNORECASE
    )
    for m in pat.finditer(text):
        rank = int(m.group(1))
        en = m.group(2).strip()
        article = m.group(3).lower()
        noun = m.group(4).strip()
        pl = m.group(5).strip()
        plural = None if pl == "-" else (pl.split()[-1] if pl else None)
        entries.append({
            "rank": rank,
            "en": en,
            "article": article,
            "de": noun,
            "plural": plural,
            "hi": "",
        })
    return entries

def fill_missing_hindi(entries, base):
    """Fill hi where empty: load cache, then optionally use googletrans and save cache."""
    import os
    import time
    cache_path = os.path.join(base, "en_hi_cache.json")
    cache = {}
    if os.path.isfile(cache_path):
        try:
            with open(cache_path, encoding="utf-8") as f:
                cache = json.load(f)
            print(f"Loaded Hindi cache: {len(cache)} entries")
        except Exception:
            pass
    need = []
    for e in entries:
        en_key = (e.get("en") or "").strip().lower()
        if not en_key or en_key == "—" or (e.get("hi") or "").strip():
            continue
        if en_key in cache:
            e["hi"] = cache[en_key]
        else:
            need.append(en_key)
    if not need:
        return
    need = list(dict.fromkeys(need))
    try:
        from googletrans import Translator
        translator = Translator()
        print(f"Translating {len(need)} missing Hindi...")
        for i, en in enumerate(need):
            if en in cache:
                continue
            try:
                r = translator.translate(en, src="en", dest="hi")
                if r and r.text:
                    cache[en] = r.text
                    for e in entries:
                        if ((e.get("en") or "").strip().lower()) == en:
                            e["hi"] = r.text
                if (i + 1) % 50 == 0:
                    print(f"  {i + 1}/{len(need)}")
                time.sleep(0.2)
            except Exception:
                time.sleep(1)
        if cache:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=0)
            print(f"Saved Hindi cache: {len(cache)} entries")
    except ImportError:
        print("Tip: install googletrans (pip install googletrans==4.0.0-rc1) to fill missing Hindi.")

def assign_category(en, de):
    en_lower = (en or "").lower().strip()
    de_lower = (de or "").lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "Other":
            continue
        for kw in keywords:
            if kw in en_lower or kw in de_lower:
                return category
    return "Other"

def main():
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    # Merge Hindi cache and extra glossary into EN_TO_HI so all translations are used
    for name, filename in [("cache", "en_hi_cache.json"), ("extra", "en_hi_extra.json")]:
        path = os.path.join(base, filename)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                for k, v in data.items():
                    if k and v and k not in EN_TO_HI:
                        EN_TO_HI[k] = v
                print(f"Merged Hindi {name}: {len(data)} entries")
            except Exception:
                pass
    print("Fetching page...")
    try:
        html = fetch_page()
    except Exception as e:
        print("Fetch failed:", e)
        html = ""
    text = re.sub(r"<[^>]+>", "\n", html)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\\\.", ".", text)
    entries = parse_line_by_line(text)
    if len(entries) < 2900:
        entries = parse_with_regex(text)
    # If fetch failed and we have no data, try loading existing JSON so we don't overwrite with placeholders
    if len(entries) < 2900:
        json_path = os.path.join(base, "2980-most-frequent-german-nouns.json")
        if os.path.isfile(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                entries = existing.get("entries") or []
                if len(entries) >= 2900:
                    print("Using existing JSON entries (fetch had failed).")
            except Exception as load_err:
                print("Could not load existing JSON:", load_err)
    # Dedupe by rank: prefer entry with plural or with German noun (de != en)
    by_rank = {}
    for e in entries:
        r = e["rank"]
        if r not in by_rank:
            by_rank[r] = e
        else:
            prev = by_rank[r]
            # Prefer entry that has plural or has distinct German noun
            better = (e.get("plural") and not prev.get("plural")) or (
                (e.get("de") or "") != (e.get("en") or "") and (prev.get("de") or "") == (prev.get("en") or "")
            )
            if better:
                by_rank[r] = e
    entries = [by_rank[r] for r in sorted(by_rank.keys())]
    # Fill missing ranks 1..2980 (source has no #354 per blog comments)
    full_list = []
    for r in range(1, TARGET + 1):
        if r in by_rank:
            full_list.append(by_rank[r])
        else:
            full_list.append({
                "rank": r,
                "en": "—",
                "article": "die",
                "de": "—",
                "plural": None,
                "hi": "",
            })
    # Re-assign rank as normal number 1..2980
    for i, e in enumerate(full_list, 1):
        e["rank"] = i
        # Hindi: from English glossary where available
        en_key = (e.get("en") or "").strip().lower()
        if en_key and en_key != "—" and en_key in EN_TO_HI:
            e["hi"] = EN_TO_HI[en_key]
    entries = full_list
    print(f"Total entries: {len(entries)}")
    # Fill missing Hindi from cache or translation
    fill_missing_hindi(entries, base)
    # Ensure no empty Hindi: fallback to English so we never write empty
    for e in entries:
        if not (e.get("hi") or "").strip() and (e.get("en") or "").strip() and (e.get("en") or "").strip() != "—":
            e["hi"] = (e.get("en") or "").strip()
        elif not (e.get("hi") or "").strip():
            e["hi"] = "—"
    # Assign categories
    by_category = defaultdict(list)
    for e in entries:
        cat = assign_category(e["en"], e.get("de"))
        by_category[cat].append(e)
    for cat in by_category:
        by_category[cat].sort(key=lambda x: x["rank"])
    sorted_cats = sorted(by_category.keys())
    # Ensure plural is never null: use DE_TO_PLURAL if known, else "—"
    for e in entries:
        if e.get("plural") is None or (e.get("plural") or "").strip() in ("", "—"):
            de = (e.get("de") or "").strip()
            e["plural"] = DE_TO_PLURAL.get(de) or "—"
    out = {
        "source": URL,
        "title": "The 2980 Most Frequently Used German Nouns (With Plural)",
        "total_entries": len(entries),
        "entries": entries,
        "categories": {cat: by_category[cat] for cat in sorted_cats},
    }
    json_path = os.path.join(base, "2980-most-frequent-german-nouns.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Wrote {json_path}")
    # Also write .js for offline loading
    js_path = os.path.join(base, "2980-most-frequent-german-nouns.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("var NOUNS_DATA = ")
        json.dump(out, f, ensure_ascii=False)
        f.write(";\n")
    print(f"Wrote {js_path}")
    print("Categories:", sorted_cats)

if __name__ == "__main__":
    main()
