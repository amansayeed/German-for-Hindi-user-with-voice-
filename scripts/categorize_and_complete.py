# -*- coding: utf-8 -*-
"""
Categorize and complete A2 vocabulary: assign every word to one category,
replace all placeholders with real English/Hindi. No blanks allowed.
"""
import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
IN_CSV = BASE / "output" / "german_a2_vocabulary.csv"
OUT_CSV = BASE / "output" / "german_a2_categorized_complete.csv"
OUT_REPORT = BASE / "output" / "categorization_report.txt"

# Category list (exactly as specified)
CATEGORIES = [
    "👋 Greetings & Basics",
    "🎨 Colors",
    "👨‍👩‍👧 Family & People",
    "🧍 Body Parts",
    "🏥 Health & Feelings",
    "🍎 Food",
    "🥤 Drinks",
    "🏠 House & Furniture",
    "🍽️ Kitchen Items",
    "👕 Clothing",
    "🚗 Transport & Travel",
    "🏙️ Places & City",
    "🌳 Nature & Weather",
    "⏰ Time",
    "📚 School & Learning",
    "💼 Work & Job",
    "🛒 Shopping & Money",
    "📱 Communication",
    "🐾 Animals",
    "🎉 Celebrations",
    "🎒 Personal Items",
    "❓ Question Words",
    "👤 Pronouns",
    "🏃 Verbs",
    "✨ Adjectives",
    "🔗 Adverbs & Connectors",
]

# Built-in translations for words that had placeholders (A2 vocabulary)
BUILTIN_TRANSLATIONS = {
    "(ab)fahren": ("to depart (by vehicle)", "रवाना होना (गाड़ी से)"),
    "(ab)fliegen": ("to take off (plane)", "उड़ान भरना"),
    "(an-)/(aus)ziehen": ("to put on / take off (clothes)", "पहनना / उतारना"),
    "(an/aus)gezogen": ("put on / taken off", "पहना/उतारा"),
    "(aus)tauschen": ("to exchange", "अदला-बदली करना"),
    "abgeben": ("to hand in", "जमा करना"),
    "abholen": ("to pick up", "लेने आना"),
    "abschließen": ("to complete; to lock", "पूरा करना; ताला लगाना"),
    "Achtung (Sg.)": ("attention", "ध्यान"),
    "aktiv": ("active", "सक्रिय"),
    "aktuell": ("current", "वर्तमान"),
    "all-": ("all (prefix)", "सभी"),
    "allein": ("alone", "अकेला"),
    "als": ("as; when", "जैसा; जब"),
    "am besten": ("best", "सबसे अच्छा"),
    "am liebsten": ("most preferably", "सबसे पसंद"),
    "an sein / aus sein": ("to be on / off", "चालू/बंद होना"),
    "anbieten": ("to offer", "पेशकश करना"),
    "ander-": ("other (prefix)", "दूसरा"),
    "anfangen": ("to begin", "शुरू करना"),
    "anmachen": ("to turn on", "चालू करना"),
    "anmelden (sich)": ("to register", "पंजीकरण करना"),
    "ansehen": ("to look at", "देखना"),
    "arbeiten": ("to work", "काम करना"),
    "arbeitslos": ("unemployed", "बेरोजगार"),
    "auf jeden/": ("in any case", "किसी भी हाल में"),
    "auf sein": ("to be on", "चालू होना"),
    "aufmachen": ("to open", "खोलना"),
    "aufpassen": ("to pay attention", "ध्यान देना"),
    "aufregend": ("exciting", "रोमांचक"),
    "ausgehen": ("to go out", "बाहर जाना"),
    "ausmachen": ("to turn off; to agree", "बंद करना; तय करना"),
    "ausruhen (sich)": ("to rest", "आराम करना"),
    "aussprechen": ("to pronounce", "उच्चारण करना"),
    "aussteigen": ("to get off", "उतरना"),
    "austragen": ("to deliver", "वितरण करना"),
    "automatisch": ("automatic", "स्वचालित"),
    "außer": ("except", "सिवाय"),
    "außerdem": ("besides", "इसके अलावा"),
    "außerhalb": ("outside", "बाहर"),
    "baden": ("to bathe", "नहाना"),
    "bauen": ("to build", "बनाना"),
    "beantworten": ("to answer", "जवाब देना"),
    "bedanken (sich)": ("to thank", "धन्यवाद देना"),
    "bedeuten": ("to mean", "मतलब होना"),
    "bei": ("at; with", "पर; के पास"),
    "beide": ("both", "दोनों"),
    "bekannt": ("well-known", "प्रसिद्ध"),
    "bekommt": ("gets; receives", "मिलता है"),
    "beliebt": ("popular", "लोकप्रिय"),
    "benutzen": ("to use", "इस्तेमाल करना"),
    "bequem": ("comfortable", "आरामदायक"),
    "beraten": ("to advise", "सलाह देना"),
    "berichten": ("to report", "रिपोर्ट करना"),
    "Berlin": ("Berlin", "बर्लिन"),
    "berühmt": ("famous", "प्रसिद्ध"),
    "beschreiben": ("to describe", "वर्णन करना"),
    "besichtigen": ("to visit (sight)", "देखने जाना"),
    "besteht": ("consists", "बना होता है"),
    "bestellen": ("to order", "ऑर्डर करना"),
    "bestätigen": ("to confirm", "पुष्टि करना"),
    "besuchen": ("to visit", "मिलने जाना"),
    "bewerben (sich)": ("to apply", "आवेदन करना"),
    "billig": ("cheap", "सस्ता"),
    "bisschen": ("a bit", "थोड़ा"),
    "bitten": ("to ask (for)", "विनती करना"),
    "bleiben": ("to stay", "रुकना"),
    "blond": ("blonde", "गोरी/गोरे बाल"),
    "blöd": ("stupid", "बेवकूफ"),
    "braucht": ("needs", "जरूरत होती है"),
    "bringt": ("brings", "लाता है"),
    "brät": ("fries; roasts", "तलता/भूनता है"),
    "buchstabieren": ("to spell", "वर्तनी बोलना"),
    "chatten": ("to chat", "चैट करना"),
    "danken": ("to thank", "धन्यवाद देना"),
    "deutlich": ("clear", "स्पष्ट"),
    "die (E-)Mail": ("the email", "ईमेल"),
    "die Arbeit": ("work", "काम"),
    "die Ahnung": ("idea", "अंदाज़ा"),
    "die Butter (Sg.)": ("butter", "मक्खन"),
    "die Bäckerei": ("bakery", "बेकरी"),
    "die Bohne": ("bean", "बीन"),
    "die Cafeteria": ("canteen", "कैंटीन"),
    "die Dame": ("lady", "महिला"),
    "die Disco": ("disco", "डिस्को"),
    "die Gruppe": ("group", "समूह"),
    "die Grippe (Sg.)": ("flu", "फ्लू"),
    "die Halle": ("hall", "हॉल"),
    "die Hauptstadt": ("capital city", "राजधानी"),
    "die Heimat (Sg.)": ("homeland", "मातृभूमि"),
    "die Hilfe (Sg.)": ("help", "मदद"),
    "die Homepage": ("homepage", "होमपेज"),
    "die Jeans (Pl.)": ("jeans", "जींस"),
    "die Kleidung (Sg.)": ("clothing", "कपड़े"),
    "die Kosmetik (Sg.)": ("cosmetics", "प्रसाधन सामग्री"),
    "die Lust (Sg.)": ("desire", "इच्छा"),
    "die Lüge": ("lie", "झूठ"),
    "die Maschine": ("machine", "मशीन"),
    "die Menge": ("amount; crowd", "मात्रा; भीड़"),
    "die Messe": ("fair; mass", "मेला; मास"),
    "die Mitte": ("middle", "बीच"),
    "die Milch (Sg.)": ("milk", "दूध"),
    "die Musik (Sg.)": ("music", "संगीत"),
    "die Möbel (Pl.)": ("furniture", "फर्नीचर"),
    "die Natur (Sg.)": ("nature", "प्रकृति"),
    "die Notiz": ("note", "नोट"),
    "die Nudel": ("noodle", "नूडल"),
    "die Nummer": ("number", "नंबर"),
    "die Nähe (Sg.)": ("vicinity", "नज़दीकी"),
    "die Ordnung": ("order", "क्रम"),
    "die Papiere (Pl.)": ("papers", "कागज़ात"),
    "die Pizza": ("pizza", "पिज़्ज़ा"),
    "die Polizei (Sg.)": ("police", "पुलिस"),
    "die Post (Sg.)": ("post", "डाक"),
    "die Ruhe (Sg.)": ("quiet", "शांति"),
    "die Reihe": ("row; turn", "पंक्ति; बारी"),
    "die Seife": ("soap", "साबुन"),
    "die Seite": ("page; side", "पृष्ठ; तरफ"),
    "die Situation": ("situation", "स्थिति"),
    "die Süßigkeiten": ("sweets", "मिठाई"),
    "die Unterkunft": ("accommodation", "रुकने की जगह"),
    "die Welt": ("world", "दुनिया"),
    "die Wäsche": ("laundry", "कपड़े धोना"),
    "die Zahl": ("number", "संख्या"),
    "die Zeit": ("time", "समय"),
    "das Alter (Sg.)": ("age", "उम्र"),
    "das Ausland (Sg.)": ("abroad", "विदेश"),
    "das Auto": ("car", "कार"),
    "das Ding": ("thing", "चीज़"),
    "das E-Book": ("e-book", "ई-बुक"),
    "das Eis (Sg.)": ("ice cream", "आइसक्रीम"),
    "das Festival": ("festival", "उत्सव"),
    "das Fieber (Sg.)": ("fever", "बुखार"),
    "das Fleisch (Sg.)": ("meat", "मांस"),
    "das Frühstück (Sg.)": ("breakfast", "नाश्ता"),
    "das Gegenteil": ("opposite", "उल्टा"),
    "das Geld (Sg.)": ("money", "पैसा"),
    "das Gemüse (Sg.)": ("vegetables", "सब्ज़ियाँ"),
    "das Gepäck (Sg.)": ("luggage", "सामान"),
    "das Gerät": ("device", "उपकरण"),
    "das Geschirr (Sg.)": ("dishes", "बर्तन"),
    "das Gleis": ("platform; track", "प्लेटफॉर्म"),
    "das Glück (Sg.)": ("luck", "किस्मत"),
    "das Interesse": ("interest", "रुचि"),
    "das Internet (Sg.)": ("internet", "इंटरनेट"),
    "das Interview": ("interview", "इंटरव्यू"),
    "das Kleid": ("dress", "पोशाक"),
    "das Licht": ("light", "रोशनी"),
    "das Lokal": ("restaurant", "रेस्तरां"),
    "das Obst (Sg.)": ("fruit", "फल"),
    "das Paar": ("pair", "जोड़ा"),
    "das Plakat": ("poster", "पोस्टर"),
    "das Poster": ("poster", "पोस्टर"),
    "das Praktikum": ("internship", "इंटर्नशिप"),
    "das Produkt": ("product", "उत्पाद"),
    "das Programm": ("program", "कार्यक्रम"),
    "das Quiz (Sg.)": ("quiz", "क्विज"),
    "das Reisebüro": ("travel agency", "यात्रा एजेंसी"),
    "das Rind": ("cattle", "मवेशी"),
    "das Rätsel": ("puzzle", "पहेली"),
    "das Schild": ("sign", "संकेत"),
    "das Service (Sg.)": ("service", "सेवा"),
    "das Ski": ("ski", "स्की"),
    "das Spaß (Sg.)": ("fun", "मज़ा"),
    "das Sport (Sg.)": ("sport", "खेल"),
    "das Studium (Sg.)": ("studies", "पढ़ाई"),
    "das Taschengeld": ("pocket money", "जेब खर्च"),
    "das Thema": ("topic", "विषय"),
    "das Wasser (Sg.)": ("water", "पानी"),
    "das Wetter (Sg.)": ("weather", "मौसम"),
    "das Öl": ("oil", "तेल"),
    "der Anrufbeantworter": ("answering machine", "जवाब देने वाला"),
    "der Anschluss": ("connection", "कनेक्शन"),
    "der Apparat": ("device", "उपकरण"),
    "der Ausweis": ("ID", "पहचान पत्र"),
    "der Automat": ("vending machine", "वेंडिंग मशीन"),
    "der Babysitter": ("babysitter", "बेबीसिटर"),
    "der Bescheid": ("notification", "सूचना"),
    "der Besuch": ("visit", "मुलाकात"),
    "der Bleistift": ("pencil", "पेंसिल"),
    "der Buchstabe": ("letter (alphabet)", "अक्षर"),
    "der Club": ("club", "क्लब"),
    "der Dank (Sg.)": ("thanks", "धन्यवाद"),
    "der Durst (Sing.)": ("thirst", "प्यास"),
    "der Ehepartner": ("spouse", "जीवनसाथी"),
    "der Eintritt": ("admission", "प्रवेश"),
    "der Hamburger": ("hamburger", "हैमबर्गर"),
    "der Haushalt": ("household", "घर"),
    "der Himmel (Sg.)": ("sky", "आसमान"),
    "der Hunger (Sg.)": ("hunger", "भूख"),
    "der Kiosk": ("kiosk", "कियोस्क"),
    "der Link": ("link", "लिंक"),
    "der Magen": ("stomach", "पेट"),
    "der Mensch": ("person", "इंसान"),
    "der Mitarbeiter": ("employee", "कर्मचारी"),
    "der Moment": ("moment", "पल"),
    "der Motor": ("engine", "इंजन"),
    "der Motorroller": ("scooter", "स्कूटर"),
    "der Müll (Sg.)": ("rubbish", "कचरा"),
    "der Ort": ("place", "जगह"),
    "der Prospekt": ("brochure", "ब्रोशर"),
    "der Raum": ("room; space", "कमरा; जगह"),
    "der Regen (Sg.)": ("rain", "बारिश"),
    "der Reifen": ("tyre", "टायर"),
    "der Reis (Sg.)": ("rice", "चावल"),
    "der Reiseführer": ("travel guide", "यात्रा गाइड"),
    "der Rest": ("rest", "बाकी"),
    "der Schluss": ("end", "अंत"),
    "der Schnee (Sg.)": ("snow", "बर्फ"),
    "der Schirm": ("umbrella", "छाता"),
    "der Ski": ("ski", "स्की"),
    "der Spaß (Sg.)": ("fun", "मज़ा"),
    "der Spaziergang": ("walk", "सैर"),
    "der Star": ("star", "सितारा"),
    "der Stock": ("floor; stick", "मंजिल; छड़ी"),
    "der Stress (Sg.)": ("stress", "तनाव"),
    "der Tipp": ("tip", "सुझाव"),
    "der Titel": ("title", "शीर्षक"),
    "der Tourist": ("tourist", "पर्यटक"),
    "der Verein": ("club; association", "क्लब"),
    "der Verkehr (Sg.)": ("traffic", "यातायात"),
    "der Vermieter": ("landlord", "मकान मालिक"),
    "der Vorschlag": ("suggestion", "सुझाव"),
    "der Wagen": ("car; wagon", "गाड़ी"),
    "der Wein": ("wine", "शराब"),
    "der Umzug": ("move", "स्थानांतरण"),
    "der Zucker (Sg.)": ("sugar", "चीनी"),
    "der/das Blog": ("blog", "ब्लॉग"),
    "der/das Comic": ("comic", "कॉमिक"),
    "der/das Laptop": ("laptop", "लैपटॉप"),
    "die Autobahn": ("motorway", "हाईवे"),
    "die Fundsachen": ("lost property", "खोया हुआ सामान"),
    "die Ferien (Pl.)": ("holidays", "छुट्टियाँ"),
    "die Freizeit (Sg.)": ("free time", "खाली समय"),
    "die Erlaubnis (Sg.)": ("permission", "इजाज़त"),
    "die Veranstaltung": ("event", "कार्यक्रम"),
    # Fragments and grammar
    "(fahren": ("to drive", "गाड़ी चलाना"),
    "(haben/machen)": ("to have/do", "रखना/करना"),
    "(hat wollen als Modalverb)": ("wanted (modal)", "चाहता था"),
    "(jahr": ("year", "साल"),
    "(sich)": ("oneself", "खुद"),
    "(sich) (über)": ("about oneself", "खुद के बारे में"),
    "(z. B. Feierabend": ("e.g. end of work", "जैसे काम खत्म"),
    "(z. B. Infotafel)": ("e.g. info board", "जैसे सूचना बोर्ड"),
    "(z. B. weiter-": ("e.g. further", "जैसे आगे"),
    "-fahren/-gehen/": ("drive/go", "चलाना/जाना"),
    "-laufen/-machen/": ("run/do", "दौड़ना/करना"),
    "-nehmen/-spielen)": ("take/play", "लेना/खेलना"),
    "-nehmen/-werfen)": ("take/throw", "लेना/फेंकना"),
    "da(r) (Bsp. darauf": ("there (e.g. on it)", "वहाँ (जैसे उस पर)"),
    "darüber)": ("about it", "उसके बारे में"),
    "das (Fahr)Rad": ("bicycle", "साइकिल"),
    "das Einkaufs-": ("shopping (prefix)", "खरीदारी"),
    "das Mineral-": ("mineral (prefix)", "खनिज"),
    "das Mobil-": ("mobile (prefix)", "मोबाइल"),
    "das Schwimm-": ("swimming (prefix)", "तैराकी"),
    "das Stipen-": ("scholarship (prefix)", "छात्रवृत्ति"),
    "das Stockwerk": ("floor (storey)", "मंजिल"),
    "das Tennis (Sg.)": ("tennis", "टेनिस"),
    "das Verkehrs-": ("transport (prefix)", "यातायात"),
    "de Rentner": ("the retiree", "पेंशनभोगी"),
    "der Anruf-": ("call (prefix)", "कॉल"),
    "der Familien-": ("family (prefix)", "परिवार"),
    "der Führer-": ("driver (prefix)", "ड्राइवर"),
    "der Glück-": ("congratulations (prefix)", "बधाई"),
    "der Gruß": ("greeting", "अभिवादन"),
    "der Käse (Sg.)": ("cheese", "पनीर"),
    "der Rundgang": ("tour", "दौरा"),
    "der Spazier-": ("walk (prefix)", "सैर"),
    "der/die": ("the (m/f)", "वह (पु/स्त्री)"),
    "die Entschuldi-": ("apology (prefix)", "माफी"),
    "die Jugend-": ("youth (prefix)", "युवा"),
    "die Kranken-": ("sick/health (prefix)", "बीमार/स्वास्थ्य"),
    "die Lebens-": ("life (prefix)", "जीवन"),
    "die Leute (Pl.)": ("people", "लोग"),
    "die Postleit-": ("postal (prefix)", "डाक"),
    "die See (Sg)": ("sea", "समुद्र"),
    "die Sehens-": ("sight (prefix)", "दर्शन"),
    "die Sprech-": ("speech (prefix)", "बोल"),
    "die Straßen-": ("street (prefix)", "सड़क"),
    "die Veranstal-": ("event (prefix)", "कार्यक्रम"),
    "die Über-": ("over (prefix)", "ऊपर"),
    # Common words
    "direkt": ("direct", "सीधा"),
    "diskutieren": ("to discuss", "चर्चा करना"),
    "dringend": ("urgent", "जरूरी"),
    "drüben": ("over there", "वहाँ"),
    "drücken": ("to press", "दबाना"),
    "dumm": ("stupid", "मूर्ख"),
    "durfte": ("was allowed", "इजाज़त थी"),
    "duschen (sich)": ("to shower", "नहाना"),
    "duscht": ("showers", "नहाता है"),
    "echt": ("real", "असली"),
    "egal": ("doesn't matter", "कोई बात नहीं"),
    "eigen-": ("own (prefix)", "अपना"),
    "eilig": ("in a hurry", "जल्दी में"),
    "ein paar": ("a few", "कुछ"),
    "einfach": ("simple", "सरल"),
    "einig-": ("some (prefix)", "कुछ"),
    "einmal": ("once", "एक बार"),
    "einpacken": ("to pack", "पैक करना"),
    "eintragen (sich)": ("to register", "दर्ज करना"),
    "einzel-": ("single (prefix)", "अकेला"),
    "einziehen": ("to move in", "रहने आना"),
    "empfehlen": ("to recommend", "सिफारिश करना"),
    "enden": ("to end", "खत्म करना"),
    "entschuldigen": ("to apologise", "माफी माँगना"),
    "erinnert": ("reminded", "याद दिलाया"),
    "erkältet sein": ("to have a cold", "जुकाम होना"),
    "erlauben": ("to allow", "इजाज़त देना"),
    "erlaubt sein": ("to be allowed", "इजाज़त होना"),
    "erreichen": ("to reach", "पहुँचना"),
    "erreicht": ("reached", "पहुँचा"),
    "erst": ("only; first", "केवल; पहले"),
    "fallen": ("to fall", "गिरना"),
    "fantastisch": ("fantastic", "शानदार"),
    "faul": ("lazy", "आलसी"),
    "fehlen": ("to be missing", "कमी होना"),
    "feiern": ("to celebrate", "मनाना"),
    "fertig sein": ("to be ready", "तैयार होना"),
    "fett": ("fat", "चर्बी"),
    "fit sein": ("to be fit", "फिट होना"),
    "fleißig": ("hard-working", "मेहनती"),
    "freiwillig": ("voluntary", "स्वैच्छिक"),
    "fremd": ("strange", "अजनबी"),
    "furchtbar": ("terrible", "भयानक"),
    "geben/sagen)": ("give/say", "देना/कहना"),
    "geboren": ("born", "जन्म"),
    "Geburts-": ("birth (prefix)", "जन्म"),
    "geehrt-": ("honoured (prefix)", "सम्मानित"),
    "gefallen": ("to please", "पसंद आना"),
    "gefährlich": ("dangerous", "खतरनाक"),
    "gegenüber": ("opposite", "सामने"),
    "geht aus": ("goes out", "बाहर जाता है"),
    "genug": ("enough", "काफी"),
    "gern": ("gladly", "खुशी से"),
    "gewesen": ("been", "था"),
    "gewinnt": ("wins", "जीतता है"),
    "gibt ab": ("hands in", "जमा करता है"),
    "gibt aus": ("spends", "खर्च करता है"),
    "gleich": ("same; soon", "वही; जल्दी"),
    "grillen": ("to grill", "ग्रिल करना"),
    "gültig sein": ("to be valid", "वैध होना"),
    "halten": ("to hold", "पकड़ना"),
    "hart": ("hard", "कठोर"),
    "hat abgeholt": ("picked up", "उठा लिया"),
    "hat abgeschlossen": ("completed", "पूरा किया"),
    "hat angeboten": ("offered", "पेशकश की"),
    "hat angefangen": ("began", "शुरू किया"),
    "hat angemeldet": ("registered", "पंजीकरण किया"),
    "hat angerufen": ("called", "फोन किया"),
    "hat angesehen": ("looked at", "देखा"),
    "hat aufgehört": ("stopped", "रुका"),
    "hat aufgepasst": ("paid attention", "ध्यान दिया"),
    "hat ausgesehen": ("looked", "देखा"),
    "hat beantwortet": ("answered", "जवाब दिया"),
    "hat bedeutet": ("meant", "मतलब था"),
    "hat begonnen": ("began", "शुरू किया"),
    "hat beraten": ("advised", "सलाह दी"),
    "hat beschwert": ("complained", "शिकायत की"),
    "hat besichtigt": ("visited", "देखा"),
    "hat bestanden": ("passed", "पास किया"),
    "hat bestellt": ("ordered", "ऑर्डर किया"),
    "hat diskutiert": ("discussed", "चर्चा की"),
    "hat eingetragen": ("registered", "दर्ज किया"),
    "hat erinnert": ("reminded", "याद दिलाया"),
    "hat erlaubt": ("allowed", "इजाज़त दी"),
    "hat erreicht": ("reached", "पहुँचा"),
    "hat erzählt": ("told", "बताया"),
    "hat gearbeitet": ("worked", "काम किया"),
    "hat gebadet": ("bathed", "नहाया"),
    "hat gebraten": ("fried", "तला"),
    "hat gebraucht": ("needed", "जरूरत थी"),
    "hat gedacht": ("thought", "सोचा"),
    "hat gedrückt": ("pressed", "दबाया"),
    "hat gedurft": ("was allowed", "इजाज़त थी"),
    "hat geduscht": ("showered", "नहाया"),
    "hat geendet": ("ended", "खत्म हुआ"),
    "hat gefallen": ("pleased", "पसंद आया"),
    "hat gefehlt": ("was missing", "कम था"),
    "hat gefeiert": ("celebrated", "मनाया"),
    "hat gefragt": ("asked", "पूछा"),
    "hat gefreut": ("was pleased", "खुश हुआ"),
    "hat gefunden": ("found", "मिला"),
    "hat gegeben": ("gave", "दिया"),
    "hat gegessen": ("ate", "खाया"),
    "hat geglaubt": ("believed", "विश्वास किया"),
    "hat gehalten": ("held", "पकड़ा"),
    "hat geheiratet": ("married", "शादी की"),
    "hat geheißen": ("was called", "कहलाता था"),
    "hat geholfen": ("helped", "मदद की"),
    "hat geholt": ("fetched", "लाया"),
    "hat gehört": ("heard", "सुना"),
    "hat gekannt": ("knew", "जानता था"),
    "hat gekauft": ("bought", "खरीदा"),
    "hat geklappt": ("worked out", "काम कर गया"),
    "hat gekostet": ("cost", "कीमत थी"),
    "hat gekündigt": ("quit", "छोड़ा"),
    "hat gelassen": ("left", "छोड़ा"),
    "hat gelebt": ("lived", "रहा"),
    "hat gelegt": ("laid", "रखा"),
    "hat geliehen": ("lent", "उधार दिया"),
    "hat gelogen": ("lied", "झूठ बोला"),
    "hat gemacht": ("made", "किया"),
    "hat gemalt": ("painted", "पेंट किया"),
    "hat gemeint": ("meant", "मतलब था"),
    "hat gemerkt": ("noticed", "ध्यान दिया"),
    "hat gemocht": ("liked", "पसंद किया"),
    "hat genannt": ("named", "नाम दिया"),
    "hat genommen": ("took", "लिया"),
    "hat geparkt": ("parked", "पार्क किया"),
    "hat gepasst": ("fitted", "फिट हुआ"),
    "hat geplant": ("planned", "योजना बनाई"),
    "hat geraten": ("advised", "सलाह दी"),
    "hat geraucht": ("smoked", "धूम्रपान किया"),
    "hat gerechnet": ("calculated", "गणना की"),
    "hat geredet": ("talked", "बात की"),
    "hat gerochen": ("smelled", "सूंघा"),
    "hat gerufen": ("called", "बुलाया"),
    "hat gesagt": ("said", "कहा"),
    "hat geschafft": ("managed", "कर लिया"),
    "hat geschenkt": ("gave (gift)", "उपहार दिया"),
    "hat geschickt": ("sent", "भेजा"),
    "hat geschienen": ("seemed", "लगा"),
    "hat geschimpft": ("scolded", "डाँटा"),
    "hat geschlafen": ("slept", "सोया"),
    "hat geschlossen": ("closed", "बंद किया"),
    "hat geschmeckt": ("tasted", "स्वाद आया"),
    "hat geschnitten": ("cut", "काटा"),
    "hat geschrieben": ("wrote", "लिखा"),
    "hat gespart": ("saved", "बचाया"),
    "hat gespeichert": ("saved", "सेव किया"),
    "hat gespielt": ("played", "खेला"),
    "hat gestellt": ("placed", "रखा"),
    "hat gestritten": ("argued", "झगड़ा किया"),
    "hat gestört": ("disturbed", "परेशान किया"),
    "hat gesucht": ("searched", "ढूंढा"),
    "hat gesungen": ("sang", "गाया"),
    "hat getan": ("did", "किया"),
    "hat geteilt": ("shared", "बाँटा"),
    "hat getragen": ("wore", "पहना"),
    "hat getrunken": ("drank", "पिया"),
    "hat gewartet": ("waited", "इंतज़ार किया"),
    "hat geweckt": ("woke", "जगाया"),
    "hat geweint": ("cried", "रोया"),
    "hat gewusst": ("knew", "जानता था"),
    "hat gewählt": ("chose", "चुना"),
    "hat gezahlt": ("paid", "भुगतान किया"),
    "hat gezeichnet": ("drew", "चित्र बनाया"),
    "hat gezeigt": ("showed", "दिखाया"),
    "hat geändert": ("changed", "बदला"),
    "hat geöffnet": ("opened", "खोला"),
    "hat geübt": ("practised", "अभ्यास किया"),
    "hat hergestellt": ("produced", "बनाया"),
    "hat interessiert": ("interested", "दिलचस्पी दिखाई"),
    "hat kontrolliert": ("checked", "जाँचा"),
    "hat probiert": ("tried", "कोशिश की"),
    "hat recht gehabt": ("was right", "सही था"),
    "hat renoviert": ("renovated", "मरम्मत की"),
    "hat stattgefunden": ("took place", "हुआ"),
    "hat unterhalten": ("entertained", "बातचीत की"),
    "hat untersucht": ("examined", "जाँचा"),
    "hat verdient": ("earned", "कमाया"),
    "hat vereinbart": ("agreed", "सहमत हुआ"),
    "hat vergessen": ("forgot", "भूल गया"),
    "hat verglichen": ("compared", "तुलना की"),
    "hat verkauft": ("sold", "बेचा"),
    "hat verletzt": ("injured", "चोट पहुँचाई"),
    "hat verliebt": ("fell in love", "प्यार हो गया"),
    "hat verloren": ("lost", "खोया"),
    "hat verpasst": ("missed", "चूक गया"),
    "hat verschoben": ("postponed", "टाला"),
    "hat verstanden": ("understood", "समझा"),
    "hat versucht": ("tried", "कोशिश की"),
    "hat vorbereitet": ("prepared", "तैयार किया"),
    "hat vorgestellt": ("introduced", "परिचय कराया"),
    "hat zugehört": ("listened", "सुना"),
    "hat übernachtet": ("stayed overnight", "रात बिताई"),
    "hat/ist": ("has/is", "है"),
    "hat/ist gelegen": ("lay", "लेटा"),
    "hat/ist gesessen": ("sat", "बैठा"),
    "hat/ist gestanden": ("stood", "खड़ा था"),
    "hat/ist gesurft": ("surfed", "सर्फ किया"),
    "hatte": ("had", "था"),
    "heiraten": ("to marry", "शादी करना"),
    "heißen": ("to be called", "कहलाना"),
    "herein/rein": ("in/inside", "अंदर"),
    "herberge": ("hostel", "हॉस्टल"),
    "herstellen": ("to produce", "बनाना"),
    "herzlich": ("heartfelt", "दिल से"),
    "hin/hin-/-hin": ("there (prefix)", "वहाँ"),
    "hoffentlich": ("hopefully", "उम्मीद है"),
    "hängen": ("to hang", "लटकना"),
    "hört auf": ("stops", "रुकता है"),
    "immer": ("always", "हमेशा"),
    "informieren": ("to inform", "सूचित करना"),
    "informiert": ("informed", "सूचित"),
    "intelligent": ("intelligent", "बुद्धिमान"),
    "interessiert": ("interested", "दिलचस्पी रखता"),
    "international": ("international", "अंतर्राष्ट्रीय"),
    "ist (ab)gefahren": ("departed", "रवाना हुआ"),
    "ist (ab)geflogen": ("took off", "उड़ान भरी"),
    "ist dabei": ("is there", "वहाँ है"),
    "ist eingezogen": ("moved in", "रहने आया"),
    "ist einverstanden": ("agrees", "सहमत है"),
    "ist erkältet": ("has a cold", "जुकाम है"),
    "ist fertig": ("is ready", "तैयार है"),
    "ist fit gewesen": ("was fit", "फिट था"),
    "ist geblieben": ("stayed", "रुका"),
    "ist gegangen": ("went", "गया"),
    "ist gekommen": ("came", "आया"),
    "ist gelaufen": ("ran", "दौड़ा"),
    "ist geschwommen": ("swam", "तैरा"),
    "ist gestorben": ("died", "मर गया"),
    "ist gewandert": ("hiked", "पैदल चला"),
    "ist gewesen": ("was", "था"),
    "ist geworden": ("became", "बना"),
    "ist gültig gewesen": ("was valid", "वैध था"),
    "ist passiert": ("happened", "हुआ"),
    "ist umgestiegen": ("changed (transport)", "बदला"),
    "ist unterwegs": ("is on the way", "रास्ते में है"),
    "ist verreist": ("is travelling", "यात्रा पर है"),
    "joggen": ("to jog", "जॉगिंग करना"),
    "keinen Fall": ("no way", "बिल्कुल नहीं"),
    "kennenlernen": ("to get to know", "जानना"),
    "klappen": ("to work out", "काम करना"),
    "Klub": ("club", "क्लब"),
    "kommt an": ("arrives", "पहुँचता है"),
    "kontrollieren": ("to check", "जाँचना"),
    "kontrolliert": ("checked", "जाँचा"),
    "lange": ("long", "लंबा"),
    "lassen": ("to let", "देना"),
    "leicht": ("easy; light", "आसान; हल्का"),
    "leider": ("unfortunately", "दुर्भाग्य से"),
    "leihen": ("to lend", "उधार देना"),
    "leise": ("quiet", "शांत"),
    "letzt-": ("last (prefix)", "आखिरी"),
    "lieb-": ("dear (prefix)", "प्यारा"),
    "Lieblings-": ("favourite (prefix)", "पसंदीदा"),
    "liefern": ("to deliver", "डिलीवर करना"),
    "lügen": ("to lie", "झूठ बोलना"),
    "machen/-helfen)": ("do/help", "करना/मदद"),
    "mal / das Mal": ("times; the time", "बार; समय"),
    "manch-": ("some (prefix)", "कुछ"),
    "manchmal": ("sometimes", "कभी-कभी"),
    "mehr": ("more", "अधिक"),
    "meinen": ("to mean", "मतलब"),
    "meist-": ("most (prefix)", "सबसे"),
    "meldet an": ("registers", "पंजीकरण करता है"),
    "merken": ("to notice", "ध्यान देना"),
    "mindestens": ("at least", "कम से कम"),
    "mochte": ("liked", "पसंद था"),
    "modern": ("modern", "आधुनिक"),
    "männlich": ("male", "पुरुष"),
    "nach Hause kommen": ("to come home", "घर आना"),
    "nebenan": ("next door", "बगल में"),
    "nennen": ("to name", "नाम देना"),
    "nichts": ("nothing", "कुछ नहीं"),
    "nie": ("never", "कभी नहीं"),
    "nirgends": ("nowhere", "कहीं नहीं"),
    "normal": ("normal", "सामान्य"),
    "notieren": ("to note", "नोट करना"),
    "notwendig": ("necessary", "जरूरी"),
    "nächste": ("next", "अगला"),
    "nützlich": ("useful", "उपयोगी"),
    "oft": ("often", "अक्सर"),
    "online": ("online", "ऑनलाइन"),
    "organisieren": ("to organise", "व्यवस्थित करना"),
    "organisiert": ("organised", "व्यवस्थित"),
    "packen": ("to pack", "पैक करना"),
    "packt ein": ("packs", "पैक करता है"),
    "parken": ("to park", "पार्क करना"),
    "passieren": ("to happen", "होना"),
    "passiert": ("happened", "हुआ"),
    "passt auf": ("pays attention", "ध्यान देता है"),
    "plötzlich": ("suddenly", "अचानक"),
    "praktisch": ("practical", "व्यावहारिक"),
    "preiswert": ("good value", "सस्ता"),
    "privat": ("private", "निजी"),
    "pro": ("per", "प्रति"),
    "probiert": ("tried", "कोशिश किया"),
    "prüfen": ("to check", "जाँचना"),
    "raten": ("to advise", "सलाह देना"),
    "rauchen": ("to smoke", "धूम्रपान करना"),
    "rechnen": ("to calculate", "गणना करना"),
    "recht haben": ("to be right", "सही होना"),
    "reden": ("to talk", "बात करना"),
    "reich": ("rich", "अमीर"),
    "reisen": ("to travel", "यात्रा करना"),
    "reiten": ("to ride", "घुड़सवारी करना"),
    "renovieren": ("to renovate", "मरम्मत करना"),
    "reparieren": ("to repair", "मरम्मत करना"),
    "reserviert": ("reserved", "आरक्षित"),
    "romantisch": ("romantic", "रोमांटिक"),
    "ruht aus": ("rests", "आराम करता है"),
    "rund": ("round", "गोल"),
    "sammelt": ("collects", "इकट्ठा करता है"),
    "schade": ("pity", "अफ़सोस"),
    "schaffen": ("to manage", "कर लेना"),
    "scheinen": ("to seem", "लगना"),
    "schimpfen": ("to scold", "डाँटना"),
    "schimpft": ("scolds", "डाँटता है"),
    "schließt": ("closes", "बंद करता है"),
    "schließt ab": ("locks", "ताला लगाता है"),
    "schlimm": ("bad", "बुरा"),
    "schmeckt": ("tastes", "स्वाद आता है"),
    "schneiden (sich)": ("to cut", "काटना"),
    "schneidet": ("cuts", "काटता है"),
    "schreiben": ("to write", "लिखना"),
    "schriftlich": ("in writing", "लिखित"),
    "schwach": ("weak", "कमज़ोर"),
    "schwanger": ("pregnant", "गर्भवती"),
    "schädlich": ("harmful", "नुकसानदेह"),
    "sein": ("to be", "होना"),
    "setzen (sich)": ("to sit down", "बैठना"),
    "setzt": ("sets", "रखता है"),
    "sicher": ("safe", "सुरक्षित"),
    "sieht aus": ("looks", "दिखता है"),
    "so": ("so", "इतना"),
    "sofort": ("immediately", "तुरंत"),
    "sogar": ("even", "भी"),
    "sollte": ("should", "चाहिए था"),
    "sonst": ("otherwise", "वरना"),
    "spazieren gehen": ("to go for a walk", "सैर करना"),
    "spielt": ("plays", "खेलता है"),
    "sportlich": ("sporty", "खेल प्रेमी"),
    "stark": ("strong", "मज़बूत"),
    "stattfinden": ("to take place", "होना"),
    "steigt aus": ("gets off", "उतरता है"),
    "steigt ein": ("gets in", "चढ़ता है"),
    "stellt vor": ("introduces", "परिचय कराता है"),
    "sterben": ("to die", "मरना"),
    "streiten (sich)": ("to argue", "झगड़ना"),
    "streng": ("strict", "सख्त"),
    "stressig": ("stressful", "तनावपूर्ण"),
    "stören": ("to disturb", "परेशान करना"),
    "surfen": ("to surf", "सर्फ करना"),
    "sympathisch": ("likeable", "सहानुभूतिपूर्ण"),
    "tauscht (aus)": ("exchanges", "अदला-बदली करता है"),
    "teilen": ("to share", "बाँटना"),
    "teilnehmen": ("to participate", "भाग लेना"),
    "teuer": ("expensive", "महंगा"),
    "tief": ("deep", "गहरा"),
    "total": ("total", "कुल"),
    "treffen (sich)": ("to meet", "मिलना"),
    "trifft": ("meets", "मिलता है"),
    "trägt ein": ("enters", "दर्ज करता है"),
    "träumt": ("dreams", "सपना देखता है"),
    "tschüs": ("bye", "बाय"),
    "tun": ("to do", "करना"),
    "um ... Uhr": ("at ... o'clock", "... बजे"),
    "unbedingt": ("absolutely", "अवश्य"),
    "unterhalten (sich)": ("to converse", "बातचीत करना"),
    "unterhält": ("entertains", "बातचीत करता है"),
    "unternehmen": ("to do (activity)", "करना"),
    "unterschreiben": ("to sign", "हस्ताक्षर करना"),
    "untersuchen": ("to examine", "जाँचना"),
    "untersucht": ("examines", "जाँचता है"),
    "unterwegs sein": ("to be on the way", "रास्ते में होना"),
    "verabredet sein": ("to have a date", "मुलाकात तय होना"),
    "verbieten /": ("to forbid", "मना करना"),
    "verboten sein": ("to be forbidden", "मना होना"),
    "vereinbaren": ("to agree", "तय करना"),
    "vergessen": ("to forget", "भूलना"),
    "vergisst": ("forgets", "भूल जाता है"),
    "vergleichen": ("to compare", "तुलना करना"),
    "vergleicht": ("compares", "तुलना करता है"),
    "verletzen (sich)": ("to injure", "चोट लगना"),
    "verletzt": ("injured", "चोट लगी"),
    "verlieben (sich)": ("to fall in love", "प्यार में पड़ना"),
    "verliert": ("loses", "खो देता है"),
    "vermieten": ("to rent out", "किराये पर देना"),
    "verpassen": ("to miss", "चूकना"),
    "verreisen": ("to travel", "यात्रा पर जाना"),
    "verreist": ("travelling", "यात्रा पर"),
    "verschieben": ("to postpone", "टालना"),
    "verschieden": ("different", "अलग"),
    "versteht": ("understands", "समझता है"),
    "versucht": ("tries", "कोशिश करता है"),
    "viel": ("much", "बहुत"),
    "vielleicht": ("perhaps", "शायद"),
    "vorbei": ("past", "पिछला"),
    "vorbereiten": ("to prepare", "तैयार करना"),
    "vorher": ("before", "पहले"),
    "vorn(e)": ("at the front", "आगे"),
    "vorsichtig": ("careful", "सावधान"),
    "vorstellen (sich)": ("to introduce oneself", "परिचय देना"),
    "Vorwort": ("foreword", "प्रस्तावना"),
    "vorwärts": ("forward", "आगे"),
    "wach": ("awake", "जागा हुआ"),
    "wahr": ("true", "सच"),
    "war dabei": ("was there", "वहाँ था"),
    "war fit": ("was fit", "फिट था"),
    "wartet": ("waits", "इंतज़ार करता है"),
    "waschen (sich)": ("to wash", "धोना"),
    "weg sein": ("to be gone", "गायब होना"),
    "wer (wen": ("who (whom", "कौन (किसे"),
    "willkommen": ("welcome", "स्वागत"),
    "Wortgruppen": ("word groups", "शब्द समूह"),
    "wählen": ("to choose", "चुनना"),
    "ändern": ("to change", "बदलना"),
    "ärgern (sich)": ("to get angry", "गुस्सा होना"),
    "ärgert": ("annoys", "परेशान करता है"),
    "übernachten": ("to stay overnight", "रात रुकना"),
    "übersetzen": ("to translate", "अनुवाद करना"),
    "überweisen": ("to transfer", "ट्रांसफर करना"),
    "überweist": ("transfers", "ट्रांसफर करता है"),
    "beantworter": ("answerer", "जवाब देने वाला"),
    "beantwortet": ("answered", "जवाब दिया"),
    "bedankt": ("thanked", "धन्यवाद दिया"),
    "beeilt": ("hurried", "जल्दी किया"),
    "begründen": ("to justify", "औचित्य देना"),
    "bereitet vor": ("prepares", "तैयार करता है"),
    "beschwert": ("complained", "शिकायत की"),
    "besichtigt": ("visited", "देखा"),
    "bestellt": ("ordered", "ऑर्डर किया"),
    "besucht": ("visited", "मिलने गया"),
    "bewirbt": ("applies", "आवेदन करता है"),
    "bleibt": ("stays", "रुकता है"),
    "Heute ist der 20.2.2012": ("Today is 20 Feb 2012", "आज 20 फरवरी 2012 है"),
    "her/her-/-her": ("here (prefix)", "यहाँ"),
    "laufen)": ("run", "दौड़ना"),
    "Länder und Nationalitäten": ("Countries and nationalities", "देश और राष्ट्रीयता"),
    "setzung": ("translation", "अनुवाद"),
    "zu sein": ("to be", "होना"),
    "zum Beispiel": ("for example", "उदाहरण के लिए"),
    "zurück": ("back", "वापस"),
    "zurück-": ("back (prefix)", "वापस"),
    "würdigkeit": ("worthiness", "योग्यता"),
    "Hausmann": ("househusband", "घरेलू पति"),
    "dium": ("(fragment)", "अंश"),
    "dabei (sein)": ("to have (with one)", "साथ होना"),
    "damals": ("back then", "उस समय"),
    "daneben": ("next to it", "बगल में"),
    "der Service (Sg.)": ("service", "सेवा"),
    "der Sport (Sg.)": ("sport", "खेल"),
    "einkaufen": ("to shop", "खरीदारी करना"),
    "fliegt (ab)": ("takes off", "उड़ान भरता है"),
    "freut": ("is pleased", "खुश होता है"),
    "fährt (ab)": ("departs", "रवाना होता है"),
    "fängt an": ("begins", "शुरू करता है"),
    "fühlt": ("feels", "महसूस करता है"),
    "gang": ("walk; corridor", "चलना; गलियारा"),
    "gehängt": ("hung", "लटकाया"),
    "gehören": ("to belong", "संबंधित होना"),
    "hat gehangen/": ("hung", "लटका था"),
    "hat gesehen": ("saw", "देखा"),
    "hat leidgetan": ("was sorry", "अफ़सोस जताया"),
    "heraus/raus": ("out", "बाहर"),
    "ist/hat gejoggt": ("jogged", "जॉगिंग किया"),
    "leidtun/leid tun": ("to be sorry", "अफ़सोस होना"),
    "lernt kennen": ("gets to know", "जानता है"),
    "reservierte": ("reserved", "आरक्षित किया"),
    "tung": ("(suffix)", "ता/ती"),
    "zieht (an/aus)": ("puts on/takes off", "पहनता/उतारता है"),
    "zieht ein": ("moves in", "रहने आता है"),
}


def load_translations():
    trans = {}
    for g, (e, h) in BUILTIN_TRANSLATIONS.items():
        trans[g] = (e, h)
        trans[g.lower()] = (e, h)
    data_path = BASE / "scripts" / "data" / "a2_translations.csv"
    if data_path.exists():
        with open(data_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                g = (row.get("German") or "").strip()
                e = (row.get("English") or "").strip()
                h = (row.get("Hindi") or "").strip()
                if g and e and h:
                    trans[g] = (e, h)
                    trans[g.lower()] = (e, h)
    return trans


def normalize_for_lookup(german):
    """Normalize for translation lookup."""
    s = (german or "").strip()
    return s.lower()


def assign_category(german, english, hindi):
    """Assign one category per word. Returns category name."""
    g = (german or "").strip().lower()
    e = (english or "").lower()
    # Greetings & Basics
    if any(x in g for x in ["hallo", "guten tag", "guten morgen", "guten abend", "gute nacht", "tschüss", "auf wiedersehen", "bis bald", "danke", "bitte", "ja", "nein", "grüß", "begrüßung"]):
        return CATEGORIES[0]
    # Colors
    if any(x in g for x in ["rot", "blau", "grün", "gelb", "schwarz", "weiß", "braun", "grau", "orange", "rosa", "lila", "farbe", "bunt", "blond", "dunkel", "hell "]):
        return CATEGORIES[1]
    # Family & People
    if any(x in g for x in ["familie", "mutter", "vater", "bruder", "schwester", "kind", "eltern", "großeltern", "onkel", "tante", "cousin", "enkel", "ehemann", "ehefrau", "partner", "freund", "freundin", "nachbar", "mensch", "leute", "dame", "herr", "frau ", "baby", "erwachsene", "verwandt", "schwager", "schwieger", "stief"]):
        return CATEGORIES[2]
    # Body Parts
    if any(x in g for x in ["kopf", "auge", "ohr", "nase", "mund", "arm", "bein", "hand", "fuß", "finger", "rücken", "bauch", "magen", "zahn", "haar", "körper"]):
        return CATEGORIES[3]
    # Health & Feelings
    if any(x in g for x in ["krank", "gesund", "arzt", "krankenhaus", "apotheke", "medizin", "fieber", "schmerz", "behandlung", "patient", "impfung", "therapie", "angst", "freude", "traurig", "wut", "stress", "müdigkeit", "gefühl", "stimmung", "laune", "sorge", "hoffnung", "liebe", "hass", "entspannung", "wellness", "massage", "yoga", "meditation", "hygiene", "diagnose", "symptom", "operation", "verletzung", "wunde", "puls", "blutdruck", "erkältet", "schwindel", "übelkeit", "albtraum", "genesen", "krankenkasse", "krankenschwester", "notarzt", "optiker", "pflaster", "verband", "thermometer", "bluttest", "tablette", "spritze", "salbe", "diät", "magenproblem"]):
        return CATEGORIES[4]
    # Food
    if any(x in g for x in ["essen", "frühstück", "mittagessen", "abendessen", "brot", "fleisch", "gemüse", "obst", "salat", "kartoffel", "nudel", "reis", "pizza", "käse", "butter", "ei", "apfel", "banane", "tomate", "zwiebel", "bohne", "birne", "zitrone", "beere", "torte", "kuchen", "süßigkeit", "portion", "gericht", "hauptgericht", "dessert", "beilage", "zutat", "rezept", "restaurant", "lokal", "café", "cafeteria", "kantine", "bäckerei", "imbiss", "picknick", "grill", "kalorie", "vitamin", "ernährung", "guten appetit", "speisekarte"]):
        return CATEGORIES[5]
    # Drinks
    if any(x in g for x in ["wasser", "tee", "kaffee", "milch", "saft", "bier", "wein", "getränk", "trinken", "mineral", "flasche", "glas ", "tasse", "durst"]):
        return CATEGORIES[6]
    # House & Furniture
    if any(x in g for x in ["haus", "wohnung", "zimmer", "bett", "tisch", "stuhl", "sofa", "schrank", "regal", "fenster", "tür", "bad", "badezimmer", "küche", "treppe", "balkon", "garten", "garage", "keller", "dach", "möbel", "lampe", "steckdose", "heizung", "teppich", "gardine", "spiegel", "nachttisch", "kommode", "bettzeug", "laken", "decke", "stockwerk", "erdgeschoss", "einziehen", "umzug", "vermieter", "miete", "nebenkosten"]):
        return CATEGORIES[7]
    # Kitchen Items
    if any(x in g for x in ["küche", "herd", "kühlschrank", "geschirr", "topf", "pfanne", "gabel", "messer", "löffel", "teller", "tasse", "glas", "besteck", "spülmaschine", "geschirrspüler", "putzmittel", "müll", "mülltonne", "recycling"]):
        return CATEGORIES[8]
    # Clothing
    if any(x in g for x in ["kleidung", "kleid", "hose", "hemd", "jacke", "pullover", "rock", "mantel", "schuh", "socke", "unterwäsche", "pyjama", "jeans", "bluse", "anzug", "krawatte", "tasche", "gürtel", "accessoire", "ohrring", "brille", "uhr ", "schmuck", "mode", "anprobe", "passform", "stoff", "baumwolle", "wolle", "seide", "leder", "sandale", "turnschuh", "strick", "nähen"]):
        return CATEGORIES[9]
    # Transport & Travel
    if any(x in g for x in ["auto", "bus", "bahn", "zug", "flug", "flughafen", "bahnhof", "bahnsteig", "ticket", "fahrkarte", "reise", "reisen", "urlaub", "koffer", "gepäck", "reisebüro", "reiseführer", "reisepass", "visum", "unterkunft", "hotel", "zimmer reservieren", "doppelzimmer", "einzelzimmer", "raststätte", "parken", "parkuhr", "benzin", "reifen", "motor", "wagen", "helm", "fahrrad", "radfahren", "verkehr", "autobahn", "straße", "weg", "umleitung", "maut", "vignette", "zoll", "passkontrolle", "bordkarte", "landung", "abflug", "gate", "gps", "navigation", "führerschein", "unfall", "panne", "versicherung", "verkehrsschild", "ampel", "fußgängerzone"]):
        return CATEGORIES[10]
    # Places & City
    if any(x in g for x in ["stadt", "dorf", "platz", "straße", "markt", "zentrum", "mitte", "ort", "adresse", "karte", "stadtplan", "führung", "besichtigung", "denkmal", "kirche", "dom", "museum", "galerie", "ausstellung", "bibliothek", "post", "bank ", "filiale", "apotheke", "drogerie", "supermarkt", "kiosk", "disco", "club", "kino", "theater", "oper", "stadion", "park", "brunnen", "brücke", "baustelle", "ausgang", "eingang", "toilette", "haltestelle"]):
        return CATEGORIES[11]
    # Nature & Weather
    if any(x in g for x in ["natur", "wald", "baum", "blume", "pflanze", "garten", "wetter", "sonne", "regen", "schnee", "wind", "wolke", "warm", "kalt", "hitze", "kälte", "frost", "hagel", "sturm", "flut", "dürre", "see ", "fluss", "berg", "strand", "küste", "landschaft", "umwelt", "klima", "tier", "vogel", "insekt"]):
        return CATEGORIES[12]
    # Time
    if any(x in g for x in ["zeit", "uhr", "stunde", "minute", "tag", "woche", "monat", "jahr", "datum", "morgen", "abend", "nacht", "früh", "spät", "jetzt", "heute", "gestern", "montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag", "sonntag", "wochenende", "ferien", "urlaub", "feiertag", "termin", "pause", "frühling", "sommer", "herbst", "winter", "saison", "kalender", "stundenplan", "zeitplan", "deadline", "frist", "zeitraum", "zeitpunkt", "zeitzone", "uhrzeit", "mitternacht", "täglich", "monatlich"]):
        return CATEGORIES[13]
    # School & Learning
    if any(x in g for x in ["schule", "unterricht", "stunde ", "klasse", "lehrer", "schüler", "student", "universität", "hochschule", "kurs", "prüfung", "klausur", "hausaufgabe", "referat", "vortrag", "vorlesung", "seminar", "semester", "zeugnis", "stipendium", "lernen", "unterricht", "fach", "mathematik", "deutsch", "englisch", "physik", "chemie", "biologie", "geschichte", "geografie", "kunst", "musik", "sport", "religion", "bildung", "nachhilfe", "prüfungsvorbereitung", "einschreibung", "tafel", "kreide", "buch", "heft", "mappe", "ranzen", "wörterbuch", "vokabel", "lernstoff", "abitur", "direktor", "klassenfahrt"]):
        return CATEGORIES[14]
    # Work & Job
    if any(x in g for x in ["arbeit", "beruf", "job", "chef", "kollege", "mitarbeiter", "angestellter", "ausbildung", "praktikum", "gehalt", "kündigung", "bewerbung", "bewerben", "stelle", "arbeitslos", "büro", "meeting", "deadline", "feierabend", "pause", "urlaub", "vollzeit", "teilzeit", "beförderung", "qualifikation", "karriere", "rentner", "pension"]):
        return CATEGORIES[15]
    # Shopping & Money
    if any(x in g for x in ["einkaufen", "shop", "geschäft", "preis", "geld", "euro", "cent", "konto", "bank", "überweisung", "barzahlung", "rechnung", "kasse", "rabatt", "angebot", "reklamation", "retoure", "umtausch", "gutschein", "kredit", "zins", "schuld", "steuer", "gehalt", "miete", "gebühr", "kassenbon", "geldautomat", "abheben", "einzahlen", "sparkonto", "kontostand", "wechselkurs", "währung", "bargeld", "rechnung bezahlen", "billig", "teuer", "preiswert", "sonderangebot"]):
        return CATEGORIES[16]
    # Communication
    if any(x in g for x in ["telefon", "handy", "email", "mail", "internet", "sms", "chat", "brief", "post", "postkarte", "anschrift", "anruf", "nachricht", "information", "auskunft", "frage", "antwort", "gespräch", "diskussion", "interview", "präsentation", "vortrag", "rede", "sprache", "übersetzung", "wörterbuch", "website", "homepage", "social media", "sender", "fernsehen", "radio", "zeitung", "zeitschrift", "werbung", "anzeige"]):
        return CATEGORIES[17]
    # Animals
    if any(x in g for x in ["tier", "hund", "katze", "vogel", "fisch", "pferd", "kuh", "schaf", "schwein", "hase", "fuchs", "bär", "wolf", "löwe", "elefant", "adler", "eule", "schwan", "ente", "papagei", "maus", "ratte", "schlange", "insekt", "biene", "mücke", "käfer", "schnecke", "regenwurm", "igel", "maulwurf", "otter", "biber", "dachs", "waschbär", "storch", "spatz", "taube", "krähe", "ameise", "floh", "tierpark", "zoo", "aquarium"]):
        return CATEGORIES[18]
    # Celebrations
    if any(x in g for x in ["geburtstag", "party", "feier", "fest", "hochzeit", "weihnachten", "ostern", "karneval", "silvester", "neujahr", "einladung", "geschenk", "karte ", "glückwunsch", "grillparty", "taufe", "beerdigung", "trauung", "verlobung", "parade", "festival", "konzert", "aufführung"]):
        return CATEGORIES[19]
    # Personal Items
    if any(x in g for x in ["tasche", "geldbörse", "brieftasche", "schlüssel", "brille", "uhr", "handy", "laptop", "tablet", "kamera", "buch", "heft", "stift", "bleistift", "radiergummi", "schere", "kleber", "papier", "zettel", "ausweis", "führerschein", "pass", "kreditkarte", "brille", "regenschirm", "schirm", "sonnenbrille", "rucksack", "koffer"]):
        return CATEGORIES[20]
    # Question Words
    if any(x in g for x in ["wer", "was", "wo", "wohin", "woher", "wann", "wie", "warum", "welch", "wie viel", "wie viele"]):
        return CATEGORIES[21]
    # Pronouns
    if any(x in g for x in ["ich", "du", "er", "sie ", "es", "wir", "ihr", "sie", "mein", "dein", "sein", "ihr", "unser", "euer", "sich", "man", "jemand", "niemand", "etwas", "nichts", "alle", "andere", "einige"]):
        return CATEGORIES[22]
    # Verbs (catch common verb patterns; many remain)
    if any(x in g for x in [" haben", " sein", " werden", " können", " müssen", " sollen", " wollen", " dürfen", " möchten"]) or re.search(r'\b(hat|ist|war|haben|sind|werden|können|müssen|sollen|wollen|dürfen)\b', g):
        return CATEGORIES[23]
    # Adjectives
    if any(x in g for x in ["gut", "schlecht", "groß", "klein", "alt", "neu", "jung", "schnell", "langsam", "leicht", "schwer", "richtig", "falsch", "wichtig", "interessant", "schön", "hässlich", "stark", "schwach", "reich", "arm", "voll", "leer", "froh", "traurig", "müde", "krank", "gesund", "frei", "besetzt", "offen", "geschlossen", "einfach", "schwer", "teuer", "billig", "nah", "weit", "früh", "spät", "viel", "wenig", "ganz", "halb", "erste", "letzte", "nächste", "gleiche", "andere", "eigen", "gemeinsam", "besonders", "normal", "typisch", "modern", "traditionell", "privat", "öffentlich", "international", "lokal", "aktiv", "passiv", "positiv", "negativ"]):
        return CATEGORIES[24]
    # Adverbs & Connectors
    if any(x in g for x in ["auch", "noch", "schon", "immer", "nie", "manchmal", "oft", "hier", "dort", "da", "heute", "morgen", "gestern", "jetzt", "dann", "deshalb", "trotzdem", "weil", "dass", "wenn", "als", "obwohl", "sondern", "aber", "denn", "oder", "und", "sogar", "besonders", "eigentlich", "vielleicht", "wahrscheinlich", "leider", "zum beispiel", "zuerst", "dann", "danach", "endlich", "plötzlich", "sofort", "gleich", "bald", "noch", "schon", "nur", "sogar", "fast", "ganz", "sehr", "zu ", "genug", "etwa", "ungefähr", "circa", "links", "rechts", "oben", "unten", "vorn", "hinten", "innen", "außen", "vorher", "nachher", "davor", "danach"]):
        return CATEGORIES[25]
    # Default: Verbs (most remaining are verb forms)
    if re.match(r'^(hat|ist|war|haben|sind|werden|können|müssen)\s', g) or re.search(r'\b(gehen|kommen|machen|sagen|geben|nehmen|sehen|wissen|kennen)\b', g):
        return CATEGORIES[23]
    # Custom: Grammar / Other
    if any(x in g for x in ["(sg.)", "(pl.)", "abkürzung", "wortliste", "vorwort", "wortgruppen"]):
        return "📋 Grammar & Reference"
    return CATEGORIES[23]  # Default Verbs


def normalize_key(g):
    """Word after article for cross-row lookup."""
    s = re.sub(r'^(der|die|das)\s+', '', (g or "").strip(), flags=re.I)
    return s.lower().strip()


def main():
    translations = load_translations()
    rows_in = []
    with open(IN_CSV, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows_in.append({
                "German": (row.get("German") or "").strip(),
                "English": (row.get("English") or "").strip(),
                "Hindi": (row.get("Hindi") or "").strip(),
            })

    # Build same-file lookup from rows that already have real translations
    for r in rows_in:
        g, e, h = r["German"], r["English"], r["Hindi"]
        if not g or e == "To be translated" or h == "अनुवाद किया जाना है":
            continue
        translations[g] = (e, h)
        translations[g.lower()] = (e, h)
        base = normalize_key(g)
        if base and base not in translations:
            translations[base] = (e, h)

    PLACEHOLDER_EN = "To be translated"
    PLACEHOLDER_HI = "अनुवाद किया जाना है"
    completed = 0
    used_categories = set()
    out_rows = []

    for r in rows_in:
        g, e, h = r["German"], r["English"], r["Hindi"]
        if not g:
            continue
        # Fill translations from dict (exact, then normalized)
        if e == PLACEHOLDER_EN or h == PLACEHOLDER_HI or not e or not h:
            key_lower = g.lower()
            base = normalize_key(g)
            if g in translations:
                e, h = translations[g]
            elif key_lower in translations:
                e, h = translations[key_lower]
            elif base in translations:
                e, h = translations[base]
            else:
                # Last resort: try first word (e.g. verb stem)
                first = g.split()[0].lower() if g else ""
                if first in translations:
                    e, h = translations[first]
            if e == PLACEHOLDER_EN or not e:
                e = "to do / thing"
            if h == PLACEHOLDER_HI or not h:
                h = "करना / चीज़"
            completed += 1
        cat = assign_category(g, e, h)
        used_categories.add(cat)
        out_rows.append({"Category": cat, "German": g, "English": e, "Hindi": h})

    (BASE / "output").mkdir(exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Category", "German", "English", "Hindi"])
        w.writeheader()
        w.writerows(out_rows)

    # Report
    still_placeholder = sum(1 for r in out_rows if "to do / thing" in r["English"] or "करना / चीज़" in r["Hindi"] or "translate:" in r["English"] or "अनुवाद:" in r["Hindi"])
    report = f"""A2 VOCABULARY — CATEGORIZATION & COMPLETION REPORT
========================================================

Total words:                    {len(out_rows)}
Translations completed:        {completed}
Entries still needing manual translation: {still_placeholder}

Categories used ({len(used_categories)}):
{chr(10).join(sorted(used_categories))}

Data quality:
- Every word has a category:   Yes
- No blank German:            Yes
- No blank English:            {"No" if still_placeholder else "Yes"}
- No blank Hindi:              {"No" if still_placeholder else "Yes"}

Output: {OUT_CSV}
Columns: Category | German | English | Hindi
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(f"Done. Total: {len(out_rows)}, Categories: {len(used_categories)}, Still need translation: {still_placeholder}")


if __name__ == "__main__":
    main()
