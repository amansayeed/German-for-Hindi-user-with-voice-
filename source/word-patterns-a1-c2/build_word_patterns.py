# -*- coding: utf-8 -*-
"""Build word-patterns-vocabulary.json with all pattern words and Hindi meanings. No duplicates."""
import json
import os

# Load extended word list if present (for 10k+ words)
EXTENDED_DATA = {}
_base = os.path.dirname(os.path.abspath(__file__))
for _fname in ("extended_words.json", "extended_extra.json"):
    _extended_path = os.path.join(_base, _fname)
    if os.path.isfile(_extended_path):
        try:
            with open(_extended_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            for cid, arr in raw.items():
                EXTENDED_DATA.setdefault(cid, []).extend([tuple(x) for x in arr])
        except Exception:
            pass
try:
    from pattern_words_extended import EXTENDED_DATA as PWE
    for cid, arr in PWE.items():
        EXTENDED_DATA.setdefault(cid, []).extend(arr)
except ImportError:
    pass

# All words per pattern: (de, en, hi). German nouns include article.
DATA = {
    "pattern_1_ance_ence": [
        ("die Toleranz", "tolerance", "सहनशीलता"),
        ("die Akzeptanz", "acceptance", "स्वीकृति"),
        ("die Distanz", "distance", "दूरी"),
        ("die Existenz", "existence", "अस्तित्व"),
        ("die Konferenz", "conference", "सम्मेलन"),
        ("die Präsenz", "presence", "उपस्थिति"),
        ("die Absenz", "absence", "अनुपस्थिति"),
        ("die Intelligenz", "intelligence", "बुद्धिमत्ता"),
        ("die Differenz", "difference", "अंतर"),
        ("die Referenz", "reference", "संदर्भ"),
        ("die Sequenz", "sequence", "क्रम"),
        ("die Frequenz", "frequency", "आवृत्ति"),
        ("die Tendenz", "tendency", "प्रवृत्ति"),
        ("die Evidenz", "evidence", "प्रमाण"),
        ("die Residenz", "residence", "निवास"),
        ("die Konsistenz", "consistency", "स्थिरता"),
        ("die Konsequenz", "consequence", "परिणाम"),
        ("die Kompetenz", "competence", "क्षमता"),
        ("die Transparenz", "transparency", "पारदर्शिता"),
        ("die Permanenz", "permanence", "स्थायित्व"),
    ],
    "pattern_2_ism": [
        ("der Tourismus", "tourism", "पर्यटन"),
        ("der Kapitalismus", "capitalism", "पूंजीवाद"),
        ("der Sozialismus", "socialism", "समाजवाद"),
        ("der Kommunismus", "communism", "साम्यवाद"),
        ("der Realismus", "realism", "यथार्थवाद"),
        ("der Idealismus", "idealism", "आदर्शवाद"),
        ("der Nationalismus", "nationalism", "राष्ट्रवाद"),
        ("der Journalismus", "journalism", "पत्रकारिता"),
        ("der Optimismus", "optimism", "आशावाद"),
        ("der Pessimismus", "pessimism", "निराशावाद"),
        ("der Patriotismus", "patriotism", "देशभक्ति"),
        ("der Feminismus", "feminism", "नारीवाद"),
        ("der Rassismus", "racism", "नस्लवाद"),
        ("der Terrorismus", "terrorism", "आतंकवाद"),
        ("der Mechanismus", "mechanism", "तंत्र"),
        ("der Organismus", "organism", "जीव"),
        ("der Buddhismus", "Buddhism", "बौद्ध धर्म"),
        ("der Hinduismus", "Hinduism", "हिंदू धर्म"),
        ("der Protestantismus", "Protestantism", "प्रोटेस्टेंटवाद"),
        ("der Katholizismus", "Catholicism", "कैथोलिकवाद"),
    ],
    "pattern_3_sion_tion": [
        ("die Aktion", "action", "कार्रवाई"),
        ("die Nation", "nation", "राष्ट्र"),
        ("die Tradition", "tradition", "परंपरा"),
        ("die Position", "position", "स्थिति"),
        ("die Information", "information", "जानकारी"),
        ("die Situation", "situation", "स्थिति"),
        ("die Operation", "operation", "ऑपरेशन"),
        ("die Konversation", "conversation", "बातचीत"),
        ("die Konstitution", "constitution", "संविधान"),
        ("die Revolution", "revolution", "क्रांति"),
        ("die Evolution", "evolution", "विकास"),
        ("die Resolution", "resolution", "संकल्प"),
        ("die Produktion", "production", "उत्पादन"),
        ("die Reduktion", "reduction", "कमी"),
        ("die Konstruktion", "construction", "निर्माण"),
        ("die Instruktion", "instruction", "निर्देश"),
        ("die Konfusion", "confusion", "भ्रम"),
        ("die Illusion", "illusion", "भ्रम"),
        ("die Diskussion", "discussion", "चर्चा"),
        ("die Mission", "mission", "मिशन"),
        ("die Passion", "passion", "जुनून"),
        ("die Session", "session", "सत्र"),
        ("die Version", "version", "संस्करण"),
        ("die Dimension", "dimension", "आयाम"),
        ("die Pension", "pension", "पेंशन"),
        ("die Profession", "profession", "पेशा"),
        ("die Expression", "expression", "अभिव्यक्ति"),
        ("die Impression", "impression", "छाप"),
        ("die Konzession", "concession", "रियायत"),
        ("die Lektion", "lesson", "पाठ"),
    ],
    "pattern_4_ty": [
        ("die Universität", "university", "विश्वविद्यालय"),
        ("die Qualität", "quality", "गुणवत्ता"),
        ("die Quantität", "quantity", "मात्रा"),
        ("die Identität", "identity", "पहचान"),
        ("die Realität", "reality", "वास्तविकता"),
        ("die Nationalität", "nationality", "राष्ट्रीयता"),
        ("die Priorität", "priority", "प्राथमिकता"),
        ("die Kapazität", "capacity", "क्षमता"),
        ("die Aktivität", "activity", "गतिविधि"),
        ("die Kreativität", "creativity", "रचनात्मकता"),
        ("die Objektivität", "objectivity", "निष्पक्षता"),
        ("die Subjektivität", "subjectivity", "व्यक्तिपरकता"),
        ("die Stabilität", "stability", "स्थिरता"),
        ("die Mobilität", "mobility", "गतिशीलता"),
        ("die Popularität", "popularity", "लोकप्रियता"),
        ("die Formalität", "formality", "औपचारिकता"),
        ("die Neutralität", "neutrality", "तटस्थता"),
        ("die Lokalität", "locality", "स्थान"),
        ("die Moralität", "morality", "नैतिकता"),
        ("die Vitalität", "vitality", "जीवन शक्ति"),
    ],
    "pattern_5_ment": [
        ("das Dokument", "document", "दस्तावेज़"),
        ("das Instrument", "instrument", "उपकरण"),
        ("das Argument", "argument", "तर्क"),
        ("das Moment", "moment", "क्षण"),
        ("das Element", "element", "तत्व"),
        ("das Fragment", "fragment", "टुकड़ा"),
        ("das Komplement", "complement", "पूरक"),
        ("das Medikament", "medication", "दवा"),
        ("das Statement", "statement", "बयान"),
        ("das Engagement", "engagement", "सगाई/प्रतिबद्धता"),
        ("das Management", "management", "प्रबंधन"),
        ("das Department", "department", "विभाग"),
        ("das Apartment", "apartment", "अपार्टमेंट"),
        ("das Equipment", "equipment", "उपकरण"),
        ("das Kompartiment", "compartment", "डिब्बा"),
        ("das Supplement", "supplement", "पूरक"),
        ("das Experiment", "experiment", "प्रयोग"),
        ("das Parlament", "parliament", "संसद"),
        ("das Fundament", "foundation", "नींव"),
    ],
    "pattern_6_al": [
        ("das Signal", "signal", "संकेत"),
        ("das Festival", "festival", "त्योहार"),
        ("das Hospital", "hospital", "अस्पताल"),
        ("das Terminal", "terminal", "टर्मिनल"),
        ("das Original", "original", "मूल"),
        ("das Material", "material", "सामग्री"),
        ("das Potenzial", "potential", "क्षमता"),
        ("das Spezial", "special", "विशेष"),
        ("das Tutorial", "tutorial", "ट्यूटोरियल"),
        ("das Memorial", "memorial", "स्मारक"),
        ("der General", "general", "जनरल"),
        ("der Admiral", "admiral", "एडमिरल"),
        ("der Kanal", "canal", "नहर"),
        ("der Kardinal", "cardinal", "कार्डिनल"),
        ("das Journal", "journal", "जर्नल"),
        ("das Portal", "portal", "पोर्टल"),
        ("das Kapital", "capital", "पूंजी"),
        ("das Lokal", "locale", "स्थान"),
        ("der Rival", "rival", "प्रतिद्वंद्वी"),
        ("das Vokal", "vowel", "स्वर"),
    ],
    "pattern_7_ic": [
        ("romantisch", "romantic", "रोमांटिक"),
        ("dramatisch", "dramatic", "नाटकीय"),
        ("automatisch", "automatic", "स्वचालित"),
        ("demokratisch", "democratic", "लोकतांत्रिक"),
        ("energisch", "energetic", "ऊर्जावान"),
        ("historisch", "historical", "ऐतिहासिक"),
        ("klassisch", "classic", "क्लासिक"),
        ("musikalisch", "musical", "संगीतमय"),
        ("optimistisch", "optimistic", "आशावादी"),
        ("pessimistisch", "pessimistic", "निराशावादी"),
        ("realistisch", "realistic", "यथार्थवादी"),
        ("spezifisch", "specific", "विशिष्ट"),
        ("strategisch", "strategic", "रणनीतिक"),
        ("sympathisch", "sympathetic", "सहानुभूतिपूर्ण"),
        ("synthetisch", "synthetic", "सिंथेटिक"),
        ("tragisch", "tragic", "दुखद"),
        ("typisch", "typical", "विशिष्ट"),
        ("elektrisch", "electric", "बिजली का"),
        ("fantastisch", "fantastic", "शानदार"),
        ("heroisch", "heroic", "वीर"),
    ],
    "pattern_8_ive": [
        ("aktiv", "active", "सक्रिय"),
        ("passiv", "passive", "निष्क्रिय"),
        ("kreativ", "creative", "रचनात्मक"),
        ("positiv", "positive", "सकारात्मक"),
        ("negativ", "negative", "नकारात्मक"),
        ("intensiv", "intensive", "गहन"),
        ("effektiv", "effective", "प्रभावी"),
        ("attraktiv", "attractive", "आकर्षक"),
        ("impulsiv", "impulsive", "आवेगी"),
        ("instinktiv", "instinctive", "सहज"),
        ("intuitiv", "intuitive", "सहजज्ञानी"),
        ("aggressiv", "aggressive", "आक्रामक"),
        ("progressiv", "progressive", "प्रगतिशील"),
        ("produktiv", "productive", "उत्पादक"),
        ("subjektiv", "subjective", "व्यक्तिपरक"),
        ("objektiv", "objective", "वस्तुनिष्ठ"),
        ("primitiv", "primitive", "आदिम"),
        ("sensitiv", "sensitive", "संवेदनशील"),
        ("selektiv", "selective", "चयनात्मक"),
        ("sportiv", "sporty", "खेलकूद वाला"),
    ],
    "pattern_9_ous": [
        ("nervös", "nervous", "घबराया हुआ"),
        ("kurios", "curious", "जिज्ञासु"),
        ("seriös", "serious", "गंभीर"),
        ("generös", "generous", "उदार"),
        ("mysteriös", "mysterious", "रहस्यमय"),
        ("harmoniös", "harmonious", "सामंजस्यपूर्ण"),
        ("anonym", "anonymous", "गुमनाम"),
        ("gloriös", "glorious", "शानदार"),
        ("luxuriös", "luxurious", "शानदार"),
        ("nebulös", "nebulous", "अस्पष्ट"),
        ("religiös", "religious", "धार्मिक"),
        ("ambitiös", "ambitious", "महत्वाकांक्षी"),
        ("infektiös", "infectious", "संक्रामक"),
        ("suspekt", "suspicious", "संदिग्ध"),
        ("variös", "various", "विभिन्न"),
    ],
    "pattern_10_ary": [
        ("militär", "military", "सैन्य"),
        ("singular", "singular", "एकवचन"),
        ("plural", "plural", "बहुवचन"),
        ("solar", "solar", "सौर"),
        ("polar", "polar", "ध्रुवीय"),
        ("vulgar", "vulgar", "अश्लील"),
        ("molar", "molar", "दाढ़"),
        ("linear", "linear", "रैखिक"),
        ("regulär", "regular", "नियमित"),
        ("populär", "popular", "लोकप्रिय"),
        ("similar", "similar", "समान"),
        ("familär", "familiar", "परिचित"),
        ("partikulär", "particular", "विशेष"),
        ("sekulär", "secular", "धर्मनिरपेक्ष"),
        ("muskulär", "muscular", "मांसल"),
        ("tubulär", "tubular", "नलिकाकार"),
        ("angulär", "angular", "कोणीय"),
        ("granulär", "granular", "दानेदार"),
        ("molekular", "molecular", "आणविक"),
        ("spekulär", "spectacular", "शानदार"),
    ],
    "pattern_11_ant": [
        ("der Migrant", "migrant", "प्रवासी"),
        ("der Demonstrant", "demonstrator", "प्रदर्शनकारी"),
        ("der Student", "student", "छात्र"),
        ("der Assistent", "assistant", "सहायक"),
        ("der Konsument", "consumer", "उपभोक्ता"),
        ("der Produzent", "producer", "निर्माता"),
        ("der Präsident", "president", "राष्ट्रपति"),
        ("der Resident", "resident", "निवासी"),
        ("der Lieferant", "supplier", "आपूर्तिकर्ता"),
        ("der Kommandant", "commander", "कमांडर"),
        ("der Konsonant", "consonant", "व्यंजन"),
        ("der Diamant", "diamond", "हीरा"),
        ("der Elefant", "elephant", "हाथी"),
        ("der Garant", "guarantor", "गारंटर"),
        ("der Informant", "informant", "सूचनादाता"),
        ("der Mandant", "client", "मुवक्किल"),
        ("der Kontrahent", "opponent", "प्रतिद्वंद्वी"),
        ("der Laborant", "lab technician", "लैब तकनीशियन"),
        ("der Emigrant", "emigrant", "उत्प्रवासी"),
    ],
    "pattern_12_ist": [
        ("der Artist", "artist", "कलाकार"),
        ("der Journalist", "journalist", "पत्रकार"),
        ("der Tourist", "tourist", "पर्यटक"),
        ("der Pianist", "pianist", "पियानोवादक"),
        ("der Gitarrist", "guitarist", "गिटारवादक"),
        ("der Optimist", "optimist", "आशावादी"),
        ("der Pessimist", "pessimist", "निराशावादी"),
        ("der Spezialist", "specialist", "विशेषज्ञ"),
        ("der Polizist", "policeman", "पुलिसवाला"),
        ("der Terrorist", "terrorist", "आतंकवादी"),
        ("der Kommunist", "communist", "कम्युनिस्ट"),
        ("der Sozialist", "socialist", "समाजवादी"),
        ("der Kapitalist", "capitalist", "पूंजीवादी"),
        ("der Aktivist", "activist", "कार्यकर्ता"),
        ("der Masochist", "masochist", "मैसोकिस्ट"),
        ("der Stylist", "stylist", "स्टाइलिस्ट"),
        ("der Typist", "typist", "टाइपिस्ट"),
        ("der Florist", "florist", "फूलवाला"),
        ("der Satirist", "satirist", "व्यंग्यकार"),
        ("der Kolumnist", "columnist", "स्तंभकार"),
    ],
    "pattern_13_logy": [
        ("die Biologie", "biology", "जीव विज्ञान"),
        ("die Geologie", "geology", "भूविज्ञान"),
        ("die Psychologie", "psychology", "मनोविज्ञान"),
        ("die Soziologie", "sociology", "समाजशास्त्र"),
        ("die Technologie", "technology", "प्रौद्योगिकी"),
        ("die Ökologie", "ecology", "पारिस्थितिकी"),
        ("die Mythologie", "mythology", "पौराणिक कथा"),
        ("die Astrologie", "astrology", "ज्योतिष"),
        ("die Meteorologie", "meteorology", "मौसम विज्ञान"),
        ("die Chronologie", "chronology", "कालक्रम"),
        ("die Terminologie", "terminology", "शब्दावली"),
        ("die Ideologie", "ideology", "विचारधारा"),
        ("die Archäologie", "archaeology", "पुरातत्व"),
        ("die Anthropologie", "anthropology", "मानव विज्ञान"),
        ("die Pharmakologie", "pharmacology", "फार्माकोलॉजी"),
        ("die Radiologie", "radiology", "रेडियोलॉजी"),
        ("die Kardiologie", "cardiology", "हृदय विज्ञान"),
        ("die Dermatologie", "dermatology", "त्वचा विज्ञान"),
        ("die Neurologie", "neurology", "न्यूरोलॉजी"),
        ("die Zoologie", "zoology", "प्राणि विज्ञान"),
    ],
    "pattern_14_graphy": [
        ("die Fotografie", "photography", "फोटोग्राफी"),
        ("die Geografie", "geography", "भूगोल"),
        ("die Biografie", "biography", "जीवनी"),
        ("die Autobiografie", "autobiography", "आत्मकथा"),
        ("die Bibliografie", "bibliography", "ग्रंथ सूची"),
        ("die Topografie", "topography", "स्थलाकृति"),
        ("die Demografie", "demography", "जनसांख्यिकी"),
        ("die Choreografie", "choreography", "नृत्य निर्देशन"),
        ("die Kalligrafie", "calligraphy", "सुलेख"),
        ("die Orthografie", "orthography", "वर्तनी"),
        ("die Stenografie", "stenography", "आशुलिपि"),
        ("die Kartografie", "cartography", "मानचित्रण"),
        ("die Ozeanografie", "oceanography", "समुद्र विज्ञान"),
        ("die Ethnografie", "ethnography", "नृवंशविज्ञान"),
        ("die Hagiografie", "hagiography", "संत जीवनी"),
        ("die Lithografie", "lithography", "लिथोग्राफी"),
        ("die Radiografie", "radiography", "रेडियोग्राफी"),
        ("die Videografie", "videography", "वीडियोग्राफी"),
        ("die Typografie", "typography", "टाइपोग्राफी"),
        ("die Ideografie", "ideography", "विचारलिपि"),
    ],
    "pattern_15_meter": [
        ("der Thermometer", "thermometer", "थर्मामीटर"),
        ("der Kilometer", "kilometre", "किलोमीटर"),
        ("der Zentimeter", "centimetre", "सेंटीमीटर"),
        ("der Millimeter", "millimetre", "मिलीमीटर"),
        ("der Diameter", "diameter", "व्यास"),
        ("der Parameter", "parameter", "पैरामीटर"),
        ("der Barometer", "barometer", "बैरोमीटर"),
        ("der Speedometer", "speedometer", "स्पीडोमीटर"),
        ("der Odometer", "odometer", "ओडोमीटर"),
        ("der Voltmeter", "voltmeter", "वोल्टमीटर"),
        ("der Amperemeter", "ammeter", "अमीटर"),
        ("der Hygrometer", "hygrometer", "आर्द्रतामापी"),
        ("der Altimeter", "altimeter", "ऊंचाई मापक"),
        ("der Chronometer", "chronometer", "क्रोनोमीटर"),
        ("der Perimeter", "perimeter", "परिधि"),
        ("der Tachometer", "tachometer", "टैकोमीटर"),
        ("der Gasometer", "gasometer", "गैसोमीटर"),
        ("der Lactometer", "lactometer", "दूध मापक"),
    ],
    "pattern_16_scope": [
        ("das Mikroskop", "microscope", "सूक्ष्मदर्शी"),
        ("das Teleskop", "telescope", "दूरबीन"),
        ("das Stethoskop", "stethoscope", "स्टेथोस्कोप"),
        ("das Endoskop", "endoscope", "एंडोस्कोप"),
        ("das Periskop", "periscope", "पेरिस्कोप"),
        ("das Kaleidoskop", "kaleidoscope", "कैलाइडोस्कोप"),
        ("das Horoskop", "horoscope", "कुंडली"),
        ("das Gyroskop", "gyroscope", "जाइरोस्कोप"),
        ("das Spektroskop", "spectroscope", "स्पेक्ट्रोस्कोप"),
        ("das Stereoskop", "stereoscope", "स्टीरियोस्कोप"),
        ("das Arthroskop", "arthroscope", "आर्थ्रोस्कोप"),
        ("das Laparoskop", "laparoscope", "लैपरोस्कोप"),
        ("das Bronchoskop", "bronchoscope", "ब्रोंकोस्कोप"),
        ("das Kolposkop", "colposcope", "कॉलपोस्कोप"),
        ("das Otoskop", "otoscope", "कान दर्शक"),
        ("das Ophthalmoskop", "ophthalmoscope", "नेत्र दर्शक"),
        ("das Dermatoskop", "dermatoscope", "डर्माटोस्कोप"),
        ("das Fluoroskop", "fluoroscope", "फ्लोरोस्कोप"),
        ("das Radioskop", "radioscope", "रेडियोस्कोप"),
    ],
    "pattern_17_phobia": [
        ("die Phobie", "phobia", "भय"),
        ("die Arachnophobie", "arachnophobia", "मकड़ी का भय"),
        ("die Agoraphobie", "agoraphobia", "खुली जगह का भय"),
        ("die Klaustrophobie", "claustrophobia", "संकीर्ण स्थान का भय"),
        ("die Hydrophobie", "hydrophobia", "पानी का भय"),
        ("die Xenophobie", "xenophobia", "विदेशियों का भय"),
        ("die Homophobie", "homophobia", "समलैंगिकता का भय"),
        ("die Nyktophobie", "nyctophobia", "अंधेरे का भय"),
        ("die Akrophobie", "acrophobia", "ऊंचाई का भय"),
        ("die Soziophobie", "sociophobia", "सामाजिक भय"),
        ("die Technophobie", "technophobia", "तकनीक का भय"),
        ("die Dentophobie", "dentophobia", "दांत का भय"),
        ("die Aviophobie", "aviophobia", "उड़ान का भय"),
        ("die Trypanophobie", "trypanophobia", "इंजेक्शन का भय"),
        ("die Emetophobie", "emetophobia", "उल्टी का भय"),
    ],
    "pattern_18_phile": [
        ("der Bibliophil", "bibliophile", "पुस्तक प्रेमी"),
        ("der Anglophil", "anglophile", "अंग्रेजी प्रेमी"),
        ("der Technophil", "technophile", "तकनीक प्रेमी"),
        ("der Audiophil", "audiophile", "ध्वनि प्रेमी"),
        ("der Francophil", "francophile", "फ्रांस प्रेमी"),
        ("der Germanophil", "germanophile", "जर्मन प्रेमी"),
        ("der Sinophil", "sinophile", "चीन प्रेमी"),
        ("der Japanophil", "japanophile", "जापान प्रेमी"),
        ("der Russophil", "russophile", "रूस प्रेमी"),
        ("der Indophil", "indophile", "भारत प्रेमी"),
    ],
    "pattern_19_age": [
        ("die Garage", "garage", "गैरेज"),
        ("die Passage", "passage", "मार्ग"),
        ("die Etage", "floor", "मंजिल"),
        ("die Reportage", "report", "रिपोर्ट"),
        ("die Montage", "assembly", "असेंबली"),
        ("die Collage", "collage", "कोलाज"),
        ("die Persiflage", "parody", "पैरोडी"),
        ("die Sabotage", "sabotage", "तोड़फोड़"),
        ("die Bandage", "bandage", "पट्टी"),
        ("die Courage", "courage", "साहस"),
        ("die Blamage", "embarrassment", "शर्मिंदगी"),
        ("die Gage", "fee", "शुल्क"),
        ("die Spionage", "espionage", "जासूसी"),
        ("die Massage", "massage", "मालिश"),
        ("die Marge", "margin", "मार्जिन"),
        ("die Triage", "triage", "ट्रायज"),
        ("die Menage", "household", "घर"),
        ("die Rage", "rage", "क्रोध"),
        ("die Image", "image", "छवि"),
        ("die Visage", "visage", "चेहरा"),
    ],
    "pattern_20_ure": [
        ("die Kultur", "culture", "संस्कृति"),
        ("die Natur", "nature", "प्रकृति"),
        ("die Temperatur", "temperature", "तापमान"),
        ("die Struktur", "structure", "संरचना"),
        ("die Literatur", "literature", "साहित्य"),
        ("die Architektur", "architecture", "वास्तुकला"),
        ("die Konstruktur", "construction", "निर्माण"),
        ("die Fraktur", "fracture", "फ्रैक्चर"),
        ("die Prozedur", "procedure", "प्रक्रिया"),
        ("die Zensur", "censorship", "सेंसरशिप"),
        ("die Diktatur", "dictatorship", "तानाशाही"),
        ("die Karikatur", "caricature", "कैरिकेचर"),
        ("die Tastatur", "keyboard", "कीबोर्ड"),
        ("die Agrikultur", "agriculture", "कृषि"),
        ("die Skulptur", "sculpture", "मूर्ति"),
        ("die Figur", "figure", "आकृति"),
        ("die Armatur", "armature", "आर्मेचर"),
        ("die Nomenklatur", "nomenclature", "नामकरण"),
        ("die Registratur", "registry", "रजिस्ट्री"),
        ("die Kur", "cure", "उपचार"),
    ],
    "pattern_21_ary_arie": [
        ("die Diktionarie", "dictionary", "शब्दकोश"),
        ("die Sekretarie", "secretary", "सचिव"),
        ("die Glossarie", "glossary", "शब्दावली"),
        ("die Notarie", "notary", "नोटरी"),
        ("die Kommentarie", "commentary", "टिप्पणी"),
        ("die Vokabularie", "vocabulary", "शब्दावली"),
        ("die Ordinarie", "ordinary", "साधारण"),
        ("die Temporarie", "temporary", "अस्थायी"),
        ("die Primarie", "primary", "प्राथमिक"),
        ("die Sekundarie", "secondary", "माध्यमिक"),
    ],
    "pattern_22_ate": [
        ("der Kandidat", "candidate", "उम्मीदवार"),
        ("der Demokrat", "democrat", "लोकतंत्रवादी"),
        ("der Diplomat", "diplomat", "राजनयिक"),
        ("der Automat", "automaton", "स्वचालित"),
        ("der Pirat", "pirate", "समुद्री डाकू"),
        ("der Soldat", "soldier", "सैनिक"),
        ("der Pilot", "pilot", "पायलट"),
        ("der Idiot", "idiot", "मूर्ख"),
        ("der Patriot", "patriot", "देशभक्त"),
        ("der Aristokrat", "aristocrat", "अभिजात"),
        ("der Bürokrat", "bureaucrat", "नौकरशाह"),
        ("der Technokrat", "technocrat", "तकनीकी विशेषज्ञ"),
        ("der Adressat", "addressee", "प्राप्तकर्ता"),
        ("das Emirat", "emirate", "अमीरात"),
        ("das Plakat", "poster", "पोस्टर"),
        ("das Format", "format", "प्रारूप"),
        ("das Resultat", "result", "परिणाम"),
        ("das Statut", "statute", "कानून"),
        ("das Zertifikat", "certificate", "प्रमाणपत्र"),
    ],
}

# Merge extended data (for A1–C1 trainer with 10,000 pattern words)
for cid, extra_list in EXTENDED_DATA.items():
    DATA.setdefault(cid, []).extend(extra_list)

def dedupe_words(words_list):
    """Remove duplicate (de, en, hi) entries. Keep first occurrence."""
    seen = set()
    out = []
    for de, en, hi in words_list:
        key = (de.strip().lower(), en.strip().lower())
        if key in seen:
            continue
        seen.add(key)
        out.append((de, en, hi))
    return out

def article_sort_key(de_str):
    """Sort order: der (0), die (1), das (2), no article (3); then by de string."""
    s = de_str.strip()
    lower = s.lower()
    if lower.startswith("der "):
        return (0, s)
    if lower.startswith("die "):
        return (1, s)
    if lower.startswith("das "):
        return (2, s)
    return (3, s)

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base, "word-patterns-vocabulary.json")

    with open(json_path, "r", encoding="utf-8") as f:
        obj = json.load(f)

    total = 0
    all_de = set()

    for cat in obj["categories"]:
        cid = cat["id"]
        if cid not in DATA:
            continue
        raw = DATA[cid]
        deduped = dedupe_words(raw)
        # Global duplicate check: no German word (normalized) appears twice in file
        words = []
        for de, en, hi in deduped:
            de_norm = de.strip().lower()
            if de_norm in all_de:
                continue
            all_de.add(de_norm)
            words.append({
                "de": de,
                "pronunciation": "",
                "hi": hi,
                "en": en,
            })
        # Sort: der, then die, then das, then no article
        words.sort(key=lambda w: article_sort_key(w["de"]))
        cat["words"] = words
        total += len(words)

    obj["totalWords"] = total
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

    print(f"Written {total} words to {json_path}")

if __name__ == "__main__":
    main()
