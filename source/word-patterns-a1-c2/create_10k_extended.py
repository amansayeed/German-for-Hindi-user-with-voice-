# -*- coding: utf-8 -*-
"""
Create extended_words.json with 450 (de, en, hi) entries per pattern.
Merge with build_word_patterns.py DATA to reach 10,000+ words.
Run: python create_10k_extended.py

To reach 10,000+ unique words in the final vocabulary: add more (en|hi) lines
to the _*_BULK strings below, or create extended_extra.json in this folder with
format {"pattern_id": [["de","en","hi"], ...]} to merge extra entries per pattern.
"""
import json
import os
import re

# Same pattern IDs as in build_word_patterns.py
PATTERN_IDS = [
    "pattern_1_ance_ence",
    "pattern_2_ism",
    "pattern_3_sion_tion",
    "pattern_4_ty",
    "pattern_5_ment",
    "pattern_6_al",
    "pattern_7_ic",
    "pattern_8_ive",
    "pattern_9_ous",
    "pattern_10_ary",
    "pattern_11_ant",
    "pattern_12_ist",
    "pattern_13_logy",
    "pattern_14_graphy",
    "pattern_15_meter",
    "pattern_16_scope",
    "pattern_17_phobia",
    "pattern_18_phile",
    "pattern_19_age",
    "pattern_20_ure",
    "pattern_21_ary_arie",
    "pattern_22_ate",
]

TARGET_PER_PATTERN = 450
OUTPUT_FILENAME = "extended_words.json"


def _dedupe_triples(triples):
    """Remove duplicate (de, en, hi) by (de_lower, en_lower). Keep first."""
    seen = set()
    out = []
    for de, en, hi in triples:
        key = (de.strip().lower(), en.strip().lower())
        if key in seen:
            continue
        seen.add(key)
        out.append([de, en, hi])
    return out


def _cap_first(s):
    return s[0].upper() + s[1:] if s else s


# ---------------------------------------------------------------------------
# Pattern 1: -ance/-ence → -anz/-enz (die)
# ---------------------------------------------------------------------------
def _build_pattern_1():
    # (English word, Hindi). German: die + stem with -ance→-anz, -ence→-enz
    en_hi_ance = [
        ("tolerance", "सहनशीलता"), ("acceptance", "स्वीकृति"), ("distance", "दूरी"),
        ("relevance", "प्रासंगिकता"), ("elegance", "शिष्टता"), ("ignorance", "अज्ञान"),
        ("importance", "महत्व"), ("abundance", "प्रचुरता"), ("attendance", "उपस्थिति"),
        ("assistance", "सहायता"), ("resistance", "प्रतिरोध"), ("persistence", "दृढ़ता"),
        ("substance", "पदार्थ"), ("instance", "उदाहरण"), ("circumstance", "परिस्थिति"),
        ("finance", "वित्त"), ("appearance", "उपस्थिति"), ("clearance", "साफ़ करना"),
        ("insurance", "बीमा"), ("governance", "शासन"), ("maintenance", "रखरखाव"),
        ("ordinance", "अध्यादेश"), ("dominance", "प्रभुत्व"), ("continuance", "निरंतरता"),
    ]
    en_hi_ence = [
        ("existence", "अस्तित्व"), ("conference", "सम्मेलन"), ("presence", "उपस्थिति"),
        ("absence", "अनुपस्थिति"), ("intelligence", "बुद्धिमत्ता"), ("difference", "अंतर"),
        ("reference", "संदर्भ"), ("sequence", "क्रम"), ("frequency", "आवृत्ति"),
        ("tendency", "प्रवृत्ति"), ("evidence", "प्रमाण"), ("residence", "निवास"),
        ("consistency", "स्थिरता"), ("consequence", "परिणाम"), ("competence", "क्षमता"),
        ("transparency", "पारदर्शिता"), ("permanence", "स्थायित्व"), ("influence", "प्रभाव"),
        ("experience", "अनुभव"), ("science", "विज्ञान"), ("patience", "धैर्य"),
        ("convenience", "सुविधा"), ("audience", "दर्शक"), ("obedience", "आज्ञाकारिता"),
        ("violence", "हिंसा"), ("silence", "चुप्पी"), ("confidence", "आत्मविश्वास"),
        ("independence", "स्वतंत्रता"), ("dependence", "निर्भरता"), ("emergence", "उदय"),
    ]
    more_ence = [
        ("preference", "पसंद"), ("inference", "अनुमान"), ("coherence", "सुसंगतता"),
        ("adherence", "पालन"), ("recurrence", "पुनरावृत्ति"), ("occurrence", "घटना"),
        ("concurrence", "सहमति"), ("divergence", "विचलन"), ("convergence", "अभिसरण"),
        ("insistence", "जोर"), ("resilience", "लचीलापन"), ("excellence", "उत्कृष्टता"),
        ("negligence", "लापरवाही"), ("prominence", "प्रमुखता"), ("imminence", "निकटता"),
        ("eminence", "श्रेष्ठता"), ("continence", "संयम"), ("abstinence", "संयम"),
        ("innocence", "निर्दोषता"), ("magnificence", "शान"),
    ]
    en_hi = en_hi_ance + en_hi_ence + more_ence + _parse_bulk(_ANCE_ENCE_BULK) + _parse_bulk(_ANCE_ENCE_BULK_2) + _parse_bulk(_ANCE_ENCE_BULK_3) + _parse_bulk(_ANCE_ENCE_BULK_4)
    seen = set()
    out = []
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        if en.endswith("ance"):
            stem = en.replace("ance", "anz")
        elif en.endswith("ence"):
            stem = en.replace("ence", "enz")
        else:
            stem = en
        de = "die " + _cap_first(stem)
        out.append((de, en, hi))
    return out


# Bulk -ance/-ence (en|hi). German: die + -anz/-enz.
_ANCE_ENCE_BULK = """
alliance|गठबंधन  allowance|भत्ता  annoyance|झुंझलाहट  assurance|आश्वासन
balance|संतुलन  brilliance|चमक  compliance|अनुपालन  defiance|अवज्ञा
disturbance|अशांति  endurance|सहनशीलता  grievance|शिकायत  guidance|मार्गदर्शन
inheritance|विरासत  nuisance|उपद्रव  perseverance|दृढ़ता  reliance|भरोसा
resemblance|समानता  surveillance|निगरानी  vengeance|बदला
affluence|समृद्धि  benevolence|परोपकार  circumference|परिधि  coincidence|संयोग
conscience|अंतरात्मा  fluorescence|प्रतिदीप्ति  incidence|घटना  indulgence|लिप्तता
licence|लाइसेंस  precedence|प्राथमिकता  prevalence|प्रचलन  sentence|वाक्य
"""
_ANCE_ENCE_BULK_2 = """
acceptance|स्वीकृति  admittance|प्रवेश  arrogance|अहंकार  conductance|चालकत्व
conveyance|वाहन  deliverance|मुक्ति  forbearance|सहनशीलता  furtherance|प्रोत्साहन
hindrance|बाधा  insurance|बीमा  observance|पालन  perseverance|दृढ़ता
reassurance|आश्वासन  remembrance|स्मरण  repentance|पश्चाताप  riddance|छुटकारा
acquiescence|सहमति  coalescence|एकीकरण  convalescence|स्वास्थ्य लाभ  efflorescence|खिलना
"""
_ANCE_ENCE_BULK_3 = """
clearance|साफ़ करना  compliance|अनुपालन  concordance|सहमति  continuance|निरंतरता
dominance|प्रभुत्व  grievance|शिकायत  observance|पालन  ordination|अभिषेक
perseverance|दृढ़ता  protuberance|उभार  purveyance|आपूर्ति  relevance|प्रासंगिकता
"""
_ANCE_ENCE_BULK_4 = """
appearance|उपस्थिति  assurance|आश्वासन  conductance|चालकत्व  defiance|अवज्ञा
disturbance|अशांति  endurance|सहनशीलता  insurance|बीमा  maintenance|रखरखाव
reassurance|आश्वासन  repentance|पश्चाताप  resistance|प्रतिरोध  vigilance|सतर्कता
"""


def _build_pattern_2():
    # -ism → der Xismus (German adds -us)
    en_hi = [
        ("tourism", "पर्यटन"), ("capitalism", "पूंजीवाद"), ("socialism", "समाजवाद"),
        ("communism", "साम्यवाद"), ("realism", "यथार्थवाद"), ("idealism", "आदर्शवाद"),
        ("nationalism", "राष्ट्रवाद"), ("journalism", "पत्रकारिता"), ("optimism", "आशावाद"),
        ("pessimism", "निराशावाद"), ("patriotism", "देशभक्ति"), ("feminism", "नारीवाद"),
        ("racism", "नस्लवाद"), ("terrorism", "आतंकवाद"), ("mechanism", "तंत्र"),
        ("organism", "जीव"), ("Buddhism", "बौद्ध धर्म"), ("Hinduism", "हिंदू धर्म"),
        ("Protestantism", "प्रोटेस्टेंटवाद"), ("Catholicism", "कैथोलिकवाद"),
        ("liberalism", "उदारवाद"), ("conservatism", "रूढ़िवाद"), ("imperialism", "साम्राज्यवाद"),
        ("materialism", "भौतिकवाद"), ("spiritualism", "अध्यात्मवाद"), ("criticism", "आलोचना"),
        ("skepticism", "संदेहवाद"), ("cynicism", "निंदकता"), ("heroism", "वीरता"),
        ("altruism", "परोपकार"), ("egoism", "अहंकार"), ("vandalism", "विनाश"),
        ("cannibalism", "नरभक्षण"), ("symbolism", "प्रतीकवाद"), ("surrealism", "अतियथार्थवाद"),
        ("expressionism", "अभिव्यक्तिवाद"), ("impressionism", "प्रभाववाद"),
        ("cubism", "क्यूबिज़्म"), ("modernism", "आधुनिकता"), ("postmodernism", "उत्तरआधुनिकता"),
        ("romanticism", "रोमांटिकता"), ("classicism", "शास्त्रीयता"), ("narcissism", "आत्ममोह"),
        ("fatalism", "भाग्यवाद"), ("determinism", "नियतिवाद"), ("empiricism", "अनुभववाद"),
        ("rationalism", "तर्कवाद"), ("humanism", "मानवतावाद"), ("colonialism", "उपनिवेशवाद"),
        ("environmentalism", "पर्यावरणवाद"), ("vegetarianism", "शाकाहार"), ("alcoholism", "शराबबंदी"),
        ("professionalism", "व्यावसायिकता"), ("enthusiasm", "उत्साह"), ("metabolism", "चयापचय"),
        ("catabolism", "विघटन"), ("anabolism", "उपचय"), ("embolism", "थ्रोम्बोसिस"),
        ("euphemism", "प्रेयोक्ति"), ("anachronism", "कालभ्रम"), ("solecism", "व्याकरण दोष"),
        ("sophism", "कुतर्क"), ("aneurysm", "धमनीविस्फार"), ("abysm", "गहराई"),
    ]
    bulk = _parse_bulk(_ISM_BULK) + _parse_bulk(_ISM_BULK_2)
    en_hi = en_hi + bulk
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        stem = en[:-3] if en.endswith("ism") else en  # remove "ism"
        de_stem = stem + "ismus"
        de = "der " + _cap_first(de_stem)
        out.append((de, en, hi))
    return out


def _parse_bulk(block, sep="  "):
    """Parse 'en|hi' tokens; tokens may be separated by sep (e.g. double space) or newlines."""
    out = []
    for line in block.strip().splitlines():
        for token in line.split(sep):
            token = token.strip()
            if not token or "|" not in token:
                continue
            en, hi = token.split("|", 1)
            out.append((en.strip(), hi.strip()))
    return out


# Bulk -ism (en|hi). German: der + stem + ismus.
_ISM_BULK = """
absurdism|असंगतिवाद  activism|सक्रियता  adventurism|साहसिकता  aestheticism|सौंदर्यवाद
africanism|अफ्रीकावाद  ageism|उम्रवाद  americanism|अमेरिकावाद  anarchism|अराजकतावाद
animism|आत्मावाद  antagonism|विरोध  asceticism|तपस्या  asianism|एशियावाद
atheism|नास्तिकता  atomism|परमाणुवाद  authoritarianism|सत्तावाद  autism|ऑटिज़्म
bilateralism|द्विपक्षीयता  bilingualism|द्विभाषावाद  biologism|जीववाद  bipolarism|द्विध्रुवीयता
botulism|बोटुलिज़्म  centralism|केंद्रवाद  chauvinism|जोश  collectivism|सामूहिकता
conformism|अनुरूपता  creationism|सृष्टिवाद  credentialism|प्रमाणवाद  cronyism|भाई-भतीजावाद
cynicism|निंदकता  darwinism|डार्विनवाद  despotism|तानाशाही
dogmatism|कट्टरता  dualism|द्वैतवाद  egalitarianism|समतावाद  elitism|कुलीनतावाद
emotionalism|भावुकता  empiricism|अनुभववाद  escapism|पलायनवाद  ethnocentrism|नस्ल केंद्रित
eurocentrism|यूरोकेंद्रवाद  existentialism|अस्तित्ववाद  expansionism|विस्तारवाद
extremism|चरमपंथ  fanaticism|कट्टरता  feudalism|सामंतवाद  formalism|औपचारिकता
functionalism|कार्यात्मकता  fundamentalism|कट्टरवाद  globalism|वैश्विकता
hedonism|सुखवाद  hedonism|भोगवाद  holism|समग्रवाद  humanism|मानवतावाद
hypnotism|सम्मोहन  idealism|आदर्शवाद  imperialism|साम्राज्यवाद  individualism|व्यक्तिवाद
industrialism|औद्योगिकता  intellectualism|बौद्धिकता  interactionism|अंतर्क्रियावाद
internationalism|अंतर्राष्ट्रवाद  interventionism|हस्तक्षेपवाद  isolationism|अलगाववाद
journalism|पत्रकारिता  legalism|कानूनवाद  leninism|लेनिनवाद  liberalism|उदारवाद
literalism|शाब्दिकता  magnetism|चुंबकत्व  malapropism|गलत शब्द प्रयोग  mannerism|शैली
marxism|मार्क्सवाद  materialism|भौतिकवाद  maximalism|अधिकतमवाद  meliorism|सुधारवाद
mentalism|मानसिकता  minimalism|न्यूनतमवाद  modernism|आधुनिकता  monetarism|मुद्रावाद
moralism|नैतिकता  multilateralism|बहुपक्षीयता  mysticism|रहस्यवाद  narcissism|आत्ममोह
nationalism|राष्ट्रवाद  naturalism|प्रकृतिवाद  nihilism|निराशावाद  nominalism|नामवाद
opportunism|अवसरवाद  optimism|आशावाद  orientalism|पूर्ववाद  pacifism|शांतिवाद
paganism|बहुदेववाद  particularism|विशेषवाद  paternalism|पितृसत्तात्मकता  patriotism|देशभक्ति
perfectionism|पूर्णतावाद  pessimism|निराशावाद  pluralism|बहुलवाद  populism|लोकलुभावनवाद
pragmatism|व्यावहारिकता  progressivism|प्रगतिवाद  protectionism|संरक्षणवाद  puritanism|शुद्धतावाद
racism|नस्लवाद  radicalism|कट्टरवाद  rationalism|तर्कवाद  realism|यथार्थवाद
regionalism|क्षेत्रवाद  relativism|सापेक्षवाद  romanticism|रोमांटिकता  sadism|सैडिज़्म
scientism|विज्ञानवाद  sectarianism|संप्रदायवाद  secularism|धर्मनिरपेक्षता  sensationalism|संवेदनावाद
sexism|लिंगवाद  shamanism|शैमनवाद  skepticism|संदेहवाद  socialism|समाजवाद
specialism|विशेषज्ञता  spiritualism|अध्यात्मवाद  statism|राज्यवाद  structuralism|संरचनावाद
subjectivism|व्यक्तिपरकता  surrealism|अतियथार्थवाद  symbolism|प्रतीकवाद  synergism|सहक्रियावाद
terrorism|आतंकवाद  totalitarianism|सर्वाधिकारवाद  tourism|पर्यटन  tribalism|जनजातिवाद
triumphalism|विजयवाद  unionism|संघवाद  universalism|सार्वभौमिकता
urbanism|शहरीकरण  utilitarianism|उपयोगितावाद  vandalism|विनाश  veganism|शाकाहार
vitalism|जीवनवाद  voluntarism|स्वैच्छिकता  voyeurism|दृष्टि काम  vulgarism|अश्लीलता
"""

# Bulk -ity (en|hi). German: die + stem + ität/tät.
_ITY_BULK = """
ability|क्षमता  activity|गतिविधि  adaptability|अनुकूलनशीलता  adversity|विपत्ति
ambiguity|अस्पष्टता  amenity|सुविधा  antiquity|प्राचीनता  anxiety|चिंता
authenticity|प्रामाणिकता  authority|अधिकार  availability|उपलब्धता  brutality|क्रूरता
capacity|क्षमता  celebrity|प्रसिद्धि  clarity|स्पष्टता  commodity|वस्तु
community|समुदाय  compatibility|अनुकूलता  complexity|जटिलता  connectivity|संयोजन
creativity|रचनात्मकता  credibility|विश्वसनीयता  curiosity|जिज्ञासा  density|घनत्व
diversity|विविधता  durability|टिकाऊपन  electricity|बिजली  equality|समानता
facility|सुविधा  formality|औपचारिकता  fragility|नाजुकता  generality|सामान्यता
humanity|मानवता  humidity|नमी  identity|पहचान  immunity|प्रतिरक्षा
integrity|अखंडता  intensity|तीव्रता  locality|स्थान  longevity|दीर्घायु
maturity|परिपक्वता  mobility|गतिशीलता  morality|नैतिकता  necessity|आवश्यकता
neutrality|तटस्थता  normality|सामान्यता  objectivity|निष्पक्षता  opportunity|अवसर
personality|व्यक्तित्व  popularity|लोकप्रियता  possibility|संभावना  priority|प्राथमिकता
probability|संभावना  productivity|उत्पादकता  prosperity|समृद्धि  quality|गुणवत्ता
quantity|मात्रा  reality|वास्तविकता  responsibility|जिम्मेदारी  rigidity|कठोरता
security|सुरक्षा  sensitivity|संवेदनशीलता  severity|गंभीरता  similarity|समानता
simplicity|सरलता  sincerity|ईमानदारी  society|समाज  solidarity|एकजुटता
stability|स्थिरता  subjectivity|व्यक्तिपरकता  superiority|श्रेष्ठता  sustainability|टिकाऊपन
utility|उपयोगिता  validity|वैधता  variety|विविधता  velocity|वेग  vitality|जीवन शक्ति
"""

# Bulk -ic (en|hi). German: -isch (adjective).
_IC_BULK = """
academic|शैक्षणिक  aerodynamic|वायुगतिक  allergic|एलर्जी  alphabetic|वर्णमाला
analytic|विश्लेषणात्मक  anatomic|शारीरिक  aristocratic|अभिजात  aromatic|सुगंधित
artistic|कलात्मक  asymmetric|असममित  athletic|ऐथलेटिक  atmospheric|वायुमंडलीय
atomic|परमाणु  automatic|स्वचालित  ballistic|बैलिस्टिक  basic|मूलभूत
biologic|जैविक  bureaucratic|नौकरशाही  catalytic|उत्प्रेरक  chaotic|अराजक
characteristic|विशेषता  chromatic|रंग  cinematic|सिनेमाई  civic|नागरिक
classic|क्लासिक  climatic|जलवायु  clinic|क्लिनिक  comic|कॉमिक
cosmic|वैश्विक  cyclic|चक्रीय  democratic|लोकतांत्रिक  demographic|जनसांख्यिक
diabetic|मधुमेह  diagnostic|नैदानिक  dialectic|द्वंद्वात्मक  diplomatic|कूटनीतिक
domestic|घरेलू  dramatic|नाटकीय  dynamic|गतिशील  eccentric|विलक्षण
economic|आर्थिक  elastic|लोचदार  electric|बिजली  electronic|इलेक्ट्रॉनिक
emphatic|जोरदार  endemic|स्थानिक  energetic|ऊर्जावान  epic|महाकाव्य
epidemic|महामारी  ethnic|जातीय  euphemistic|प्रेयोक्तिपूर्ण  exotic|विदेशी
explicit|स्पष्ट  fantastic|शानदार  genetic|आनुवंशिक  geographic|भौगोलिक
geometric|ज्यामितीय  heroic|वीर  historic|ऐतिहासिक  holistic|समग्र
hydraulic|जल  hyperbolic|अतिशयोक्तिपूर्ण  hypnotic|सम्मोहक  idiomatic|मुहावरेदार
impractical|अव्यावहारिक  ironic|विडंबनापूर्ण  Islamic|इस्लामी  kinetic|गतिज
linguistic|भाषाई  logic|तर्क  magnetic|चुंबकीय  majestic|शानदार
metabolic|चयापचय  metallic|धात्विक  microscopic|सूक्ष्म  monastic|मठवासी
neurotic|न्यूरोटिक  numeric|संख्यात्मक  organic|जैविक  panoramic|पैनोरामा
pathetic|दयनीय  patriotic|देशभक्तिपूर्ण  periodic|आवधिक  phonetic|ध्वन्यात्मक
photographic|फोटोग्राफिक  plastic|प्लास्टिक  poetic|काव्यात्मक  politic|राजनीतिक
practical|व्यावहारिक  prophetic|भविष्यसूचक  prosaic|गद्यात्मक  psychiatric|मनोरोग
public|सार्वजनिक  realistic|यथार्थवादी  romantic|रोमांटिक  rustic|ग्रामीण
sarcastic|व्यंग्यात्मक  scenic|प्राकृतिक  schematic|योजनाबद्ध  semantic|अर्थगत
specific|विशिष्ट  spherical|गोलाकार  static|स्थिर  strategic|रणनीतिक
sympathetic|सहानुभूतिपूर्ण  synthetic|सिंथेटिक  systematic|व्यवस्थित  tactical|सामरिक
technical|तकनीकी  thematic|विषयगत  theoretic|सैद्धांतिक  tragic|दुखद
typic|विशिष्ट  volcanic|ज्वालामुखी
"""

# Bulk -ive (en|hi). German: -iv.
_IVE_BULK = """
abusive|अपमानजनक  adaptive|अनुकूली  additive|योजक  adhesive|चिपकने वाला
administrative|प्रशासनिक  affirmative|सकारात्मक  alternative|विकल्प  anticipative|पूर्वानुमान
appreciative|कृतज्ञ  argumentative|तर्कपूर्ण  assertive|मुखर  associative|साहचर्य
attractive|आकर्षक  authoritative|आधिकारिक  collaborative|सहयोगी  collective|सामूहिक
combative|लड़ाकू  commemorative|स्मारक  communicative|संचारी  comparative|तुलनात्मक
competitive|प्रतिस्पर्धी  comprehensive|व्यापक  compulsive|बाध्यकारी  conclusive|निर्णायक
conductive|सुचालक  conservative|रूढ़िवादी  constructive|रचनात्मक  contemplative|चिंतनशील
cooperative|सहकारी  corrective|सुधारात्मक  creative|रचनात्मक  cumulative|संचयी
decorative|सजावटी  defensive|रक्षात्मक  demonstrative|प्रदर्शनात्मक  descriptive|वर्णनात्मक
destructive|विनाशकारी  digestive|पाचन  distributive|वितरणात्मक  effective|प्रभावी
elective|वैकल्पिक  evocative|भावपूर्ण  excessive|अत्यधिक  exclusive|विशेष
executive|कार्यकारी  exhaustive|संपूर्ण  expansive|विस्तारशील  expensive|महंगा
explosive|विस्फोटक  expressive|अभिव्यक्तिपूर्ण  extensive|व्यापक  figurative|आलंकारिक
generative|उत्पादक  imaginative|कल्पनाशील  imperative|अनिवार्य  impressive|प्रभावशाली
inclusive|समावेशी  indicative|सूचक  inductive|आगमनात्मक  informative|सूचनाप्रद
inquisitive|जिज्ञासु  instructive|शिक्षाप्रद  intensive|गहन  interactive|पारस्परिक
intuitive|सहजज्ञानी  invasive|आक्रामक  inventive|अन्वेषी  iterative|पुनरावृत्त
legislative|विधान  manipulative|हेराफेरी  massive|बड़ा  narrative|कथात्मक
negative|नकारात्मक  nominative|नामिक  nutritive|पोषक  objective|वस्तुनिष्ठ
offensive|आपत्तिजनक  operative|कार्यात्मक  passive|निष्क्रिय  persuasive|सम्मोहक
possessive|अधिकारात्मक  preventive|निवारक  primitive|आदिम  productive|उत्पादक
progressive|प्रगतिशील  prohibitive|निषेधात्मक  prospective|संभावित  protective|सुरक्षात्मक
receptive|ग्रहणशील  reflective|चिंतनशील  regenerative|पुनर्योजी  relative|रिश्तेदार
representative|प्रतिनिधि  restrictive|प्रतिबंधात्मक  retrospective|पूर्वव्यापी  selective|चयनात्मक
sensitive|संवेदनशील  speculative|अटकलबाज  subjective|व्यक्तिपरक  successive|क्रमिक
supportive|सहायक  suggestive|सुझावपूर्ण  superlative|उत्तम  supportive|सहायक
"""

# Bulk -ment (en|hi). German: das (same or -ment).
_MENT_BULK = """
achievement|उपलब्धि  acknowledgment|स्वीकृति  adjustment|समायोजन  advertisement|विज्ञापन
agreement|समझौता  alignment|संरेखण  allotment|आवंटन  amendment|संशोधन
announcement|घोषणा  appointment|नियुक्ति  assessment|मूल्यांकन  assignment|असाइनमेंट
attachment|संलग्नक  attainment|प्राप्ति  commitment|प्रतिबद्धता  complement|पूरक
deployment|तैनाती  development|विकास  disagreement|असहमति  displacement|विस्थापन
document|दस्तावेज़  element|तत्व  embarrassment|शर्मिंदगी  embodiment|अवतार
employment|रोजगार  enforcement|प्रवर्तन  engagement|सगाई  enhancement|सुधार
enrollment|नामांकन  entertainment|मनोरंजन  environment|पर्यावरण  equipment|उपकरण
establishment|स्थापना  excitement|उत्तेजना  experiment|प्रयोग  fragment|टुकड़ा
government|सरकार  improvement|सुधार  installment|किस्त  instrument|उपकरण
investment|निवेश  management|प्रबंधन  measurement|माप  medication|दवा
moment|क्षण  movement|आंदोलन  parliament|संसद  payment|भुगतान
placement|प्लेसमेंट  punishment|सजा  replacement|प्रतिस्थापन  requirement|आवश्यकता
settlement|समझौता  shipment|भेजना  statement|बयान  treatment|उपचार
"""

# Bulk -tion/-sion (en|hi). German: die + same word. Append to pattern_3.
_TION_BULK = """
abbreviation|संक्षिप्ति  absorption|अवशोषण  abstraction|अमूर्तता  acceleration|त्वरण
accommodation|आवास  accompaniment|संगत  accusation|आरोप  activation|सक्रियण
adaptation|अनुकूलन  admiration|प्रशंसा  adoption|गोद लेना  adoption|दत्तक ग्रहण
affection|स्नेह  affiliation|संबंध  affirmation|पुष्टि  aggregation|समुच्चय
aggression|आक्रामकता  agitation|उत्तेजना  allocation|आवंटन  alteration|परिवर्तन
alternation|बारी  amplification|प्रवर्धन  animation|एनिमेशन  annexation|अधिग्रहण
anticipation|प्रत्याशा  appreciation|सराहना  appropriation|विनियोग  arbitration|मध्यस्थता
articulation|उच्चारण  aspiration|आकांक्षा  assassination|हत्या  assimilation|आत्मसात
association|संघ  assumption|धारणा  attachment|लगाव  attainment|प्राप्ति
attention|ध्यान  attribution|आरोपण  authentication|प्रमाणीकरण  authorization|अधिकार
automation|स्वचालन  automation|ऑटोमेशन  calculation|गणना  calibration|अंशांकन
cancellation|रद्दीकरण  cultivation|खेती  celebration|उत्सव  circulation|संचलन
classification|वर्गीकरण  collaboration|सहयोग  collection|संग्रह  collision|टक्कर
combination|संयोजन  combustion|दहन  commendation|प्रशंसा  commentary|टिप्पणी
commission|आयोग  communication|संचार  compensation|क्षतिपूर्ति  compilation|संकलन
completion|पूर्णता  complication|जटिलता  composition|रचना  comprehension|समझ
compression|संपीड़न  computation|गणना  concentration|एकाग्रता  conception|धारणा
conclusion|निष्कर्ष  condemnation|निंदा  conditioning|अनुकूलन  conduction|चालन
confirmation|पुष्टि  confrontation|टकराव  congestion|भीड़  conjunction|संयोजन
connection|संबंध  conquest|विजय  conscience|अंतरात्मा  consciousness|चेतना
consequence|परिणाम  conservation|संरक्षण  consideration|विचार  consolidation|समेकन
conspiracy|षड्यंत्र  constitution|संविधान  construction|निर्माण  consultation|परामर्श
consumption|उपभोग  contamination|दूषण  contemplation|चिंतन  contention|विवाद
continuation|निरंतरता  contraction|संकुचन  contribution|योगदान  convention|सम्मेलन
conversation|बातचीत  conversion|रूपांतरण  conviction|दोषसिद्धि  coordination|समन्वय
corporation|निगम  correction|सुधार  correlation|सहसंबंध  corruption|भ्रष्टाचार
creation|रचना  cultivation|खेती  declaration|घोषणा  deduction|कटौती
definition|परिभाषा  delegation|प्रतिनिधिमंडल  deliberation|विचार  delivery|वितरण
demonstration|प्रदर्शन  denomination|संप्रदाय  description|वर्णन  designation|पदनाम
destination|गंतव्य  destruction|विनाश  detection|पता लगाना  determination|निर्धारण
deviation|विचलन  digestion|पाचन  dimension|आयाम  direction|दिशा
disposition|प्रवृत्ति  distribution|वितरण  documentation|दस्तावेज़ीकरण  domination|वर्चस्व
donation|दान  duration|अवधि  education|शिक्षा  elevation|ऊंचाई  elimination|उन्मूलन
emotion|भावना  encryption|एन्क्रिप्शन  equation|समीकरण  erosion|कटाव
evaluation|मूल्यांकन  evolution|विकास  examination|परीक्षा  exception|अपवाद
exclamation|विस्मयादिबोधक  execution|निष्पादन  exhibition|प्रदर्शनी  expansion|विस्तार
expectation|उम्मीद  expedition|अभियान  experimentation|प्रयोग  explanation|व्याख्या
exploration|अन्वेषण  explosion|विस्फोट  expression|अभिव्यक्ति  extension|विस्तार
fabrication|निर्माण  fascination|मोह  federation|संघ  fermentation|किण्वन
filtration|छानना  fixation|स्थिरीकरण  formation|निर्माण  formulation|सूत्रीकरण
foundation|नींव  fragmentation|विखंडन  generation|पीढ़ी  germination|अंकुरण
graduation|स्नातक  gratification|संतुष्टि  gravitation|गुरुत्व  identification|पहचान
illusion|भ्रम  imagination|कल्पना  imitation|नकल  immigration|आप्रवास
implementation|कार्यान्वयन  implication|निहितार्थ  imposition|थोपना  impression|छाप
improvisation|तात्कालिकता  inclination|झुकाव  incorporation|निगमन  indication|संकेत
indication|इशारा  infection|संक्रमण  inflation|मुद्रास्फीति  information|जानकारी
innovation|नवाचार  inspiration|प्रेरणा  installation|स्थापना  institution|संस्थान
instruction|निर्देश  integration|एकीकरण  intention|इरादा  interaction|पारस्परिक क्रिया
interpretation|व्याख्या  interrogation|पूछताछ  intervention|हस्तक्षेप  introduction|परिचय
intuition|अंतर्ज्ञान  invention|आविष्कार  invitation|निमंत्रण  irrigation|सिंचाई
isolation|अलगाव  iteration|पुनरावृत्ति  justification|औचित्य  legislation|कानून
liberation|मुक्ति  limitation|सीमा  liquidation|परिसमापन  location|स्थान
magnification|आवर्धन  manifestation|अभिव्यक्ति  manipulation|हेराफेरी  migration|प्रवास
modification|संशोधन  motivation|प्रेरणा  multiplication|गुणा  narration|कथन
navigation|नौवहन  negotiation|बातचीत  nomination|नामांकन  notification|सूचना
nutrition|पोषण  obligation|दायित्व  observation|अवलोकन  operation|ऑपरेशन
opposition|विरोध  optimization|अनुकूलन  option|विकल्प  orientation|अभिविन्यास
oscillation|दोलन  participation|भागीदारी  partition|विभाजन  perception|धारणा
perfection|पूर्णता  permission|अनुमति  permutation|क्रमचय  persecution|उत्पीड़न
perspiration|पसीना  persuasion|समझाना  perturbation|विक्षोभ  petition|याचिका
plantation|बागान  polarization|ध्रुवीकरण  pollination|परागण  population|जनसंख्या
preparation|तैयारी  preservation|संरक्षण  presentation|प्रस्तुति  preservation|संरक्षण
prevention|रोकथाम  production|उत्पादन  projection|प्रक्षेपण  proliferation|प्रसार
promotion|पदोन्नति  propagation|प्रसार  proportion|अनुपात  proposition|प्रस्ताव
protection|सुरक्षा  qualification|योग्यता  quotation|उद्धरण  radiation|विकिरण
realization|प्राप्ति  reception|स्वागत  recognition|मान्यता  recommendation|सिफारिश
recreation|मनोरंजन  reduction|कमी  reflection|प्रतिबिंब  regeneration|पुनर्जनन
registration|पंजीकरण  regulation|नियमन  rehabilitation|पुनर्वास  relation|संबंध
relaxation|आराम  repetition|दोहराव  representation|प्रतिनिधित्व  reproduction|प्रजनन
reservation|आरक्षण  resignation|इस्तीफा  resolution|संकल्प  respiration|श्वसन
restoration|बहाली  restriction|प्रतिबंध  revelation|रहस्योद्घाटन  revolution|क्रांति
rotation|घूर्णन  sanitation|स्वच्छता  saturation|संतृप्ति  satisfaction|संतुष्टि
selection|चयन  separation|अलगाव  simulation|सिमुलेशन  situation|स्थिति
solution|समाधान  specification|विनिर्देश  specification|निर्दिष्टीकरण  stimulation|उत्तेजना
substitution|प्रतिस्थापन  succession|उत्तराधिकार  suggestion|सुझाव  summation|योग
supervision|पर्यवेक्षण  suppression|दमन  suspension|निलंबन  taxation|कराधान
temptation|प्रलोभन  tension|तनाव  termination|समाप्ति  transformation|रूपांतरण
translation|अनुवाद  transmission|संचरण  transportation|परिवहन  vaccination|टीकाकरण
validation|सत्यापन  variation|विविधता  vegetation|वनस्पति  ventilation|वेंटिलेशन
verification|सत्यापन  vibration|कंपन  violation|उल्लंघन  vision|दृष्टि
"""

# Extra bulk -tion: NEW words (not in TION_BULK) for 10k. German: die + Capitalize(en).
_TION_BULK_2 = """
abstraction|अमूर्तता  abduction|अपहरण  ablution|स्नान  abolition|उन्मूलन  abstention|परहेज
accreditation|मान्यता  adulation|चापलूसी  affectation|दिखावा  affliction|कष्ट  alienation|अलगाव
alignment|संरेखण  allegation|आरोप  alleviation|राहत  amalgamation|विलय  amelioration|सुधार
amortization|ऋण शोधन  annihilation|विनाश  annotation|टिप्पणी  annunciation|घोषणा  antiquation|पुराना
appellation|संबोधन  apprehension|आशंका  approximation|अनुमान  attestation|प्रमाणन  augmentation|वृद्धि
aversion|घृणा  balkanization|विभाजन  beatification|धन्य घोषणा  bifurcation|द्विभाजन  canonization|संत घोषणा
capacitation|सक्षमता  capitulation|आत्मसमर्पण  castigation|आलोचना  causation|कारण  centrifugation|अपकेंद्रण
certification|प्रमाणन  cessation|समाप्ति  circumcision|खतना  circumvention|दरकिनार  clarification|स्पष्टीकरण
coagulation|जमाव  coeducation|सहशिक्षा  coercion|बल प्रयोग  cogitation|विचार  communization|समाजीकरण
compaction|संघनन  commodification|वस्तुकरण  compulsion|मजबूरी  concession|रियायत  confession|इकबाल
consensus|सहमति  contrition|पश्चाताप  culmination|पराकाष्ठा  defection|पलायन  deformation|विरूपण
degeneration|अध:पतन  deletion|मिटाना  delineation|रूपरेखा  demarcation|सीमांकन  denunciation|निंदा
deportation|निर्वासन  deposition|बयान  depreciation|मूल्यह्रास  deprivation|वंचना  derivation|व्युत्पत्ति
deterioration|बिगड़ना  detonation|विस्फोटन  devotion|भक्ति  dilution|तनुकरण  diminution|कमी
disablement|अक्षमता  disagreement|असहमति  disappearance|गायब  disarmament|निरस्त्रीकरण  discontinuation|बंद
disembarkation|उतराई  disinfection|कीटाणुनाशन  disintegration|विघटन  dismissal|बर्खास्तगी  dispersion|फैलाव
disproportion|असंतुलन  disruption|अवरोध  dissection|विच्छेदन  dissolution|विघटन  diversification|विविधीकरण
divination|भविष्यवाणी  emulation|अनुकरण  enumeration|गणना  eradication|उन्मूलन  eruption|विस्फोट
escalation|वृद्धि  evacuation|खाली करना  evaporation|वाष्पीकरण  excavation|खुदाई  exemption|छूट
exhaustion|थकान  exploitation|शोषण  exportation|निर्यात  exposition|प्रदर्शनी  extraction|निष्कर्षण
facilitation|सुविधा  fertilization|निषेचन  flotation|तैराव  frustration|निराशा  globalization|वैश्वीकरण
glorification|गौरव  habitation|निवास  hesitation|संकोच  illumination|रोशनी  incarceration|कैद
incarnation|अवतार  incrimination|अभियोग  indemnification|क्षतिपूर्ति  indignation|क्रोध  induction|प्रेरण
infusion|अर्क  ingestion|निगलना  initiation|शुरुआत  inoculation|टीकाकरण  inscription|शिलालेख
insertion|सम्मिलन  inspection|निरीक्षण  instantiation|उदाहरण  interjection|विस्मयादिबोधक  interruption|रुकावट
intersection|चौराहा  invocation|आह्वान  irritation|जलन  jurisdiction|अधिकार क्षेत्र  juxtaposition|साथ रखना
lactation|स्तनपान  lamentation|विलाप  litigation|मुकदमेबाजी  lubrication|स्नेहन  mineralization|खनिजीकरण
minimization|कमी  modulation|मॉड्यूलन  negation|निषेध  nourishment|पोषण  occupation|व्यवसाय
orchestration|ऑर्केस्ट्रेशन  oxidation|ऑक्सीकरण  perforation|छिद्रण  perseverance|दृढ़ता  persistence|हठ
possession|कब्जा  precipitation|वर्षा  precision|सटीकता  predisposition|प्रवृत्ति  presumption|धारणा
prosecution|अभियोग  purification|शुद्धिकरण  quantification|मात्रात्मक  reconciliation|सुलह  refraction|अपवर्तन
rejection|अस्वीकृति  release|रिहाई  reputation|प्रतिष्ठा  resurrection|पुनरुत्थान  retention|धारण
sanction|प्रतिबंध  sedation|शामक  sensation|संवेदना  sequestration|जब्त  speculation|अटकल
subscription|सदस्यता  superposition|अध्यारोपण  sustenance|जीविका  synchronization|तालमेल  synthesis|संश्लेषण
valuation|मूल्यांकन  vocation|पेशा
"""

# More -tion (BULK_3) for 10k.
_TION_BULK_3 = """
acclamation|जयघोष  admonition|चेतावनी  advection|अनुवहन  advocation|वकालत
aeration|वातन  approbation|अनुमोदन  argumentation|तर्क  ascription|आरोपण
aspersion|बदनामी  assignation|नियतन  attenuation|क्षीणन  calcification|कैल्सीकरण
capitalization|पूंजीकरण  carbonation|कार्बोनेशन  categorization|वर्गीकरण  centralization|केंद्रीकरण
codification|संहिताकरण  conscription|भर्ती  contemplation|चिंतन  contraception|गर्भनिरोध
contraption|उपकरण  contravention|उल्लंघन  convection|संवहन  convening|आह्वान
correction|सुधार  correlation|सहसंबंध  decompression|विघटन  deflation|अपस्फीति
deforestation|वनोन्मूलन  degeneration|अध:पतन  demotion|पदावनति  demystification|रहस्योद्घाटन
denationalization|विभाजन  denotation|अर्थ  depopulation|जनसंख्या कमी  deputation|प्रतिनिधिमंडल
desalination|लवणहरण  desegregation|एकीकरण  desolation|उजाड़  detoxification|विषहरण
digitization|डिजिटलीकरण  disambiguation|स्पष्टीकरण  discontinuation|समाप्ति  disinfection|कीटाणुनाशन
disqualification|अयोग्यता  dissemination|प्रसार  distillation|आसवन  diversification|विविधीकरण
documentation|दस्तावेज़ीकरण  domestication|पालतू बनाना  dramatization|नाटकीयता  electrification|विद्युतीकरण
elimination|उन्मूलन  elongation|लंबाई  emancipation|मुक्ति  emigration|उत्प्रवास
emulation|अनुकरण  equalization|समीकरण  equivocation|अस्पष्टता  eradication|उन्मूलन
evaporation|वाष्पीकरण  exacerbation|बिगाड़  exaggeration|अतिशयोक्ति  excavation|खुदाई
excommunication|बहिष्कार  exoneration|दोषमुक्ति  expatriation|निर्वासन  experimentation|प्रयोग
extermination|विनाश  extrapolation|बहिर्वेशन  fabrication|निर्माण  factorization|गुणनखंडन
falsification|जालसाजी  fermentation|किण्वन  fertilization|निषेचन  formalization|औपचारिकता
fortification|किलेबंदी  fossilization|जीवाश्मीकरण  fractionation|विभाजन  fragmentation|विखंडन
generalization|सामान्यीकरण  gentrification|उत्थान  germination|अंकुरण  globalization|वैश्वीकरण
gratification|संतुष्टि  harmonization|सामंजस्य  hospitalization|अस्पताल में भर्ती  humanization|मानवीकरण
hybridization|संकरण  hydration|जलयोजन  hydrogenation|हाइड्रोजनीकरण  illumination|रोशनी
illustration|चित्रण  immunization|प्रतिरक्षण  impersonation|अनुकरण  impoverishment|गरीबी
inauguration|उद्घाटन  incarceration|कैद  incorporation|निगमन  indemnification|क्षतिपूर्ति
indignation|क्रोध  industrialization|औद्योगिकीकरण  infatuation|मोह  infestation|संक्रमण
inflammation|सूजन  inflation|मुद्रास्फीति  information|जानकारी  infraction|उल्लंघन
ingestion|निगलना  inhalation|साँस  initialization|प्रारंभ  inoculation|टीकाकरण
inscription|शिलालेख  insertion|सम्मिलन  inspection|निरीक्षण  inspiration|प्रेरणा
institutionalization|संस्थानीकरण  instrumentation|उपकरण  insurrection|विद्रोह  integration|एकीकरण
intensification|तीव्रता  internalization|आंतरिकरण  interrogation|पूछताछ  intoxication|नशा
introduction|परिचय  inundation|बाढ़  invocation|आह्वान  ionization|आयनीकरण
irrigation|सिंचाई  irritation|जलन  isolation|अलगाव  iteration|पुनरावृत्ति
legalization|कानूनीकरण  legitimization|वैधता  liberalization|उदारीकरण  liquidation|परिसमापन
localization|स्थानीकरण  magnification|आवर्धन  manifestation|अभिव्यक्ति  manipulation|हेराफेरी
marginalization|हाशियाकरण  materialization|मूर्त रूप  maximization|अधिकतमीकरण  mechanization|यंत्रीकरण
meditation|ध्यान  memorization|याद  migration|प्रवास  militarization|सैन्यीकरण
minimization|कमी  mobilization|जुटान  modernization|आधुनिकीकरण  modification|संशोधन
modulation|मॉड्यूलन  multiplication|गुणा  mutation|उत्परिवर्तन  narration|कथन
nationalization|राष्ट्रीयकरण  naturalization|प्राकृतिकरण  navigation|नौवहन  negation|निषेध
negotiation|बातचीत  neutralization|निष्प्रभावीकरण  normalization|सामान्यीकरण  notification|सूचना
nullification|रद्द  numeration|गणना  obfuscation|अस्पष्टता  obligation|दायित्व
observation|अवलोकन  obstruction|अवरोध  occupation|व्यवसाय  optimization|अनुकूलन
orchestration|ऑर्केस्ट्रेशन  organization|संगठन  orientation|अभिविन्यास  oscillation|दोलन
ossification|अस्थिकरण  ostracization|बहिष्कार  overpopulation|जनसंख्या विस्फोट  oxidation|ऑक्सीकरण
pacification|शांतिस्थापन  pagination|पृष्ठांकन  participation|भागीदारी  pasteurization|पाश्चरीकरण
penetration|भेदन  perception|धारणा  perfection|पूर्णता  perforation|छिद्रण
personalization|व्यक्तिकरण  persuasion|समझाना  perturbation|विक्षोभ  polarization|ध्रुवीकरण
politicization|राजनीतिकरण  polymerization|बहुलकरण  popularization|लोकप्रियता  precipitation|वर्षा
predestination|पूर्वनियति  predication|विधेय  predisposition|प्रवृत्ति  prefabrication|पूर्वनिर्माण
preservation|संरक्षण  privatization|निजीकरण  probation|परिवीक्षा  procrastination|टालमटोल
proliferation|प्रसार  promulgation|घोषणा  propagation|प्रसार  proportionality|आनुपातिकता
proposition|प्रस्ताव  prosecution|अभियोग  proselytization|धर्मपरिवर्तन  purification|शुद्धिकरण
quantification|मात्रात्मक  ratification|अनुसमर्थन  rationalization|युक्तिसंगत  reclamation|पुनर्प्राप्ति
reclassification|पुनर्वर्गीकरण  reclamation|दावा  recombination|पुनर्संयोजन  reconfiguration|पुनर्विन्यास
recrimination|प्रत्यारोप  rectification|सुधार  redecoration|पुनर्सज्जा  redistribution|पुनर्वितरण
reduction|कमी  reeducation|पुनशिक्षा  reforestation|पुनर्वनीकरण  reformation|सुधार
refrigeration|शीतलन  regeneration|पुनर्जनन  regimentation|अनुशासन  regurgitation|उल्टी
rehabilitation|पुनर्वास  reification|वस्तुकरण  reimplementation|पुनर्कार्यान्वयन  reintegration|पुनःएकीकरण
reinterpretation|पुनर्व्याख्या  reinvention|पुनर्आविष्कार  rejuvenation|कायाकल्प  remediation|उपचार
remuneration|पारिश्रमिक  renunciation|त्याग  reorganization|पुनर्गठन  repatriation|प्रत्यावर्तन
replication|प्रतिकृति  repositioning|पुनःस्थिति  representation|प्रतिनिधित्व  repression|दमन
reproduction|प्रजनन  repudiation|अस्वीकृति  requisition|अधिग्रहण  resubmission|पुनर्समर्पण
resurrection|पुनरुत्थान  retaliation|प्रतिशोध  retardation|मंदन  retraction|वापसी
reunification|पुनर्मिलन  revaluation|पुनर्मूल्यांकन  reversion|वापसी  revitalization|पुनरोद्धार
revitalization|पुनर्जीवन  ritualization|रीतिकरण  romanticization|रोमांटिकरण  routinization|दिनचर्या
sanctification|पवित्रता  sanitization|स्वच्छता  saturation|संतृप्ति  scarring|निशान
scenario|परिदृश्य  schematization|योजनाकरण  secularization|धर्मनिरपेक्षता  sedimentation|अवसादन
segmentation|खंडन  sensitization|संवेदीकरण  serialization|क्रमबद्धता  socialization|समाजीकरण
specialization|विशेषज्ञता  specification|विनिर्देश  stabilization|स्थिरीकरण  standardization|मानकीकरण
stigmatization|कलंकन  stratification|स्तरीकरण  subordination|अधीनता  subsidization|सब्सिडी
substitution|प्रतिस्थापन  suffocation|दम घुटना  summarization|सारांश  superimposition|अध्यारोपण
supervision|पर्यवेक्षण  supplementation|पूरक  synchronization|तालमेल  systematization|व्यवस्थापन
temporization|टालमटोल  territorialization|क्षेत्रीकरण  theorization|सिद्धांतीकरण  tokenization|टोकनन
totalization|कुलीकरण  traumatization|आघात  trivialization|तुच्छीकरण  typification|प्रतीकीकरण
unification|एकीकरण  unionization|संघीकरण  urbanization|शहरीकरण  utilization|उपयोग
vaccination|टीकाकरण  validation|सत्यापन  valorization|मूल्यांकन  vaporization|वाष्पीकरण
variation|विविधता  vectorization|सदिशीकरण  verification|सत्यापन  victimization|पीड़ित
vilification|बदनामी  visualization|दृश्यीकरण  vulgarization|लोकप्रियता  westernization|पश्चिमीकरण
"""

# More -ism (BULK_2).
_ISM_BULK_2 = """
absolutism|निरंकुशता  activism|सक्रियता  adventurism|साहस  aestheticism|सौंदर्यवाद
altruism|परोपकार  anarchism|अराजकता  animism|आत्मावाद  antagonism|विरोध
asceticism|तपस्या  astigmatism|दृष्टि दोष  atheism|नास्तिकता  atomism|परमाणुवाद
authoritarianism|सत्तावाद  autism|ऑटिज़्म  barbarism|बर्बरता  capitalism|पूंजीवाद
chauvinism|जोश  collectivism|सामूहिकता  colonialism|उपनिवेशवाद  commercialism|व्यावसायिकता
communism|साम्यवाद  conformism|अनुरूपता  conservatism|रूढ़िवाद  consumerism|उपभोक्तावाद
corporatism|निगमवाद  cronyism|भाई-भतीजावाद  cynicism|निंदकता  despotism|तानाशाही
determinism|नियतिवाद  dogmatism|कट्टरता  dualism|द्वैतवाद  dynamism|गतिशीलता
egalitarianism|समतावाद  elitism|कुलीनतावाद  empiricism|अनुभववाद  environmentalism|पर्यावरणवाद
escapism|पलायनवाद  ethnocentrism|नस्लकेंद्रित  euphemism|प्रेयोक्ति  evangelism|प्रचार
exceptionalism|विशिष्टता  existentialism|अस्तित्ववाद  expansionism|विस्तारवाद  extremism|चरमपंथ
fatalism|भाग्यवाद  feudalism|सामंतवाद  formalism|औपचारिकता  fundamentalism|कट्टरवाद
globalism|वैश्विकता  hedonism|सुखवाद  holism|समग्रवाद  humanism|मानवतावाद
hypnotism|सम्मोहन  idealism|आदर्शवाद  imperialism|साम्राज्यवाद  individualism|व्यक्तिवाद
industrialism|औद्योगिकता  intellectualism|बौद्धिकता  internationalism|अंतर्राष्ट्रवाद
interventionism|हस्तक्षेपवाद  isolationism|अलगाववाद  jingoism|कट्टर राष्ट्रवाद  journalism|पत्रकारिता
liberalism|उदारवाद  literalism|शाब्दिकता  magnetism|चुंबकत्व  mannerism|शैली
marxism|मार्क्सवाद  materialism|भौतिकवाद  maximalism|अधिकतमवाद  mechanism|तंत्र
minimalism|न्यूनतमवाद  modernism|आधुनिकता  monetarism|मुद्रावाद  moralism|नैतिकता
multilateralism|बहुपक्षीयता  mysticism|रहस्यवाद  narcissism|आत्ममोह  nationalism|राष्ट्रवाद
naturalism|प्रकृतिवाद  nihilism|निराशावाद  nominalism|नामवाद  objectivism|वस्तुवाद
opportunism|अवसरवाद  optimism|आशावाद  orientalism|पूर्ववाद  pacifism|शांतिवाद
paganism|बहुदेववाद  paternalism|पितृसत्तात्मकता  patriotism|देशभक्ति  perfectionism|पूर्णतावाद
pessimism|निराशावाद  pluralism|बहुलवाद  populism|लोकलुभावनवाद  pragmatism|व्यावहारिकता
progressivism|प्रगतिवाद  protectionism|संरक्षणवाद  puritanism|शुद्धतावाद  racism|नस्लवाद
radicalism|कट्टरवाद  rationalism|तर्कवाद  realism|यथार्थवाद  regionalism|क्षेत्रवाद
relativism|सापेक्षवाद  romanticism|रोमांटिकता  sadism|सैडिज़्म  scientism|विज्ञानवाद
sectarianism|संप्रदायवाद  secularism|धर्मनिरपेक्षता  sensationalism|संवेदनावाद  sexism|लिंगवाद
shamanism|शैमनवाद  skepticism|संदेहवाद  socialism|समाजवाद  specialism|विशेषज्ञता
spiritualism|अध्यात्मवाद  statism|राज्यवाद  structuralism|संरचनावाद  subjectivism|व्यक्तिपरकता
surrealism|अतियथार्थवाद  symbolism|प्रतीकवाद  synergism|सहक्रियावाद  terrorism|आतंकवाद
totalitarianism|सर्वाधिकारवाद  tourism|पर्यटन  tribalism|जनजातिवाद  triumphalism|विजयवाद
unionism|संघवाद  universalism|सार्वभौमिकता  urbanism|शहरीकरण  utilitarianism|उपयोगितावाद
vandalism|विनाश  veganism|शाकाहार  vitalism|जीवनवाद  voluntarism|स्वैच्छिकता
voyeurism|दृष्टि काम  vulgarism|अश्लीलता  zealotism|कट्टरता
"""

# More -ity/-ty (BULK_2).
_ITY_BULK_2 = """
accountability|जवाबदेही  adaptability|अनुकूलनशीलता  affordability|किफायत  aggressivity|आक्रामकता
ambiguity|अस्पष्टता  amenity|सुविधा  amorality|नैतिकताहीनता  applicability|प्रयोज्यता
approachability|पहुंच  availability|उपलब्धता  biocompatibility|जैव अनुकूलता  capability|क्षमता
cardiovascularity|हृदय  causality|कारणता  celebrity|प्रसिद्धि  centrality|केंद्रीयता
certainty|निश्चितता  circularity|वृत्ताकारता  civility|नागरिकता  clarity|स्पष्टता
commodity|वस्तु  commonality|समानता  compatibility|अनुकूलता  complexity|जटिलता
compressibility|संपीड्यता  conductivity|चालकता  connectivity|संयोजन  conspicuity|दृश्यता
continuity|निरंतरता  convexity|उत्तलता  credibility|विश्वसनीयता  culpability|दोष
curiosity|जिज्ञासा  density|घनत्व  dimensionality|आयाम  disability|अक्षमता
discontinuity|असंततता  diversity|विविधता  durability|टिकाऊपन  elasticity|लोच
electricity|बिजली  eligibility|पात्रता  equality|समानता  equanimity|समभाव
equity|इक्विटी  extremity|चरम  facility|सुविधा  familiarity|परिचितता
feasibility|व्यवहार्यता  fertility|उर्वरता  flexibility|लचीलापन  formality|औपचारिकता
fragility|नाजुकता  frivolity|तुच्छता  generality|सामान्यता  generosity|उदारता
heterogeneity|विषमता  homogeneity|समरूपता  hospitality|आतिथ्य  humanity|मानवता
humidity|नमी  identity|पहचान  immunity|प्रतिरक्षा  impossibility|असंभावना
impunity|दण्डमुक्ति  inability|अक्षमता  inclusivity|समावेशिता  inequality|असमानता
inferiority|निम्नता  infinity|अनंत  inflexibility|अनम्यता  instability|अस्थिरता
integrity|अखंडता  intensity|तीव्रता  intermittency|रुक-रुक  invisibility|अदृश्यता
irregularity|अनियमितता  legality|वैधता  liability|देयता  liberality|उदारता
locality|स्थान  longevity|दीर्घायु  luminosity|चमक  majority|बहुमत
maturity|परिपक्वता  minority|अल्पसंख्यक  mobility|गतिशीलता  modality|प्रणाली
morality|नैतिकता  mortality|मृत्यु दर  multiplicity|बहुलता  mutuality|पारस्परिकता
necessity|आवश्यकता  neutrality|तटस्थता  normality|सामान्यता  novelty|नवीनता
objectivity|निष्पक्षता  opacity|अपारदर्शिता  opportunity|अवसर  parity|समानता
particularity|विशिष्टता  permeability|पारगम्यता  personality|व्यक्तित्व  plurality|बहुलता
polarity|ध्रुवीयता  popularity|लोकप्रियता  possibility|संभावना  priority|प्राथमिकता
probability|संभावना  productivity|उत्पादकता  profitability|लाभप्रदता  prosperity|समृद्धि
proximity|निकटता  publicity|प्रचार  purity|शुद्धता  quantity|मात्रा  reality|वास्तविकता
reciprocity|पारस्परिकता  regularity|नियमितता  reliability|विश्वसनीयता  responsibility|जिम्मेदारी
reversibility|उत्क्रमणीयता  rigidity|कठोरता  royalty|रॉयल्टी  sanity|मानसिक स्वास्थ्य
scarcity|कमी  security|सुरक्षा  sensitivity|संवेदनशीलता  severity|गंभीरता
simplicity|सरलता  sincerity|ईमानदारी  solidarity|एकजुटता  solubility|विलेयता
specificity|विशिष्टता  stability|स्थिरता  suitability|उपयुक्तता  superiority|श्रेष्ठता
sustainability|टिकाऊपन  susceptibility|संवेदनशीलता  symmetry|सममिति  technicality|तकनीकी
tranquility|शांति  uniformity|एकरूपता  uniqueness|विशिष्टता  unity|एकता
validity|वैधता  variability|परिवर्तनशीलता  variety|विविधता  velocity|वेग  viability|व्यवहार्यता
vitality|जीवन शक्ति  volatility|अस्थिरता
"""

# More -ic (BULK_2).
_IC_BULK_2 = """
algebraic|बीजगणितीय  algorithmic|एल्गोरिदम  analgesic|दर्दनाशक  analgesic|पीड़ानाशक
anthropogenic|मानवजनित  antiseptic|रोगाणुरोधक  apocalyptic|सर्वनाश  archaeological|पुरातात्विक
architectonic|वास्तु  aristocratic|अभिजात  aromatic|सुगंधित  asthmatic|दमा
asymmetric|असममित  astrophysical|खगोल भौतिक  atmospheric|वायुमंडलीय  autobiographical|आत्मकथात्मक
autocratic|निरंकुश  autobiographical|आत्मकथात्मक  axiomatic|स्वयंसिद्ध  ballistic|बैलिस्टिक
biochemical|जैव रासायनिक  biographical|जीवनी  bronchial|ब्रोंकियल  bureaucratic|नौकरशाही
cardiovascular|हृदय  catalytic|उत्प्रेरक  catastrophic|विनाशकारी  chronological|कालानुक्रमिक
cinematic|सिनेमाई  climatic|जलवायु  clinical|नैदानिक  colloquial|बोलचाल
comic|कॉमिक  cosmological|ब्रह्मांड  cryptographic|क्रिप्टोग्राफिक  cubic|घन
cyclic|चक्रीय  cylindrical|बेलनाकार  demographic|जनसांख्यिक  deterministic|नियतिवादी
diagnostic|नैदानिक  dialectic|द्वंद्वात्मक  didactic|शिक्षाप्रद  diplomatic|कूटनीतिक
dramatic|नाटकीय  dynamic|गतिशील  eclectic|उदार  ecological|पारिस्थितिक
econometric|अर्थमितीय  electrolytic|इलेक्ट्रोलाइटिक  electromagnetic|विद्युत चुंबकीय
elliptic|दीर्घवृत्तीय  empirical|अनुभवजन्य  enzymatic|एंजाइम  epidemic|महामारी
ergonomic|कार्यिक  ethnographic|नृवंशविज्ञान  etymological|व्युत्पत्ति  euphemistic|प्रेयोक्तिपूर्ण
evolutionary|विकासवादी  exponential|घातांक  expressionistic|अभिव्यक्तिवादी  extrinsic|बाह्य
ferromagnetic|लौहचुंबकीय  forensic|फॉरेंसिक  futuristic|भविष्यवादी  galvanic|गैल्वेनिक
genealogical|वंशावली  generic|सामान्य  genetic|आनुवंशिक  genomic|जीनोम
geophysical|भूभौतिक  grammatical|व्याकरणिक  graphic|ग्राफिक  gravitational|गुरुत्वीय
harmonic|सुरीला  heuristic|अनुमानी  hierarchical|पदानुक्रमिक  holographic|होलोग्राफिक
homogeneous|समांगी  hydrodynamic|जलगतिक  hyperbolic|अतिशयोक्तिपूर्ण  ideological|विचारधारात्मक
idiomatic|मुहावरेदार  idiosyncratic|विलक्षण  immunological|प्रतिरक्षा  impressionistic|प्रभाववादी
improvisational|तात्कालिक  inflammatory|सूजन  inflationary|मुद्रास्फीति  informative|सूचनाप्रद
infrastructure|अवसंरचना  innovative|नवीन  institutional|संस्थागत  instrumental|साधन
intrinsic|आंतरिक  ironic|विडंबनापूर्ण  isotropic|समदैशिक  kinetic|गतिज
lexical|शाब्दिक  linear|रैखिक  linguistic|भाषाई  logarithmic|लघुगणक
lyric|गीतात्मक  macroscopic|विस्तृत  magnetic|चुंबकीय  melodramatic|नाटकीय
metabolic|चयापचय  metaphorical|रूपक  methodological|विधिपरक  microscopic|सूक्ष्म
mnemonic|स्मृति  modal|मॉडल  molecular|आणविक  monolithic|एकाश्म
monotonic|एकस्वर  morphological|रूपात्मक  multimedia|मल्टीमीडिया  mystical|रहस्यमय
narcotic|नशीला  narrative|कथात्मक  neurological|न्यूरोलॉजिकल  nominal|नाममात्र
nonlinear|अरैखिक  nostalgic|विरासत  ontological|अस्तित्ववादी  operational|कार्यात्मक
optical|ऑप्टिकल  optimal|इष्टतम  organic|जैविक  orthopedic|ऑर्थोपेडिक
paradigmatic|प्रतिमान  parametric|पैरामीट्रिक  parasitic|परजीवी  parochial|संकीर्ण
pathogenic|रोगजनक  patriotic|देशभक्तिपूर्ण  pedagogical|शैक्षणिक  periodic|आवधिक
peripheral|परिधीय  phonetic|ध्वन्यात्मक  photographic|फोटोग्राफिक  phylogenetic|वंशावली
pneumatic|वायवीय  poetic|काव्यात्मक  polemic|विवादात्मक  political|राजनीतिक
polyphonic|बहुस्वर  pragmatic|व्यावहारिक  prehistoric|प्रागैतिहासिक  probabilistic|संभाव्य
problematic|समस्यापूर्ण  prophetic|भविष्यसूचक  prophylactic|निवारक  prosaic|गद्यात्मक
prosodic|छंद  prosthetic|कृत्रिम अंग  psychiatric|मनोरोग  psychological|मनोवैज्ञानिक
pyrotechnic|आतिशबाजी  quadratic|द्विघात  qualitative|गुणात्मक  quantitative|मात्रात्मक
realistic|यथार्थवादी  recursive|पुनरावर्ती  relativistic|सापेक्ष  rhetorical|वक्रपटु
rhythmic|लयबद्ध  romantic|रोमांटिक  satiric|व्यंग्यात्मक  schematic|योजनाबद्ध
semantic|अर्थगत  semiotic|संकेत  spherical|गोलाकार  stochastic|यादृच्छिक
strategic|रणनीतिक  stylistic|शैलीगत  syllabic|अक्षर  symbolic|प्रतीकात्मक
sympathetic|सहानुभूतिपूर्ण  symptomatic|लक्षणात्मक  syntactic|वाक्यात्मक  systematic|व्यवस्थित
tactical|सामरिक  taxonomic|वर्गीकरण  technological|तकनीकी  tectonic|भूगर्भिक
telepathic|टेलीपैथिक  thematic|विषयगत  theoretical|सैद्धांतिक  thermodynamic|ऊष्मागतिक
topographic|स्थलाकृतिक  tragic|दुखद  traumatic|आघात  trigonometric|त्रिकोणमितीय
typographic|टाइपोग्राफिक  ultrasonic|अल्ट्रासोनिक  universal|सार्वभौम  utilitarian|उपयोगितावादी
"""

# More -ive (BULK_2).
_IVE_BULK_2 = """
abortive|निष्फल  absorptive|अवशोषक  abusive|अपमानजनक  accretive|संचयी
accusative|अभियोग  acquisitive|अर्जनशील  active|सक्रिय  adaptive|अनुकूली
additive|योजक  adhesive|चिपकने वाला  adjunctive|संलग्न  adoptive|गोद लेना
adversative|विरोधी  affective|भावनात्मक  affirmative|सकारात्मक  aggressive|आक्रामक
alternative|विकल्प  amusive|मनोरंजक  anticipative|पूर्वानुमान  appetitive|इच्छाशक्ति
appreciative|कृतज्ञ  apprehensive|भयभीत  approachive|पहुंच  appropriative|अधिग्रहण
approximative|अनुमानित  argumentative|तर्कपूर्ण  assertive|मुखर  associative|साहचर्य
assumptive|धारणात्मक  attentive|सावधान  attractive|आकर्षक  attributive|विशेषण
auditive|श्रवण  augmentative|वर्धक  authoritative|आधिकारिक  autosuggestive|स्व-सुझाव
aversive|घृणाजनक  bequestive|वसीयत  capitative|प्रति व्यक्ति  captive|बंदी
causative|कारण  coercive|बलपूर्वक  cognitive|संज्ञानात्मक  cohesive|संसक्त
collaborative|सहयोगी  collective|सामूहिक  combative|लड़ाकू  commemorative|स्मारक
communicative|संचारी  comparative|तुलनात्मक  competitive|प्रतिस्पर्धी  comprehensive|व्यापक
compulsive|बाध्यकारी  conclusive|निर्णायक  conductive|सुचालक  conservative|रूढ़िवादी
constructive|रचनात्मक  consumptive|क्षय  contemplative|चिंतनशील  contraceptive|गर्भनिरोधक
conversive|परिवर्तनशील  cooperative|सहकारी  corrective|सुधारात्मक  correlative|सहसंबंधी
corrosive|संक्षारक  creative|रचनात्मक  cumulative|संचयी  curative|उपचारात्मक
decorative|सजावटी  deductive|निगमनात्मक  defensive|रक्षात्मक  demonstrative|प्रदर्शनात्मक
derivative|व्युत्पन्न  descriptive|वर्णनात्मक  destructive|विनाशकारी  detective|जासूस
determinative|निर्धारक  digestive|पाचन  diminutive|क्षुद्र  directive|निर्देशात्मक
disruptive|विघटनकारी  distributive|वितरणात्मक  divisive|विभाजनकारी  effective|प्रभावी
elective|वैकल्पिक  emotive|भावनात्मक  evocative|भावपूर्ण  excessive|अत्यधिक
exclusive|विशेष  executive|कार्यकारी  exhaustive|संपूर्ण  expansive|विस्तारशील
expensive|महंगा  expressive|अभिव्यक्तिपूर्ण  extensive|व्यापक  extractive|निष्कर्षण
figurative|आलंकारिक  formative|गठनात्मक  fugitive|भगोड़ा  generative|उत्पादक
imperative|अनिवार्य  impressive|प्रभावशाली  impulsive|आवेगी  inclusive|समावेशी
indicative|सूचक  inductive|आगमनात्मक  informative|सूचनाप्रद  inquisitive|जिज्ञासु
instructive|शिक्षाप्रद  intensive|गहन  interactive|पारस्परिक  intuitive|सहजज्ञानी
invasive|आक्रामक  inventive|अन्वेषी  iterative|पुनरावृत्त  laxative|रेचक
legislative|विधान  manipulative|हेराफेरी  massive|बड़ा  narrative|कथात्मक
negative|नकारात्मक  nutritive|पोषक  objective|वस्तुनिष्ठ  offensive|आपत्तिजनक
operative|कार्यात्मक  palliative|पीड़ा निवारक  passive|निष्क्रिय  persuasive|सम्मोहक
possessive|अधिकारात्मक  preventive|निवारक  primitive|आदिम  productive|उत्पादक
progressive|प्रगतिशील  prohibitive|निषेधात्मक  prospective|संभावित  protective|सुरक्षात्मक
receptive|ग्रहणशील  reflective|चिंतनशील  regenerative|पुनर्योजी  relative|रिश्तेदार
representative|प्रतिनिधि  restrictive|प्रतिबंधात्मक  retrospective|पूर्वव्यापी  selective|चयनात्मक
sensitive|संवेदनशील  speculative|अटकलबाज  subjective|व्यक्तिपरक  successive|क्रमिक
supportive|सहायक  suggestive|सुझावपूर्ण  superlative|उत्तम  suppressive|दमनकारी
"""

# More -ment (BULK_2).
_MENT_BULK_2 = """
acknowledgment|स्वीकृति  adjudgment|निर्णय  adjustment|समायोजन  advertisement|विज्ञापन
alignment|संरेखण  allotment|आवंटन  amendment|संशोधन  announcement|घोषणा
appointment|नियुक्ति  argument|तर्क  arrangement|व्यवस्था  assessment|मूल्यांकन
assignment|असाइनमेंट  attachment|संलग्नक  attainment|प्राप्ति  augment|वृद्धि
basement|तहखाना  bereavement|शोक  bombardment|बमबारी  casement|खिड़की
commitment|प्रतिबद्धता  complement|पूरक  compliment|प्रशंसा  confinement|कैद
consignment|भेजना  containment|रोक  contentment|संतोष  deployment|तैनाती
development|विकास  disagreement|असहमति  disarmament|निरस्त्रीकरण  displacement|विस्थापन
embarrassment|शर्मिंदगी  embodiment|अवतार  empowerment|सशक्तिकरण  encouragement|प्रोत्साहन
enforcement|प्रवर्तन  engagement|सगाई  enhancement|सुधार  enlargement|विस्तार
enrollment|नामांकन  entertainment|मनोरंजन  environment|पर्यावरण  establishment|स्थापना
excitement|उत्तेजना  experiment|प्रयोग  filament|तंतु  fragment|टुकड़ा
fulfillment|पूर्ति  government|सरकार  impairment|कमी  implementation|कार्यान्वयन
improvement|सुधार  installment|किस्त  instrument|उपकरण  investment|निवेश
involvement|भागीदारी  judgment|निर्णय  management|प्रबंधन  measurement|माप
medication|दवा  misalignment|गलत संरेखण  misgovernment|कुशासन  mismanagement|कुप्रबंधन
moment|क्षण  movement|आंदोलन  nourishment|पोषण  parliament|संसद
payment|भुगतान  placement|प्लेसमेंट  postponement|स्थगन  punishment|सजा
replacement|प्रतिस्थापन  requirement|आवश्यकता  resentment|नाराजगी  retirement|सेवानिवृत्ति
settlement|समझौता  shipment|भेजना  statement|बयान  supplement|पूरक
treatment|उपचार  underdevelopment|अविकसित  underemployment|अल्परोजगार  unemployment|बेरोजगारी
"""

# BULK for all remaining categories (6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22)
_AL_BULK = """
arrival|आगमन  approval|स्वीकृति  betrayal|विश्वासघात  burial|दफन  denial|इनकार
dismissal|बर्खास्तगी  disposal|निपटान  interval|अंतराल  recital|वादन  referral|संदर्भ
renewal|नवीनीकरण  rental|किराया  retrieval|पुनर्प्राप्ति  reversal|उलटफेर  trial|परीक्षण
withdrawal|निकासी  appraisal|मूल्यांकन
"""
_AL_BULK_2 = """
acquittal|दोषमुक्ति  arousal|उत्तेजना  bestowal|प्रदान  betrayal|विश्वासघात  burial|दफनाना
committal|सुपुर्दगी  deferral|स्थगन  dispersal|फैलाव  portrayal|चित्रण  rebuttal|खंडन
rehearsal|पूर्वाभ्यास  removal|हटाना  reprisal|प्रतिशोध  reversal|उलटफेर  survival|उत्तरजीविता
"""
_AL_BULK_3 = """
approval|स्वीकृति  arrival|आगमन  festival|त्योहार  refusal|इनकार  proposal|प्रस्ताव
removal|हटाना  survival|उत्तरजीविता  criminal|अपराधी  mineral|खनिज  animal|जानवर
"""
_AL_BULK_4 = """
approval|स्वीकृति  burial|दफन  denial|इनकार  dismissal|बर्खास्तगी  interval|अंतराल
rehearsal|पूर्वाभ्यास  renewal|नवीनीकरण  rental|किराया  withdrawal|निकासी
"""
_AL_BULK_5 = """
canal|नहर  capital|पूंजी  cardinal|कार्डिनल  journal|जर्नल  material|सामग्री
memorial|स्मारक  portal|पोर्टल  principal|मुख्य  proposal|प्रस्ताव  refusal|इनकार
"""

_OUS_BULK = """
advantageous|लाभकारी  ambiguous|अस्पष्ट  ambitious|महत्वाकांक्षी  analogous|समान
autonomous|स्वायत्त  continuous|निरंतर  courteous|विनम्र  dubious|संदिग्ध
erroneous|गलत  fabulous|शानदार  gorgeous|भव्य  heterogeneous|विषम
homogeneous|समांगी  instantaneous|तात्कालिक  jealous|ईर्ष्यालु  joyous|खुश
laborious|परिश्रमी  monotonous|एकस्वर  mountainous|पहाड़ी  notorious|कुख्यात
obvious|स्पष्ट  pious|धार्मिक  precious|कीमती  previous|पिछला  righteous|धर्मात्मा
rigorous|कठोर  spontaneous|सहज  strenuous|कठिन  superfluous|अतिरिक्त  synonymous|समानार्थी
tedious|उबाऊ  unanimous|सर्वसम्मत  virtuous|सदाचारी  zealous|उत्साही
"""
_OUS_BULK_2 = """
analogous|समान  atrocious|भयानक  capacious|विशाल  conscientious|ईमानदार
conspicuous|स्पष्ट  contagious|संक्रामक  contentious|विवादास्पद  courageous|बहादुर
decorous|शिष्ट  ferocious|क्रूर  frivolous|तुच्छ  glorious|शानदार  gracious|कृपालु
harmonious|सामंजस्यपूर्ण  hideous|भद्दा  hilarious|मजाकिया  indigenous|देशी
ingenious|सरल  instantaneous|तात्कालिक  miraculous|चमत्कारी  monotonous|एकस्वर
ominous|अनिष्टसूचक  pompous|दिखावटी  prosperous|समृद्ध  ridiculous|हास्यास्पद
"""
_OUS_BULK_3 = """
adventurous|साहसी  aqueous|जलीय  aqueous|जल  carnivorous|मांसाहारी  herbivorous|शाकाहारी
ravenous|भूखा  voracious|लालची  amphibious|उभयचर  amphibious|द्विचर
"""
_OUS_BULK_4 = """
ambiguous|अस्पष्ट  ambitious|महत्वाकांक्षी  autonomous|स्वायत्त  continuous|निरंतर
courageous|बहादुर  dubious|संदिग्ध  enormous|विशाल  famous|प्रसिद्ध  generous|उदार
"""
_OUS_BULK_5 = """
anxious|चिंतित  cautious|सतर्क  conscious|सचेत  contagious|संक्रामक  curious|जिज्ञासु
delicious|स्वादिष्ट  furious|क्रोधित  glorious|शानदार  hazardous|खतरनाक  jealous|ईर्ष्यालु
"""

_ARY_BULK = """
ancillary|सहायक  arbitrary|मनमाना  budgetary|बजट  capillary|केशिका  complementary|पूरक
elementary|प्राथमिक  evolutionary|विकासवादी  fragmentary|खंडित  hereditary|वंशानुगत
honorary|सम्मानित  imaginary|काल्पनिक  involuntary|अनैच्छिक  itinerary|यात्रा कार्यक्रम
legendary|पौराणिक  literary|साहित्यिक  momentary|क्षणिक  monetary|मौद्रिक
ordinary|साधारण  planetary|ग्रह  reactionary|प्रतिक्रियावादी  revolutionary|क्रांतिकारी
sanitary|स्वच्छता  sedentary|गतिहीन  solitary|एकांत  stationary|स्थिर  supplementary|पूरक
temporary|अस्थायी  unitary|एकात्मक  voluntary|स्वैच्छिक
"""
_ARY_BULK_2 = """
adversary|प्रतिद्वंद्वी  anniversary|वर्षगांठ  apiary|मधुमक्खी फार्म  aviary|पक्षी घर
boundary|सीमा  commentary|टिप्पणी  contemporary|समकालीन  coronary|कोरोनरी
customary|प्रथागत  dietary|आहार  disciplinary|अनुशासनात्मक  documentary|वृत्तचित्र
dictionary|शब्दकोश  estuary|मुहाना  evolutionary|विकासवादी  functionary|अधिकारी
genuary|जनवरी  intermediary|मध्यस्थ  judiciary|न्यायपालिका  luminary|प्रकाशस्तंभ
missionary|मिशनरी  monetary|मौद्रिक  momentary|क्षणिक  necessary|आवश्यक
"""
_ARY_BULK_3 = """
antiquary|पुरावस्तु  capillary|केशिका  corollary|परिणाम  emissary|दूत  estuary|मुहाना
granary|अन्नागार  hereditary|वंशानुगत  maxillary|जबड़ा  maxillary|मैक्सिलरी
"""
_ARY_BULK_4 = """
arbitrary|मनमाना  binary|द्विआधारी  capillary|केशिका  coronary|कोरोनरी
documentary|वृत्तचित्र  elementary|प्राथमिक  honorary|सम्मानित  imaginary|काल्पनिक
"""
_ARY_BULK_5 = """
complimentary|प्रशंसात्मक  contemporary|समकालीन  customary|प्रथागत  disciplinary|अनुशासनात्मक
literary|साहित्यिक  military|सैन्य  necessary|आवश्यक  preliminary|प्रारंभिक  voluntary|स्वैच्छिक
"""

_ANT_BULK = """
accountant|लेखाकार  applicant|आवेदक  attendant|परिचारक  commandant|कमांडर
consultant|सलाहकार  defendant|प्रतिवादी  descendant|वंशज  emigrant|उत्प्रवासी
immigrant|आप्रवासी  informant|सूचनादाता  inhabitant|निवासी  merchant|व्यापारी
participant|भागीदार  pharmacist|फार्मासिस्ट  protestant|प्रोटेस्टेंट  quadrant|चतुर्थांश
relaxant|शामक  servant|नौकर  tenant|किराएदार  truant|अनुपस्थित  tyrant|तानाशाह
vacant|खाली  warrant|वारंट
"""
_ANT_BULK_2 = """
antioxidant|एंटीऑक्सिडेंट  aspirant|उम्मीदवार  celebrant|उत्सव मनाने वाला  claimant|दावेदार
combatant|योद्धा  coolant|शीतलक  covenant|संधि  dependant|आश्रित  disputant|विवादी
entrant|प्रवेशक  executant|कार्यान्वयक  expectant|गर्भवती  extravagant|फिजूलखर्च
inhabitant|निवासी  lubricant|स्नेहक  migrant|प्रवासी  oxidant|ऑक्सीकरण  pollutant|प्रदूषक
registrant|पंजीकृत  reluctant|अनिच्छुक  remnant|अवशेष  restaurant|रेस्तरां  stimulant|उत्तेजक
"""
_ANT_BULK_3 = """
assistant|सहायक  coolant|शीतलक  defendant|प्रतिवादी  disinfectant|कीटाणुनाशक
migrant|प्रवासी  refrigerant|शीतलक  suppressant|दमनकारी  surfactant|सर्फेक्टेंट
"""
_ANT_BULK_4 = """
assistant|सहायक  consultant|सलाहकार  defendant|प्रतिवादी  immigrant|आप्रवासी
participant|भागीदार  merchant|व्यापारी  tenant|किराएदार  servant|नौकर
"""
_ANT_BULK_5 = """
applicant|आवेदक  attendant|परिचारक  commandant|कमांडर  coolant|शीतलक  descendant|वंशज
emigrant|उत्प्रवासी  informant|सूचनादाता  inhabitant|निवासी  relaxant|शामक  tyrant|तानाशाह
"""

_IST_BULK = """
archivist|संग्रहालय अधिकारी  artist|कलाकार  atheist|नास्तिक  botanist|वनस्पतिशास्त्री
cartoonist|कार्टूनिस्ट  chemist|रसायनज्ञ  columnist|स्तंभकार  cyclist|साइकिल चालक
dentist|दंत चिकित्सक  economist|अर्थशास्त्री  environmentalist|पर्यावरणवादी  florist|फूलवाला
geologist|भूवैज्ञानिक  guitarist|गिटारवादक  journalist|पत्रकार  linguist|भाषाविद
motorist|मोटर चालक  novelist|उपन्यासकार  ophthalmologist|नेत्र रोग विशेषज्ञ  pharmacist|फार्मासिस्ट
pianist|पियानोवादक  physicist|भौतिक विज्ञानी  psychiatrist|मनोचिकित्सक  psychologist|मनोवैज्ञानिक
scientist|वैज्ञानिक  sociologist|समाजशास्त्री  specialist|विशेषज्ञ  stylist|स्टाइलिस्ट
tourist|पर्यटक  typist|टाइपिस्ट  violinist|वायलिन वादक
"""
_IST_BULK_2 = """
activist|कार्यकर्ता  anarchist|अराजकतावादी  archaeologist|पुरातत्ववेत्ता  biologist|जीवविज्ञानी
capitalist|पूंजीवादी  dermatologist|त्वचा विशेषज्ञ  environmentalist|पर्यावरणवादी
extremist|चरमपंथी  feminist|नारीवादी  idealist|आदर्शवादी  nationalist|राष्ट्रवादी
naturalist|प्रकृतिवादी  neurologist|न्यूरोलॉजिस्ट  ophthalmologist|नेत्र रोग विशेषज्ञ
optimist|आशावादी  pessimist|निराशावादी  pharmacist|फार्मासिस्ट  psychiatrist|मनोचिकित्सक
realist|यथार्थवादी  satirist|व्यंग्यकार  terrorist|आतंकवादी  therapist|चिकित्सक
"""
_IST_BULK_3 = """
analyst|विश्लेषक  anthropologist|मानवविज्ञानी  archaeologist|पुरातत्ववेत्ता
geologist|भूविज्ञानी  hygienist|स्वच्छता विशेषज्ञ  meteorologist|मौसम विज्ञानी
pharmacist|फार्मासिस्ट  podiatrist|पोडियाट्रिस्ट  therapist|चिकित्सक
"""
_IST_BULK_4 = """
artist|कलाकार  chemist|रसायनज्ञ  cyclist|साइकिल चालक  dentist|दंत चिकित्सक
economist|अर्थशास्त्री  journalist|पत्रकार  novelist|उपन्यासकार  physicist|भौतिक विज्ञानी
"""
_IST_BULK_5 = """
archaeologist|पुरातत्ववेत्ता  biologist|जीवविज्ञानी  dermatologist|त्वचा विशेषज्ञ
ophthalmologist|नेत्र रोग विशेषज्ञ  pharmacist|फार्मासिस्ट  psychiatrist|मनोचिकित्सक
sociologist|समाजशास्त्री  specialist|विशेषज्ञ  therapist|चिकित्सक
"""

_LOGY_BULK = """
anthropology|मानव विज्ञान  archaeology|पुरातत्व  astrology|ज्योतिष  biology|जीव विज्ञान
cardiology|हृदय विज्ञान  chronology|कालक्रम  criminology|अपराध विज्ञान  dermatology|त्वचा विज्ञान
ecology|पारिस्थितिकी  epidemiology|महामारी विज्ञान  etymology|व्युत्पत्ति  geology|भूविज्ञान
ideology|विचारधारा  meteorology|मौसम विज्ञान  microbiology|सूक्ष्म जीव विज्ञान  mythology|पौराणिक कथा
neurology|न्यूरोलॉजी  pathology|रोग विज्ञान  pharmacology|फार्माकोलॉजी  physiology|शरीर विज्ञान
psychology|मनोविज्ञान  radiology|रेडियोलॉजी  sociology|समाजशास्त्र  technology|प्रौद्योगिकी
terminology|शब्दावली  theology|धर्मशास्त्र  zoology|प्राणि विज्ञान
"""
_LOGY_BULK_2 = """
aetiology|कारण विज्ञान  bacteriology|जीवाणु विज्ञान  cosmology|ब्रह्मांड विज्ञान
criminology|अपराध विज्ञान  cytology|कोशिका विज्ञान  ecology|पारिस्थितिकी
embryology|भ्रूण विज्ञान  epidemiology|महामारी विज्ञान  genealogy|वंशावली
gerontology|वृद्धावस्था विज्ञान  histology|ऊतक विज्ञान  immunology|प्रतिरक्षा विज्ञान
meteorology|मौसम विज्ञान  microbiology|सूक्ष्म जीव विज्ञान  morphology|रूप विज्ञान
neurology|न्यूरोलॉजी  oncology|ऑन्कोलॉजी  paleontology|जीवाश्म विज्ञान
parasitology|परजीवी विज्ञान  pharmacology|फार्माकोलॉजी  physiology|शरीर विज्ञान
rheology|प्रवाह विज्ञान  seismology|भूकंप विज्ञान  serology|सीरम विज्ञान
"""
_LOGY_BULK_3 = """
anthropology|मानव विज्ञान  astrology|ज्योतिष  biology|जीव विज्ञान  ecology|पारिस्थितिकी
geology|भूविज्ञान  neurology|न्यूरोलॉजी  psychology|मनोविज्ञान  sociology|समाजशास्त्र
technology|प्रौद्योगिकी  zoology|प्राणि विज्ञान
"""
_LOGY_BULK_4 = """
archaeology|पुरातत्व  cardiology|हृदय विज्ञान  dermatology|त्वचा विज्ञान
epidemiology|महामारी विज्ञान  geology|भूविज्ञान  morphology|रूप विज्ञान
pathology|रोग विज्ञान  pharmacology|फार्माकोलॉजी  radiology|रेडियोलॉजी
"""
_LOGY_BULK_5 = """
aetiology|कारण विज्ञान  bacteriology|जीवाणु विज्ञान  chronology|कालक्रम  cosmology|ब्रह्मांड विज्ञान
criminology|अपराध विज्ञान  etymology|व्युत्पत्ति  ideology|विचारधारा  meteorology|मौसम विज्ञान
microbiology|सूक्ष्म जीव विज्ञान  neurology|न्यूरोलॉजी  physiology|शरीर विज्ञान  theology|धर्मशास्त्र
"""

_GRAPHY_BULK = """
autobiography|आत्मकथा  bibliography|ग्रंथ सूची  biography|जीवनी  calligraphy|सुलेख
cartography|मानचित्रण  choreography|नृत्य निर्देशन  cinematography|सिनेमाटोग्राफी  cryptography|क्रिप्टोग्राफी
demography|जनसांख्यिकी  ethnography|नृवंशविज्ञान  geography|भूगोल  lithography|लिथोग्राफी
oceanography|समुद्र विज्ञान  orthography|वर्तनी  photography|फोटोग्राफी  radiography|रेडियोग्राफी
stenography|आशुलिपि  topography|स्थलाकृति  typography|टाइपोग्राफी  videography|वीडियोग्राफी
"""
_GRAPHY_BULK_2 = """
autoradiography|ऑटोरेडियोग्राफी  biography|जीवनी  choreography|नृत्य निर्देशन
cosmography|ब्रह्मांड विज्ञान  discography|डिस्कोग्राफी  ethnography|नृवंशविज्ञान
hagiography|संत जीवनी  historiography|इतिहास लेखन  iconography|चित्रण  mammography|मैमोग्राफी
palaeography|पुरालिपि  petrography|शैल विज्ञान  phonography|ध्वनि अंकन
photography|फोटोग्राफी  radiography|रेडियोग्राफी  sonography|अल्ट्रासाउंड  stratigraphy|स्तर विज्ञान
"""
_GRAPHY_BULK_3 = """
biography|जीवनी  geography|भूगोल  photography|फोटोग्राफी  topography|स्थलाकृति
typography|टाइपोग्राफी  demography|जनसांख्यिकी  choreography|नृत्य निर्देशन
"""
_GRAPHY_BULK_4 = """
autobiography|आत्मकथा  biography|जीवनी  cartography|मानचित्रण  demography|जनसांख्यिकी
geography|भूगोल  photography|फोटोग्राफी  topography|स्थलाकृति  typography|टाइपोग्राफी
"""
_GRAPHY_BULK_5 = """
bibliography|ग्रंथ सूची  calligraphy|सुलेख  choreography|नृत्य निर्देशन  cryptography|क्रिप्टोग्राफी
ethnography|नृवंशविज्ञान  lithography|लिथोग्राफी  oceanography|समुद्र विज्ञान  orthography|वर्तनी
radiography|रेडियोग्राफी  stenography|आशुलिपि  videography|वीडियोग्राफी
"""

_METER_BULK = """
altimeter|ऊंचाई मापक  ammeter|अमीटर  barometer|बैरोमीटर  centimeter|सेंटीमीटर
chronometer|क्रोनोमीटर  diameter|व्यास  galvanometer|गैल्वनोमीटर  gasometer|गैसोमीटर
hectometer|हेक्टोमीटर  hygrometer|आर्द्रतामापी  kilometer|किलोमीटर  lactometer|दूध मापक
millimeter|मिलीमीटर  odometer|ओडोमीटर  parameter|पैरामीटर  pedometer|कदम मापक
perimeter|परिधि  speedometer|स्पीडोमीटर  spectrometer|स्पेक्ट्रोमीटर  tachometer|टैकोमीटर
thermometer|थर्मामीटर  voltmeter|वोल्टमीटर
"""
_METER_BULK_2 = """
anemometer|हवा मापक  calorimeter|कैलोरीमीटर  dynamometer|बल मापक  flowmeter|प्रवाह मापक
goniometer|कोण मापक  inclinometer|झुकाव मापक  interferometer|इंटरफेरोमीटर
manometer|दबाव मापक  multimeter|मल्टीमीटर  ohmmeter|ओम मापक  photometer|प्रकाश मापक
radiometer|विकिरण मापक  taximeter|टैक्सी मीटर  telemeter|दूर मापक  voltmeter|वोल्टमीटर
"""
_METER_BULK_3 = """
altimeter|ऊंचाई मापक  barometer|बैरोमीटर  kilometer|किलोमीटर  thermometer|थर्मामीटर
voltmeter|वोल्टमीटर  parameter|पैरामीटर  diameter|व्यास  perimeter|परिधि
"""
_METER_BULK_4 = """
ammeter|अमीटर  centimeter|सेंटीमीटर  chronometer|क्रोनोमीटर  hygrometer|आर्द्रतामापी
millimeter|मिलीमीटर  odometer|ओडोमीटर  pedometer|कदम मापक  speedometer|स्पीडोमीटर
"""
_METER_BULK_5 = """
dynamometer|बल मापक  flowmeter|प्रवाह मापक  galvanometer|गैल्वनोमीटर  gasometer|गैसोमीटर
manometer|दबाव मापक  multimeter|मल्टीमीटर  spectrometer|स्पेक्ट्रोमीटर  tachometer|टैकोमीटर
voltmeter|वोल्टमीटर
"""

_SCOPE_BULK = """
arthroscope|आर्थ्रोस्कोप  bronchoscope|ब्रोंकोस्कोप  colposcope|कॉलपोस्कोप  dermatoscope|डर्माटोस्कोप
endoscope|एंडोस्कोप  fluoroscope|फ्लोरोस्कोप  gyroscope|जाइरोस्कोप  horoscope|कुंडली
kaleidoscope|कैलाइडोस्कोप  laparoscope|लैपरोस्कोप  microscope|सूक्ष्मदर्शी  otoscope|कान दर्शक
periscope|पेरिस्कोप  spectroscope|स्पेक्ट्रोस्कोप  stethoscope|स्टेथोस्कोप  stereoscope|स्टीरियोस्कोप
telescope|दूरबीन
"""
_SCOPE_BULK_2 = """
bioscope|बायोस्कोप  cystoscope|मूत्राशय दर्शक  electroscope|इलेक्ट्रोस्कोप
episcope|एपिस्कोप  fetoscope|भ्रूण दर्शक  gastroscope|गैस्ट्रोस्कोप  iconoscope|आइकनोस्कोप
laryngoscope|स्वर यंत्र दर्शक  oscilloscope|ऑसिलोस्कोप  proctoscope|मलाशय दर्शक
retinoscope|रेटिनोस्कोप  rhinoscope|नाक दर्शक  sigmoidoscope|सिग्मॉइडोस्कोप
"""
_SCOPE_BULK_3 = """
microscope|सूक्ष्मदर्शी  telescope|दूरबीन  endoscope|एंडोस्कोप  periscope|पेरिस्कोप
kaleidoscope|कैलाइडोस्कोप  horoscope|कुंडली  stethoscope|स्टेथोस्कोप
"""
_SCOPE_BULK_4 = """
arthroscope|आर्थ्रोस्कोप  bronchoscope|ब्रोंकोस्कोप  dermatoscope|डर्माटोस्कोप
fluoroscope|फ्लोरोस्कोप  laparoscope|लैपरोस्कोप  otoscope|कान दर्शक  spectroscope|स्पेक्ट्रोस्कोप
"""
_SCOPE_BULK_5 = """
colposcope|कॉलपोस्कोप  cystoscope|मूत्राशय दर्शक  electroscope|इलेक्ट्रोस्कोप  gastroscope|गैस्ट्रोस्कोप
gyroscope|जाइरोस्कोप  kaleidoscope|कैलाइडोस्कोप  oscilloscope|ऑसिलोस्कोप  stereoscope|स्टीरियोस्कोप
"""

_PHOBIA_BULK = """
acrophobia|ऊंचाई का भय  agoraphobia|खुली जगह का भय  arachnophobia|मकड़ी का भय
aviophobia|उड़ान का भय  claustrophobia|संकीर्ण स्थान का भय  dentophobia|दांत का भय
emetophobia|उल्टी का भय  hemophobia|खून का भय  homophobia|समलैंगिकता का भय
hydrophobia|पानी का भय  nyctophobia|अंधेरे का भय  sociophobia|सामाजिक भय
technophobia|तकनीक का भय  trypanophobia|इंजेक्शन का भय  xenophobia|विदेशियों का भय
"""
_PHOBIA_BULK_2 = """
aerophobia|उड़ान का भय  ailurophobia|बिल्ली का भय  algophobia|दर्द का भय  apiphobia|मधुमक्खी का भय
astraphobia|बिजली का भय  atelophobia|अपूर्णता का भय  autophobia|अकेलेपन का भय
barophobia|गुरुत्व का भय  bathmophobia|ढलान का भय  belonephobia|सुई का भय
cyberphobia|कंप्यूटर का भय  ergophobia|काम का भय  gamophobia|विवाह का भय
gynophobia|महिलाओं का भय  iatrophobia|डॉक्टर का भय  logophobia|शब्दों का भय
pyrophobia|आग का भय  thanatophobia|मृत्यु का भय  triskaidekaphobia|१३ का भय
"""
_PHOBIA_BULK_3 = """
acrophobia|ऊंचाई का भय  agoraphobia|खुली जगह का भय  claustrophobia|संकीर्ण स्थान का भय
hydrophobia|पानी का भय  xenophobia|विदेशियों का भय  nyctophobia|अंधेरे का भय
"""
_PHOBIA_BULK_4 = """
acrophobia|ऊंचाई का भय  agoraphobia|खुली जगह का भय  arachnophobia|मकड़ी का भय
claustrophobia|संकीर्ण स्थान का भय  hydrophobia|पानी का भय  technophobia|तकनीक का भय
"""
_PHOBIA_BULK_5 = """
aviophobia|उड़ान का भय  dentophobia|दांत का भय  hemophobia|खून का भय  homophobia|समलैंगिकता का भय
nyctophobia|अंधेरे का भय  sociophobia|सामाजिक भय  trypanophobia|इंजेक्शन का भय  xenophobia|विदेशियों का भय
"""

_PHILE_BULK = """
anglophile|अंग्रेजी प्रेमी  audiophile|ध्वनि प्रेमी  bibliophile|पुस्तक प्रेमी  francophile|फ्रांस प्रेमी
germanophile|जर्मन प्रेमी  indophile|भारत प्रेमी  japanophile|जापान प्रेमी  russophile|रूस प्रेमी
sinophile|चीन प्रेमी  technophile|तकनीक प्रेमी  thermophile|उष्माप्रिय
"""
_PHILE_BULK_2 = """
anglophile|अंग्रेजी प्रेमी  oenophile|शराब प्रेमी  ailurophile|बिल्ली प्रेमी
cinephile|सिनेमा प्रेमी  logophile|शब्द प्रेमी  necrophile|मृतक प्रेमी
paedophile|बाल लैंगिक  technophile|तकनीक प्रेमी  xenophile|विदेशी प्रेमी
zoophile|जानवर प्रेमी
"""
_PHILE_BULK_3 = """
bibliophile|पुस्तक प्रेमी  audiophile|ध्वनि प्रेमी  francophile|फ्रांस प्रेमी
germanophile|जर्मन प्रेमी  indophile|भारत प्रेमी  sinophile|चीन प्रेमी
"""
_PHILE_BULK_4 = """
anglophile|अंग्रेजी प्रेमी  audiophile|ध्वनि प्रेमी  bibliophile|पुस्तक प्रेमी
technophile|तकनीक प्रेमी  thermophile|उष्माप्रिय
"""
_PHILE_BULK_5 = """
francophile|फ्रांस प्रेमी  germanophile|जर्मन प्रेमी  indophile|भारत प्रेमी  japanophile|जापान प्रेमी
oenophile|शराब प्रेमी  russophile|रूस प्रेमी  sinophile|चीन प्रेमी  xenophile|विदेशी प्रेमी
"""

_AGE_BULK = """
bandage|पट्टी  barrage|बांध  camouflage|छलावरण  carriage|गाड़ी  collage|कोलाज
coverage|कवरेज  courage|साहस  damage|नुकसान  dosage|खुराक  garage|गैरेज
heritage|विरासत  image|छवि  leakage|रिसाव  luggage|सामान  marriage|विवाह
massage|मालिश  message|संदेश  mileage|माइलेज  package|पैकेज  passage|मार्ग
percentage|प्रतिशत  pilgrimage|तीर्थयात्रा  plumage|पंख  postage|डाक शुल्क
sabotage|तोड़फोड़  shortage|कमी  storage|भंडारण  usage|उपयोग  village|गांव
voyage|यात्रा  wreckage|मलबा
"""
_AGE_BULK_2 = """
acreage|एकड़  appendage|अनुलग्नक  cleavage|विभाजन  coinage|सिक्का  foliage|पत्ते
footage|फुटेज  hemorrhage|रक्तस्राव  lineage|वंश  manage|प्रबंधन  mortgage|बंधक
patronage|संरक्षण  pillage|लूट  reportage|रिपोर्ट  umbrage|नाराजगी  voltage|वोल्टेज
"""
_AGE_BULK_3 = """
bandage|पट्टी  damage|नुकसान  garage|गैरेज  message|संदेश  package|पैकेज
passage|मार्ग  voyage|यात्रा  storage|भंडारण  usage|उपयोग  village|गांव
"""
_AGE_BULK_4 = """
courage|साहस  heritage|विरासत  marriage|विवाह  mileage|माइलेज  percentage|प्रतिशत
shortage|कमी  wreckage|मलबा  collage|कोलाज  luggage|सामान  postage|डाक शुल्क
"""
_AGE_BULK_5 = """
bandage|पट्टी  barrage|बांध  camouflage|छलावरण  carriage|गाड़ी  coverage|कवरेज  dosage|खुराक
image|छवि  leakage|रिसाव  massage|मालिश  message|संदेश  pilgrimage|तीर्थयात्रा  sabotage|तोड़फोड़
"""

_URE_BULK = """
agriculture|कृषि  architecture|वास्तुकला  armature|आर्मेचर  caricature|कैरिकेचर
culture|संस्कृति  curvature|वक्रता  failure|विफलता  figure|आकृति  fracture|फ्रैक्चर
literature|साहित्य  measure|माप  nature|प्रकृति  nomenclature|नामकरण  pressure|दबाव
procedure|प्रक्रिया  sculpture|मूर्ति  signature|हस्ताक्षर  structure|संरचना
temperature|तापमान  texture|बनावट
"""
_URE_BULK_2 = """
adventure|साहस  aperture|छिद्र  closure|बंद होना  composite|मिश्रित  creature|प्राणी
departure|प्रस्थान  disclosure|खुलासा  enclosure|बाड़ा  exposure|जोखिम  fixture|फिक्स्चर
furniture|फर्नीचर  gesture|इशारा  legislature|विधानमंडल  mixture|मिश्रण  moisture|नमी
pasture|चरागाह  picture|तस्वीर  posture|मुद्रा  scripture|धर्मग्रंथ  seizure|जब्ती
"""
_URE_BULK_3 = """
culture|संस्कृति  nature|प्रकृति  structure|संरचना  literature|साहित्य  temperature|तापमान
pressure|दबाव  procedure|प्रक्रिया  sculpture|मूर्ति  signature|हस्ताक्षर  failure|विफलता
"""
_URE_BULK_4 = """
agriculture|कृषि  architecture|वास्तुकला  curvature|वक्रता  exposure|जोखिम
legislature|विधानमंडल  mixture|मिश्रण  moisture|नमी  pasture|चरागाह  texture|बनावट
"""
_URE_BULK_5 = """
adventure|साहस  aperture|छिद्र  closure|बंद होना  creature|प्राणी  departure|प्रस्थान
disclosure|खुलासा  enclosure|बाड़ा  fixture|फिक्स्चर  furniture|फर्नीचर  gesture|इशारा
"""

_ARY_ARIE_BULK = """
commentary|टिप्पणी  dictionary|शब्दकोश  glossary|शब्दावली  notary|नोटरी
primary|प्राथमिक  salary|वेतन  sanctuary|अभयारण्य  secondary|माध्यमिक
secretary|सचिव  vocabulary|शब्दावली
"""
_ARY_ARIE_BULK_2 = """
actuary|बीमा गणितज्ञ  adversary|प्रतिद्वंद्वी  anniversary|वर्षगांठ  auxiliary|सहायक
beneficiary|लाभार्थी  dignitary|गणमान्य  dispensary|दवाखाना  emissary|दूत
formulary|सूत्रावली  functionary|अधिकारी  infirmary|चिकित्सालय  itinerary|यात्रा कार्यक्रम
lapidary|पत्थर काटने वाला  literary|साहित्यिक  mercenary|भाड़े का  monastery|मठ
"""
_ARY_ARIE_BULK_3 = """
commentary|टिप्पणी  dictionary|शब्दकोश  glossary|शब्दावली  notary|नोटरी
salary|वेतन  sanctuary|अभयारण्य  secretary|सचिव  vocabulary|शब्दावली
"""
_ARY_ARIE_BULK_4 = """
actuary|बीमा गणितज्ञ  beneficiary|लाभार्थी  dispensary|दवाखाना  infirmary|चिकित्सालय
itinerary|यात्रा कार्यक्रम  primary|प्राथमिक  secondary|माध्यमिक
"""
_ARY_ARIE_BULK_5 = """
adversary|प्रतिद्वंद्वी  anniversary|वर्षगांठ  commentary|टिप्पणी  dictionary|शब्दकोश
glossary|शब्दावली  notary|नोटरी  salary|वेतन  sanctuary|अभयारण्य  secretary|सचिव
"""

_ATE_BULK = """
advocate|वकील  aggregate|कुल  certificate|प्रमाणपत्र  climate|जलवायु  candidate|उम्मीदवार
debate|बहस  delegate|प्रतिनिधि  dictate|हुक्म  doctorate|डॉक्टरेट  duplicate|प्रतिलिपि
estimate|अनुमान  graduate|स्नातक  magistrate|मजिस्ट्रेट  mandate|जनादेश  pirate|समुद्री डाकू
private|निजी  separate|अलग  state|राज्य  template|टेम्पलेट
"""
_ATE_BULK_2 = """
affiliate|सहयोगी  alternate|वैकल्पिक  associate|सहयोगी  carbohydrate|कार्बोहाइड्रेट
chocolate|चॉकलेट  electorate|मतदाता  mandate|जनादेश  palate|तालू  predicate|विधेय
primate|प्राइमेट  private|निजी  senate|सीनेट  syndicate|सिंडिकेट  triangulate|त्रिभुज
"""
_ATE_BULK_3 = """
advocate|वकील  certificate|प्रमाणपत्र  climate|जलवायु  delegate|प्रतिनिधि  doctorate|डॉक्टरेट
graduate|स्नातक  magistrate|मजिस्ट्रेट  mandate|जनादेश  pirate|समुद्री डाकू  state|राज्य
"""
_ATE_BULK_4 = """
candidate|उम्मीदवार  debate|बहस  dictate|हुक्म  duplicate|प्रतिलिपि  estimate|अनुमान
private|निजी  template|टेम्पलेट  aggregate|कुल  separate|अलग
"""
_ATE_BULK_5 = """
advocate|वकील  certificate|प्रमाणपत्र  climate|जलवायु  delegate|प्रतिनिधि  doctorate|डॉक्टरेट
graduate|स्नातक  magistrate|मजिस्ट्रेट  mandate|जनादेश  pirate|समुद्री डाकू  state|राज्य
"""


def _build_pattern_3():
    # -tion/-sion → die Xtion/Xsion (German often same spelling)
    en_hi = [
        ("action", "कार्रवाई"), ("nation", "राष्ट्र"), ("tradition", "परंपरा"),
        ("position", "स्थिति"), ("information", "जानकारी"), ("situation", "स्थिति"),
        ("operation", "ऑपरेशन"), ("conversation", "बातचीत"), ("constitution", "संविधान"),
        ("revolution", "क्रांति"), ("evolution", "विकास"), ("resolution", "संकल्प"),
        ("production", "उत्पादन"), ("reduction", "कमी"), ("construction", "निर्माण"),
        ("instruction", "निर्देश"), ("confusion", "भ्रम"), ("illusion", "भ्रम"),
        ("discussion", "चर्चा"), ("mission", "मिशन"), ("passion", "जुनून"),
        ("session", "सत्र"), ("version", "संस्करण"), ("dimension", "आयाम"),
        ("pension", "पेंशन"), ("profession", "पेशा"), ("expression", "अभिव्यक्ति"),
        ("impression", "छाप"), ("concession", "रियायत"), ("lesson", "पाठ"),
        ("addition", "जोड़"), ("edition", "संस्करण"), ("condition", "स्थिति"),
        ("competition", "प्रतिस्पर्धा"), ("repetition", "दोहराव"), ("petition", "याचिका"),
        ("recognition", "मान्यता"), ("definition", "परिभाषा"),
        ("determination", "निर्धारण"), ("examination", "परीक्षा"), ("imagination", "कल्पना"),
        ("explanation", "व्याख्या"), ("organization", "संगठन"), ("civilization", "सभ्यता"),
        ("communication", "संचार"), ("application", "आवेदन"), ("relation", "संबंध"),
        ("population", "जनसंख्या"), ("education", "शिक्षा"), ("location", "स्थान"),
        ("vacation", "छुट्टी"), ("creation", "रचना"), ("foundation", "नींव"),
        ("donation", "दान"), ("celebration", "उत्सव"), ("preparation", "तैयारी"),
        ("declaration", "घोषणा"), ("consideration", "विचार"), ("observation", "अवलोकन"),
        ("conservation", "संरक्षण"), ("reservation", "आरक्षण"), ("innovation", "नवाचार"),
        ("motivation", "प्रेरणा"), ("elevation", "ऊंचाई"), ("evaluation", "मूल्यांकन"),
        ("variation", "विविधता"), ("association", "संघ"), ("negotiation", "बातचीत"),
        ("mediation", "मध्यस्थता"), ("radiation", "विकिरण"), ("graduation", "स्नातक"),
        ("equation", "समीकरण"), ("quotation", "उद्धरण"), ("rotation", "घूर्णन"),
        ("migration", "प्रवास"), ("integration", "एकीकरण"), ("segregation", "अलगाव"),
        ("investigation", "जांच"), ("legislation", "कानून"), ("regulation", "नियमन"),
        ("calculation", "गणना"), ("formulation", "सूत्रीकरण"), ("accumulation", "संचय"),
        ("simulation", "सिमुलेशन"), ("manipulation", "हेराफेरी"), ("circulation", "संचलन"),
        ("inflation", "मुद्रास्फीति"), ("installation", "स्थापना"), ("violation", "उल्लंघन"),
        ("isolation", "अलगाव"), ("contamination", "दूषण"), ("elimination", "उन्मूलन"),
        ("destination", "गंतव्य"), ("designation", "पदनाम"), ("resignation", "इस्तीफा"),
        ("inclination", "झुकाव"), ("ordination", "अभिषेक"), ("fascination", "मोह"),
        ("continuation", "निरंतरता"), ("attention", "ध्यान"), ("intention", "इरादा"),
        ("convention", "सम्मेलन"), ("invention", "आविष्कार"), ("prevention", "रोकथाम"),
        ("intervention", "हस्तक्षेप"), ("tension", "तनाव"), ("extension", "विस्तार"),
        ("comprehension", "समझ"), ("apprehension", "आशंका"), ("suspension", "निलंबन"),
        ("expansion", "विस्तार"), ("conversion", "रूपांतरण"), ("diversion", "विचलन"),
        ("subversion", "विध्वंस"), ("reversion", "वापसी"), ("aversion", "घृणा"),
        ("immersion", "डुबकी"), ("dispersion", "फैलाव"), ("aspersion", "बदनामी"),
        ("emersion", "उभरना"),
    ]
    bulk = (_parse_bulk(_TION_BULK.replace("  ", "\n")) + _parse_bulk(_TION_BULK_2.replace("  ", "\n"))
            + _parse_bulk(_TION_BULK_3.replace("  ", "\n")))
    en_hi = en_hi + bulk
    out = []
    seen_en = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen_en:
            continue
        seen_en.add(en)
        de = "die " + _cap_first(en)
        out.append((de, en, hi))
    return out


def _expand_to_target(entries, target, _pattern_id):
    """Dedupe and return (no cycling – only unique words; add more BULK/en_hi to reach 10k)."""
    return _dedupe_triples(entries)[:target]


def _build_pattern_4():
    # -ty → -tät (die)
    en_hi = [
        ("university", "विश्वविद्यालय"), ("quality", "गुणवत्ता"), ("quantity", "मात्रा"),
        ("identity", "पहचान"), ("reality", "वास्तविकता"), ("nationality", "राष्ट्रीयता"),
        ("priority", "प्राथमिकता"), ("capacity", "क्षमता"), ("activity", "गतिविधि"),
        ("creativity", "रचनात्मकता"), ("objectivity", "निष्पक्षता"), ("subjectivity", "व्यक्तिपरकता"),
        ("stability", "स्थिरता"), ("mobility", "गतिशीलता"), ("popularity", "लोकप्रियता"),
        ("formality", "औपचारिकता"), ("neutrality", "तटस्थता"), ("locality", "स्थान"),
        ("morality", "नैतिकता"), ("vitality", "जीवन शक्ति"), ("equality", "समानता"),
        ("community", "समुदाय"), ("opportunity", "अवसर"), ("possibility", "संभावना"),
        ("responsibility", "जिम्मेदारी"), ("ability", "क्षमता"), ("facility", "सुविधा"),
        ("utility", "उपयोगिता"), ("humidity", "नमी"), ("density", "घनत्व"),
        ("intensity", "तीव्रता"), ("curiosity", "जिज्ञासा"), ("anxiety", "चिंता"),
        ("variety", "विविधता"), ("society", "समाज"), ("prosperity", "समृद्धि"),
        ("security", "सुरक्षा"), ("purity", "शुद्धता"), ("maturity", "परिपक्वता"),
        ("sincerity", "ईमानदारी"), ("severity", "गंभीरता"), ("clarity", "स्पष्टता"),
    ]
    bulk = _parse_bulk(_ITY_BULK) + _parse_bulk(_ITY_BULK_2)
    en_hi = en_hi + bulk
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        if en.endswith("ity"):
            de_stem = en[:-3] + "ität"
        elif en.endswith("ty"):
            de_stem = en[:-2] + "tät"
        else:
            de_stem = en + "tät"
        de = "die " + _cap_first(de_stem)
        out.append((de, en, hi))
    return out


# Manual overrides: English -> German form where different from rule.
_MENT_OVERRIDES = {"medication": "Medikament"}

def _build_pattern_5():
    # -ment → das (same or similar)
    en_hi = [
        ("document", "दस्तावेज़"), ("instrument", "उपकरण"), ("argument", "तर्क"),
        ("moment", "क्षण"), ("element", "तत्व"), ("fragment", "टुकड़ा"),
        ("complement", "पूरक"), ("medication", "दवा"), ("statement", "बयान"),
        ("engagement", "सगाई"), ("management", "प्रबंधन"), ("department", "विभाग"),
        ("apartment", "अपार्टमेंट"), ("equipment", "उपकरण"), ("compartment", "डिब्बा"),
        ("supplement", "पूरक"), ("experiment", "प्रयोग"), ("parliament", "संसद"),
        ("fundament", "नींव"), ("basement", "तहखाना"), ("replacement", "प्रतिस्थापन"),
        ("assessment", "मूल्यांकन"), ("adjustment", "समायोजन"), ("shipment", "भेजना"),
        ("payment", "भुगतान"), ("employment", "रोजगार"), ("development", "विकास"),
        ("movement", "आंदोलन"), ("improvement", "सुधार"), ("agreement", "समझौता"),
        ("treatment", "उपचार"), ("investment", "निवेश"), ("announcement", "घोषणा"),
        ("entertainment", "मनोरंजन"), ("environment", "पर्यावरण"), ("settlement", "समझौता"),
        ("installment", "किस्त"), ("commitment", "प्रतिबद्धता"), ("enrollment", "नामांकन"),
    ]
    bulk = _parse_bulk(_MENT_BULK) + _parse_bulk(_MENT_BULK_2)
    en_hi = en_hi + bulk
    seen = set()
    out = []
    for en, hi in en_hi:
        if en in seen:
            continue
        seen.add(en)
        de_word = _MENT_OVERRIDES.get(en, _cap_first(en))
        out.append(("das " + de_word, en, hi))
    return out


def _build_pattern_6():
    # -al → das/der (noun)
    en_hi = [
        ("signal", "संकेत"), ("festival", "त्योहार"), ("hospital", "अस्पताल"),
        ("terminal", "टर्मिनल"), ("original", "मूल"), ("material", "सामग्री"),
        ("potential", "क्षमता"), ("tutorial", "ट्यूटोरियल"), ("memorial", "स्मारक"),
        ("general", "जनरल"), ("admiral", "एडमिरल"), ("canal", "नहर"),
        ("cardinal", "कार्डिनल"), ("journal", "जर्नल"), ("portal", "पोर्टल"),
        ("capital", "पूंजी"), ("rival", "प्रतिद्वंद्वी"), ("vowel", "स्वर"),
        ("principal", "मुख्य"), ("animal", "जानवर"), ("mineral", "खनिज"),
        ("criminal", "अपराधी"), ("professional", "पेशेवर"), ("removal", "हटाना"),
        ("approval", "स्वीकृति"), ("survival", "उत्तरजीविता"), ("arrival", "आगमन"),
        ("proposal", "प्रस्ताव"), ("refusal", "इनकार"), ("rehearsal", "पूर्वाभ्यास"),
    ]
    bulk = _parse_bulk(_AL_BULK) + _parse_bulk(_AL_BULK_2) + _parse_bulk(_AL_BULK_3) + _parse_bulk(_AL_BULK_4) + _parse_bulk(_AL_BULK_5)
    en_hi = en_hi + bulk
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        out.append(("das " + _cap_first(en), en, hi))
    return out


def _build_pattern_7():
    # -ic → -isch (adjective, no article)
    en_hi = [
        ("romantic", "रोमांटिक"), ("dramatic", "नाटकीय"), ("automatic", "स्वचालित"),
        ("democratic", "लोकतांत्रिक"), ("energetic", "ऊर्जावान"), ("historical", "ऐतिहासिक"),
        ("classic", "क्लासिक"), ("musical", "संगीतमय"), ("optimistic", "आशावादी"),
        ("pessimistic", "निराशावादी"), ("realistic", "यथार्थवादी"), ("specific", "विशिष्ट"),
        ("strategic", "रणनीतिक"), ("sympathetic", "सहानुभूतिपूर्ण"), ("synthetic", "सिंथेटिक"),
        ("tragic", "दुखद"), ("typical", "विशिष्ट"), ("electric", "बिजली का"),
        ("fantastic", "शानदार"), ("heroic", "वीर"), ("economic", "आर्थिक"),
        ("political", "राजनीतिक"), ("physical", "शारीरिक"), ("practical", "व्यावहारिक"),
        ("critical", "आलोचनात्मक"), ("mechanical", "यांत्रिक"), ("chemical", "रासायनिक"),
        ("artistic", "कलात्मक"), ("characteristic", "विशेषता"), ("diplomatic", "कूटनीतिक"),
        ("systematic", "व्यवस्थित"), ("problematic", "समस्यापूर्ण"), ("automatic", "स्वचालित"),
        ("symbolic", "प्रतीकात्मक"), ("organic", "जैविक"), ("academic", "शैक्षणिक"),
        ("dynamic", "गतिशील"), ("atomic", "परमाणु"), ("electronic", "इलेक्ट्रॉनिक"),
        ("basic", "मूलभूत"), ("plastic", "प्लास्टिक"), ("public", "सार्वजनिक"),
        ("republic", "गणतंत्र"), ("topic", "विषय"), ("logic", "तर्क"),
    ]
    bulk = _parse_bulk(_IC_BULK) + _parse_bulk(_IC_BULK_2)
    en_hi = en_hi + bulk
    out = []
    seen = set()
    for en, hi in en_hi:
        if en in seen:
            continue
        seen.add(en)
        if en.endswith("ic"):
            de_stem = en[:-2] + "isch"
        else:
            de_stem = en + "isch"
        out.append((de_stem, en, hi))
    return out


def _build_pattern_8():
    # -ive → -iv (adjective)
    en_hi = [
        ("active", "सक्रिय"), ("passive", "निष्क्रिय"), ("creative", "रचनात्मक"),
        ("positive", "सकारात्मक"), ("negative", "नकारात्मक"), ("intensive", "गहन"),
        ("effective", "प्रभावी"), ("attractive", "आकर्षक"), ("impulsive", "आवेगी"),
        ("instinctive", "सहज"), ("intuitive", "सहजज्ञानी"), ("aggressive", "आक्रामक"),
        ("progressive", "प्रगतिशील"), ("productive", "उत्पादक"), ("subjective", "व्यक्तिपरक"),
        ("objective", "वस्तुनिष्ठ"), ("primitive", "आदिम"), ("sensitive", "संवेदनशील"),
        ("selective", "चयनात्मक"), ("sportive", "खेलकूद वाला"), ("native", "मूल निवासी"),
        ("alternative", "विकल्प"), ("conservative", "रूढ़िवादी"), ("decorative", "सजावटी"),
        ("defensive", "रक्षात्मक"), ("offensive", "आपत्तिजनक"), ("expensive", "महंगा"),
        ("extensive", "व्यापक"), ("massive", "बड़ा"), ("passive", "निष्क्रिय"),
        ("relative", "रिश्तेदार"), ("representative", "प्रतिनिधि"), ("competitive", "प्रतिस्पर्धी"),
        ("additive", "योजक"), ("cognitive", "संज्ञानात्मक"), ("fugitive", "भगोड़ा"),
        ("narrative", "कथात्मक"), ("preventive", "निवारक"), ("respective", "संबंधित"),
    ]
    bulk = _parse_bulk(_IVE_BULK) + _parse_bulk(_IVE_BULK_2)
    en_hi = en_hi + bulk
    out = []
    seen = set()
    for en, hi in en_hi:
        if en in seen:
            continue
        seen.add(en)
        if en.endswith("ive"):
            de_stem = en[:-3] + "iv"
        else:
            de_stem = en + "iv"
        out.append((de_stem, en, hi))
    return out


def _build_pattern_9():
    # -ous → -ös (adjective)
    en_hi = [
        ("nervous", "घबराया हुआ"), ("curious", "जिज्ञासु"), ("serious", "गंभीर"),
        ("generous", "उदार"), ("mysterious", "रहस्यमय"), ("harmonious", "सामंजस्यपूर्ण"),
        ("anonymous", "गुमनाम"), ("glorious", "शानदार"), ("luxurious", "शानदार"),
        ("nebulous", "अस्पष्ट"), ("religious", "धार्मिक"), ("ambitious", "महत्वाकांक्षी"),
        ("infectious", "संक्रामक"), ("suspicious", "संदिग्ध"), ("various", "विभिन्न"),
        ("dangerous", "खतरनाक"), ("famous", "प्रसिद्ध"), ("enormous", "विशाल"),
        ("numerous", "कई"), ("poisonous", "जहरीला"), ("marvelous", "अद्भुत"),
        ("humorous", "मजाकिया"), ("vigorous", "जोरदार"), ("courageous", "बहादुर"),
    ]
    en_hi = en_hi + _parse_bulk(_OUS_BULK) + _parse_bulk(_OUS_BULK_2) + _parse_bulk(_OUS_BULK_3) + _parse_bulk(_OUS_BULK_4) + _parse_bulk(_OUS_BULK_5)
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        if en.endswith("ous"):
            de_stem = en[:-3] + "ös"
        else:
            de_stem = en + "ös"
        out.append((de_stem, en, hi))
    return out


def _build_pattern_10():
    # -ary → -är (adjective)
    en_hi = [
        ("military", "सैन्य"), ("singular", "एकवचन"), ("plural", "बहुवचन"),
        ("solar", "सौर"), ("polar", "ध्रुवीय"), ("vulgar", "अश्लील"),
        ("molar", "दाढ़"), ("linear", "रैखिक"), ("regular", "नियमित"),
        ("popular", "लोकप्रिय"), ("similar", "समान"), ("familiar", "परिचित"),
        ("particular", "विशेष"), ("secular", "धर्मनिरपेक्ष"), ("muscular", "मांसल"),
        ("tubular", "नलिकाकार"), ("angular", "कोणीय"), ("granular", "दानेदार"),
        ("molecular", "आणविक"), ("spectacular", "शानदार"), ("vocabulary", "शब्दावली"),
        ("preliminary", "प्रारंभिक"), ("secondary", "माध्यमिक"), ("primary", "प्राथमिक"),
        ("temporary", "अस्थायी"), ("arbitrary", "मनमाना"), ("contemporary", "समकालीन"),
        ("necessary", "आवश्यक"), ("voluntary", "स्वैच्छिक"), ("customary", "प्रथागत"),
    ]
    en_hi = en_hi + _parse_bulk(_ARY_BULK) + _parse_bulk(_ARY_BULK_2) + _parse_bulk(_ARY_BULK_3) + _parse_bulk(_ARY_BULK_4) + _parse_bulk(_ARY_BULK_5)
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        if en.endswith("ary"):
            de_stem = en[:-3] + "är"
        elif en.endswith("ar"):
            de_stem = en + "är" if not en.endswith("är") else en
        else:
            de_stem = en + "är"
        out.append((de_stem, en, hi))
    return out


def _build_pattern_11():
    # -ant → der Xant (person/thing)
    en_hi = [
        ("migrant", "प्रवासी"), ("demonstrator", "प्रदर्शनकारी"), ("student", "छात्र"),
        ("assistant", "सहायक"), ("consumer", "उपभोक्ता"), ("producer", "निर्माता"),
        ("president", "राष्ट्रपति"), ("resident", "निवासी"), ("supplier", "आपूर्तिकर्ता"),
        ("commander", "कमांडर"), ("consonant", "व्यंजन"), ("diamond", "हीरा"),
        ("elephant", "हाथी"), ("guarantor", "गारंटर"), ("informant", "सूचनादाता"),
        ("client", "मुवक्किल"), ("opponent", "प्रतिद्वंद्वी"), ("emigrant", "उत्प्रवासी"),
        ("applicant", "आवेदक"), ("accountant", "लेखाकार"), ("consultant", "सलाहकार"),
        ("participant", "भागीदार"), ("attendant", "परिचारक"), ("defendant", "प्रतिवादी"),
        ("immigrant", "आप्रवासी"), ("merchant", "व्यापारी"), ("tenant", "किराएदार"),
        ("servant", "नौकर"), ("inhabitant", "निवासी"), ("lieferant", "आपूर्तिकर्ता"),
        ("kommandant", "कमांडर"), ("laborant", "लैब तकनीशियन"), ("kontrahent", "प्रतिद्वंद्वी"),
    ]
    en_hi = en_hi + _parse_bulk(_ANT_BULK) + _parse_bulk(_ANT_BULK_2) + _parse_bulk(_ANT_BULK_3) + _parse_bulk(_ANT_BULK_4) + _parse_bulk(_ANT_BULK_5)
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        de_word = en if en.endswith("ant") else (en.replace("or", "ant").replace("er", "ant") if "or" in en or "er" in en else en)
        if not de_word.endswith("ant"):
            de_word = en
        de = "der " + _cap_first(de_word)
        out.append((de, en, hi))
    return out


def _build_pattern_12():
    # -ist → der Xist
    en_hi = [
        ("artist", "कलाकार"), ("journalist", "पत्रकार"), ("tourist", "पर्यटक"),
        ("pianist", "पियानोवादक"), ("guitarist", "गिटारवादक"), ("optimist", "आशावादी"),
        ("pessimist", "निराशावादी"), ("specialist", "विशेषज्ञ"), ("terrorist", "आतंकवादी"),
        ("communist", "कम्युनिस्ट"), ("socialist", "समाजवादी"), ("capitalist", "पूंजीवादी"),
        ("activist", "कार्यकर्ता"), ("stylist", "स्टाइलिस्ट"), ("typist", "टाइपिस्ट"),
        ("florist", "फूलवाला"), ("satirist", "व्यंग्यकार"), ("columnist", "स्तंभकार"),
        ("scientist", "वैज्ञानिक"), ("economist", "अर्थशास्त्री"), ("dentist", "दंत चिकित्सक"),
        ("chemist", "रसायनज्ञ"), ("physicist", "भौतिक विज्ञानी"), ("biologist", "जीवविज्ञानी"),
        ("psychologist", "मनोवैज्ञानिक"), ("sociologist", "समाजशास्त्री"), ("geologist", "भूविज्ञानी"),
        ("archaeologist", "पुरातत्ववेत्ता"), ("anthropologist", "मानवविज्ञानी"),
    ]
    en_hi = en_hi + _parse_bulk(_IST_BULK) + _parse_bulk(_IST_BULK_2) + _parse_bulk(_IST_BULK_3) + _parse_bulk(_IST_BULK_4) + _parse_bulk(_IST_BULK_5)
    seen = set()
    out = []
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        out.append(("der " + _cap_first(en), en, hi))
    return out


def _build_pattern_13():
    # -logy → die Xlogie
    en_hi = [
        ("biology", "जीव विज्ञान"), ("geology", "भूविज्ञान"), ("psychology", "मनोविज्ञान"),
        ("sociology", "समाजशास्त्र"), ("technology", "प्रौद्योगिकी"), ("ecology", "पारिस्थितिकी"),
        ("mythology", "पौराणिक कथा"), ("astrology", "ज्योतिष"), ("meteorology", "मौसम विज्ञान"),
        ("chronology", "कालक्रम"), ("terminology", "शब्दावली"), ("ideology", "विचारधारा"),
        ("archaeology", "पुरातत्व"), ("anthropology", "मानव विज्ञान"), ("pharmacology", "फार्माकोलॉजी"),
        ("radiology", "रेडियोलॉजी"), ("cardiology", "हृदय विज्ञान"), ("dermatology", "त्वचा विज्ञान"),
        ("neurology", "न्यूरोलॉजी"), ("zoology", "प्राणि विज्ञान"), ("pathology", "रोग विज्ञान"),
        ("physiology", "शरीर विज्ञान"), ("theology", "धर्मशास्त्र"), ("etymology", "व्युत्पत्ति"),
        ("criminology", "अपराध विज्ञान"), ("epidemiology", "महामारी विज्ञान"),
    ]
    en_hi = en_hi + _parse_bulk(_LOGY_BULK) + _parse_bulk(_LOGY_BULK_2) + _parse_bulk(_LOGY_BULK_3) + _parse_bulk(_LOGY_BULK_4) + _parse_bulk(_LOGY_BULK_5)
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        de_stem = en.replace("y", "ie") if en.endswith("ology") else en[:-2] + "ologie"
        if not de_stem.endswith("ologie"):
            de_stem = en[:-2] + "ologie"  # biology -> biologie
        de = "die " + _cap_first(de_stem)
        out.append((de, en, hi))
    return out


def _build_pattern_14():
    # -graphy → die Xgrafie
    en_hi = [
        ("photography", "फोटोग्राफी"), ("geography", "भूगोल"), ("biography", "जीवनी"),
        ("autobiography", "आत्मकथा"), ("bibliography", "ग्रंथ सूची"), ("topography", "स्थलाकृति"),
        ("demography", "जनसांख्यिकी"), ("choreography", "नृत्य निर्देशन"), ("calligraphy", "सुलेख"),
        ("orthography", "वर्तनी"), ("stenography", "आशुलिपि"), ("cartography", "मानचित्रण"),
        ("oceanography", "समुद्र विज्ञान"), ("ethnography", "नृवंशविज्ञान"),
        ("typography", "टाइपोग्राफी"), ("radiography", "रेडियोग्राफी"), ("videography", "वीडियोग्राफी"),
        ("lithography", "लिथोग्राफी"), ("hagiography", "संत जीवनी"), ("cryptography", "क्रिप्टोग्राफी"),
    ]
    en_hi = en_hi + _parse_bulk(_GRAPHY_BULK) + _parse_bulk(_GRAPHY_BULK_2) + _parse_bulk(_GRAPHY_BULK_3) + _parse_bulk(_GRAPHY_BULK_4) + _parse_bulk(_GRAPHY_BULK_5)
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        de_stem = en.replace("phy", "fie").replace("ography", "ografie")
        if "ografie" not in de_stem:
            de_stem = en[:-3] + "ografie"
        de = "die " + _cap_first(de_stem)
        out.append((de, en, hi))
    return out


def _build_pattern_15():
    # -meter → der Xmeter
    en_hi = [
        ("thermometer", "थर्मामीटर"), ("kilometre", "किलोमीटर"), ("centimetre", "सेंटीमीटर"),
        ("millimetre", "मिलीमीटर"), ("diameter", "व्यास"), ("parameter", "पैरामीटर"),
        ("barometer", "बैरोमीटर"), ("speedometer", "स्पीडोमीटर"), ("odometer", "ओडोमीटर"),
        ("voltmeter", "वोल्टमीटर"), ("ammeter", "अमीटर"), ("hygrometer", "आर्द्रतामापी"),
        ("altimeter", "ऊंचाई मापक"), ("chronometer", "क्रोनोमीटर"), ("perimeter", "परिधि"),
        ("tachometer", "टैकोमीटर"), ("gasometer", "गैसोमीटर"), ("lactometer", "दूध मापक"),
        ("pedometer", "कदम मापक"), ("galvanometer", "गैल्वनोमीटर"), ("spectrometer", "स्पेक्ट्रोमीटर"),
    ]
    en_hi = en_hi + _parse_bulk(_METER_BULK) + _parse_bulk(_METER_BULK_2) + _parse_bulk(_METER_BULK_3) + _parse_bulk(_METER_BULK_4) + _parse_bulk(_METER_BULK_5)
    seen = set()
    out = []
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        out.append(("der " + _cap_first(en), en, hi))
    return out


def _build_pattern_16():
    # -scope → das Xskop
    en_hi = [
        ("microscope", "सूक्ष्मदर्शी"), ("telescope", "दूरबीन"), ("stethoscope", "स्टेथोस्कोप"),
        ("endoscope", "एंडोस्कोप"), ("periscope", "पेरिस्कोप"), ("kaleidoscope", "कैलाइडोस्कोप"),
        ("horoscope", "कुंडली"), ("gyroscope", "जाइरोस्कोप"), ("spectroscope", "स्पेक्ट्रोस्कोप"),
        ("stereoscope", "स्टीरियोस्कोप"), ("arthroscope", "आर्थ्रोस्कोप"), ("laparoscope", "लैपरोस्कोप"),
        ("bronchoscope", "ब्रोंकोस्कोप"), ("colposcope", "कॉलपोस्कोप"), ("otoscope", "कान दर्शक"),
        ("ophthalmoscope", "नेत्र दर्शक"), ("dermatoscope", "डर्माटोस्कोप"), ("fluoroscope", "फ्लोरोस्कोप"),
    ]
    en_hi = en_hi + _parse_bulk(_SCOPE_BULK) + _parse_bulk(_SCOPE_BULK_2) + _parse_bulk(_SCOPE_BULK_3) + _parse_bulk(_SCOPE_BULK_4) + _parse_bulk(_SCOPE_BULK_5)
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        de_stem = en.replace("scope", "skop")
        de = "das " + _cap_first(de_stem)
        out.append((de, en, hi))
    return out


def _build_pattern_17():
    # -phobia → die Xphobie
    en_hi = [
        ("phobia", "भय"), ("arachnophobia", "मकड़ी का भय"), ("agoraphobia", "खुली जगह का भय"),
        ("claustrophobia", "संकीर्ण स्थान का भय"), ("hydrophobia", "पानी का भय"),
        ("xenophobia", "विदेशियों का भय"), ("homophobia", "समलैंगिकता का भय"),
        ("nyctophobia", "अंधेरे का भय"), ("acrophobia", "ऊंचाई का भय"), ("sociophobia", "सामाजिक भय"),
        ("technophobia", "तकनीक का भय"), ("dentophobia", "दांत का भय"), ("aviophobia", "उड़ान का भय"),
        ("trypanophobia", "इंजेक्शन का भय"), ("emetophobia", "उल्टी का भय"),
        ("hemophobia", "खून का भय"), ("pyrophobia", "आग का भय"), ("astraphobia", "बिजली का भय"),
    ]
    en_hi = en_hi + _parse_bulk(_PHOBIA_BULK) + _parse_bulk(_PHOBIA_BULK_2) + _parse_bulk(_PHOBIA_BULK_3) + _parse_bulk(_PHOBIA_BULK_4) + _parse_bulk(_PHOBIA_BULK_5)
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        de_stem = en.replace("phobia", "phobie") if en != "phobia" else "Phobie"
        de = "die " + _cap_first(de_stem)
        out.append((de, en, hi))
    return out


def _build_pattern_18():
    # -phile → der Xphil
    en_hi = [
        ("bibliophile", "पुस्तक प्रेमी"), ("anglophile", "अंग्रेजी प्रेमी"), ("technophile", "तकनीक प्रेमी"),
        ("audiophile", "ध्वनि प्रेमी"), ("francophile", "फ्रांस प्रेमी"), ("germanophile", "जर्मन प्रेमी"),
        ("sinophile", "चीन प्रेमी"), ("japanophile", "जापान प्रेमी"), ("russophile", "रूस प्रेमी"),
        ("indophile", "भारत प्रेमी"), ("necrophilia", "मृतक प्रेम"), ("paedophile", "बाल लैंगिक"),
        ("hemophile", "रक्तस्राव रोग"), ("thermophile", "उष्माप्रिय"),         ("halophile", "लवणप्रिय"),
    ]
    en_hi = en_hi + _parse_bulk(_PHILE_BULK) + _parse_bulk(_PHILE_BULK_2) + _parse_bulk(_PHILE_BULK_3) + _parse_bulk(_PHILE_BULK_4) + _parse_bulk(_PHILE_BULK_5)
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        de_stem = en.replace("phile", "phil").replace("philia", "phil")
        de = "der " + _cap_first(de_stem)
        out.append((de, en, hi))
    return out


def _build_pattern_19():
    # -age → die Xage
    en_hi = [
        ("garage", "गैरेज"), ("passage", "मार्ग"), ("floor", "मंजिल"), ("report", "रिपोर्ट"),
        ("assembly", "असेंबली"), ("collage", "कोलाज"), ("parody", "पैरोडी"), ("sabotage", "तोड़फोड़"),
        ("bandage", "पट्टी"), ("courage", "साहस"), ("embarrassment", "शर्मिंदगी"), ("fee", "शुल्क"),
        ("espionage", "जासूसी"), ("massage", "मालिश"), ("margin", "मार्जिन"), ("triage", "ट्रायज"),
        ("household", "घर"), ("rage", "क्रोध"), ("image", "छवि"), ("visage", "चेहरा"),
        ("voyage", "यात्रा"), ("usage", "उपयोग"), ("storage", "भंडारण"), ("coverage", "कवरेज"),
        ("percentage", "प्रतिशत"), ("damage", "नुकसान"), ("manage", "प्रबंधन"), ("marriage", "विवाह"),
        ("carriage", "गाड़ी"), ("package", "पैकेज"), ("village", "गांव"), ("advantage", "फायदा"),
    ]
    en_hi = en_hi + _parse_bulk(_AGE_BULK) + _parse_bulk(_AGE_BULK_2) + _parse_bulk(_AGE_BULK_3) + _parse_bulk(_AGE_BULK_4) + _parse_bulk(_AGE_BULK_5)
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        if en.endswith("age"):
            de_word = en
        else:
            de_word = en + "age" if "age" not in en else en
        de = "die " + _cap_first(de_word)
        out.append((de, en, hi))
    return out


def _build_pattern_20():
    # -ure → die Xur (German often -ur)
    en_hi = [
        ("culture", "संस्कृति"), ("nature", "प्रकृति"), ("temperature", "तापमान"),
        ("structure", "संरचना"), ("literature", "साहित्य"), ("architecture", "वास्तुकला"),
        ("construction", "निर्माण"), ("fracture", "फ्रैक्चर"), ("procedure", "प्रक्रिया"),
        ("censorship", "सेंसरशिप"), ("dictatorship", "तानाशाही"), ("caricature", "कैरिकेचर"),
        ("keyboard", "कीबोर्ड"), ("agriculture", "कृषि"), ("sculpture", "मूर्ति"),
        ("figure", "आकृति"), ("nomenclature", "नामकरण"), ("registry", "रजिस्ट्री"),
        ("cure", "उपचार"), ("failure", "विफलता"), ("pressure", "दबाव"), ("measure", "माप"),
        ("pleasure", "खुशी"), ("exposure", "जोखिम"), ("closure", "बंद होना"),         ("disclosure", "खुलासा"),
    ]
    en_hi = en_hi + _parse_bulk(_URE_BULK) + _parse_bulk(_URE_BULK_2) + _parse_bulk(_URE_BULK_3) + _parse_bulk(_URE_BULK_4) + _parse_bulk(_URE_BULK_5)
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        de_stem = en
        de = "die " + _cap_first(de_stem)
        out.append((de, en, hi))
    return out


def _build_pattern_21():
    # -ary (noun) → die Xarie
    en_hi = [
        ("dictionary", "शब्दकोश"), ("secretary", "सचिव"), ("glossary", "शब्दावली"),
        ("notary", "नोटरी"), ("commentary", "टिप्पणी"), ("vocabulary", "शब्दावली"),
        ("ordinary", "साधारण"), ("temporary", "अस्थायी"), ("primary", "प्राथमिक"),
        ("secondary", "माध्यमिक"), ("sanctuary", "अभयारण्य"), ("salary", "वेतन"),
        ("military", "सैन्य"), ("necessary", "आवश्यक"), ("preliminary", "प्रारंभिक"),
    ]
    en_hi = en_hi + _parse_bulk(_ARY_ARIE_BULK) + _parse_bulk(_ARY_ARIE_BULK_2) + _parse_bulk(_ARY_ARIE_BULK_3) + _parse_bulk(_ARY_ARIE_BULK_4) + _parse_bulk(_ARY_ARIE_BULK_5)
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        de_stem = en.replace("ary", "arie").replace("y", "ie")
        if not de_stem.endswith("arie"):
            de_stem = en[:-2] + "arie" if en.endswith("ry") else en + "arie"
        de = "die " + _cap_first(de_stem)
        out.append((de, en, hi))
    return out


def _build_pattern_22():
    # -ate → der/das Xat
    en_hi = [
        ("candidate", "उम्मीदवार"), ("democrat", "लोकतंत्रवादी"), ("diplomat", "राजनयिक"),
        ("automaton", "स्वचालित"), ("pirate", "समुद्री डाकू"), ("soldier", "सैनिक"),
        ("pilot", "पायलट"), ("idiot", "मूर्ख"), ("patriot", "देशभक्त"), ("aristocrat", "अभिजात"),
        ("bureaucrat", "नौकरशाह"), ("technocrat", "तकनीकी विशेषज्ञ"), ("addressee", "प्राप्तकर्ता"),
        ("emirate", "अमीरात"), ("poster", "पोस्टर"), ("format", "प्रारूप"), ("result", "परिणाम"),
        ("statute", "कानून"), ("certificate", "प्रमाणपत्र"), ("graduate", "स्नातक"),
        ("delegate", "प्रतिनिधि"), ("advocate", "वकील"), ("magistrate", "मजिस्ट्रेट"),
        ("climate", "जलवायु"), ("estimate", "अनुमान"), ("certificate", "प्रमाणपत्र"),
        ("mandate", "जनादेश"), ("dictate", "हुक्म"), ("debate", "बहस"), ("state", "राज्य"),
    ]
    en_hi = en_hi + _parse_bulk(_ATE_BULK) + _parse_bulk(_ATE_BULK_2) + _parse_bulk(_ATE_BULK_3) + _parse_bulk(_ATE_BULK_4) + _parse_bulk(_ATE_BULK_5)
    # Neuter in German: Format, Resultat, Statut, Zertifikat, Plakat, Emirat
    neuter_de = {"format": "Format", "result": "Resultat", "statute": "Statut",
                 "certificate": "Zertifikat", "poster": "Plakat", "emirate": "Emirat"}
    out = []
    seen = set()
    for en, hi in en_hi:
        en = en.strip()
        if en in seen:
            continue
        seen.add(en)
        if en.lower() in neuter_de:
            de_stem = neuter_de[en.lower()]
            art = "das "
        elif en.endswith("ate"):
            de_stem = _cap_first(en[:-2] + "at")
            art = "der "
        else:
            de_stem = _cap_first(en)
            art = "der "
        de = art + de_stem
        out.append((de, en, hi))
    return out


def main():
    builders = {
        "pattern_1_ance_ence": _build_pattern_1,
        "pattern_2_ism": _build_pattern_2,
        "pattern_3_sion_tion": _build_pattern_3,
        "pattern_4_ty": _build_pattern_4,
        "pattern_5_ment": _build_pattern_5,
        "pattern_6_al": _build_pattern_6,
        "pattern_7_ic": _build_pattern_7,
        "pattern_8_ive": _build_pattern_8,
        "pattern_9_ous": _build_pattern_9,
        "pattern_10_ary": _build_pattern_10,
        "pattern_11_ant": _build_pattern_11,
        "pattern_12_ist": _build_pattern_12,
        "pattern_13_logy": _build_pattern_13,
        "pattern_14_graphy": _build_pattern_14,
        "pattern_15_meter": _build_pattern_15,
        "pattern_16_scope": _build_pattern_16,
        "pattern_17_phobia": _build_pattern_17,
        "pattern_18_phile": _build_pattern_18,
        "pattern_19_age": _build_pattern_19,
        "pattern_20_ure": _build_pattern_20,
        "pattern_21_ary_arie": _build_pattern_21,
        "pattern_22_ate": _build_pattern_22,
    }
    extended = {}
    for pid in PATTERN_IDS:
        raw = builders[pid]() if pid in builders else []
        extended[pid] = _expand_to_target(raw, TARGET_PER_PATTERN, pid)

    # Optional: merge extra data from extended_extra.json (same format as output)
    extra_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extended_extra.json")
    if os.path.isfile(extra_path):
        try:
            with open(extra_path, "r", encoding="utf-8") as f:
                extra = json.load(f)
            for pid, arr in extra.items():
                if pid in extended:
                    extended[pid] = extended[pid] + [[x[0], x[1], x[2]] for x in arr]
                    extended[pid] = _expand_to_target(
                        [tuple(x) for x in extended[pid]], TARGET_PER_PATTERN, pid
                    )
        except Exception as e:
            print(f"Warning: could not load {extra_path}: {e}")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_FILENAME)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(extended, f, ensure_ascii=False, indent=2)
    total = sum(len(v) for v in extended.values())
    unique_de = set()
    for arr in extended.values():
        for row in arr:
            unique_de.add(row[0].strip().lower())
    print(f"Written {total} extended words ({len(unique_de)} unique DE) to {out_path}")


if __name__ == "__main__":
    main()
