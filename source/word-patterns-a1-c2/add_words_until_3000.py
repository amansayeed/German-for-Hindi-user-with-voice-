# -*- coding: utf-8 -*-
"""
Add words to word-patterns-vocabulary.json until total reaches 3000.
Uses create_10k_extended pattern builders; adds only (de, en, hi) not already in vocab.
No duplicates. Then runs build_word_patterns.py to regenerate JSON.
"""
import json
import os
import subprocess
import sys

TARGET_TOTAL = 3000
BASE = os.path.dirname(os.path.abspath(__file__))
VOCAB_JSON = os.path.join(BASE, "word-patterns-vocabulary.json")
EXTRA_JSON = os.path.join(BASE, "extended_extra.json")

PATTERN_IDS = [
    "pattern_1_ance_ence", "pattern_2_ism", "pattern_3_sion_tion", "pattern_4_ty",
    "pattern_5_ment", "pattern_6_al", "pattern_7_ic", "pattern_8_ive", "pattern_9_ous",
    "pattern_10_ary", "pattern_11_ant", "pattern_12_ist", "pattern_13_logy",
    "pattern_14_graphy", "pattern_15_meter", "pattern_16_scope", "pattern_17_phobia",
    "pattern_18_phile", "pattern_19_age", "pattern_20_ure", "pattern_21_ary_arie",
    "pattern_22_ate",
]


def load_existing_de():
    """Set of normalized (lowercase) German words already in vocabulary."""
    with open(VOCAB_JSON, "r", encoding="utf-8") as f:
        obj = json.load(f)
    out = set()
    for cat in obj.get("categories", []):
        for w in cat.get("words", []):
            de = (w.get("de") or "").strip().lower()
            if de:
                out.add(de)
    return out


def _parse_bulk(block, sep="  "):
    out = []
    for line in block.strip().splitlines():
        for token in line.split(sep):
            token = token.strip()
            if not token or "|" not in token:
                continue
            parts = token.split("|", 1)
            if len(parts) == 2:
                out.append((parts[0].strip(), parts[1].strip()))
    return out


def _cap_first(s):
    return (s[0].upper() + s[1:]) if s else s


def get_additional_bulk_candidates():
    """Extra (cid, de, en, hi) from new bulk en|hi to reach 3000."""
    # New -ance/-ence (pattern 1): die + -anz/-enz
    p1_bulk = """
    consonance|स्वर सामंजस्य  extravagance|फिजूलखर्च  extravagance|अति  forbearance|सहनशीलता
    irrelevance|अप्रासंगिकता  luminance|चमक  malfeasance|दुराचार  nuisance|उपद्रव
    perseverance|दृढ़ता  protuberance|उभार  purveyance|आपूर्ति  relevance|प्रासंगिकता
    remittance|भेजी रकम  repentance|पश्चाताप  resonance|अनुनाद  severance|विच्छेद
    surveillance|निगरानी  turbulence|अशांति  variance|अंतर  vigilance|सतर्कता
    """
    out = []
    for en, hi in _parse_bulk(p1_bulk):
        if en.endswith("ance"):
            stem = en.replace("ance", "anz")
        elif en.endswith("ence"):
            stem = en.replace("ence", "enz")
        else:
            continue
        de = "die " + _cap_first(stem)
        out.append(("pattern_1_ance_ence", de, en, hi))

    # New -ism (pattern 2): der + stem + ismus
    p2_bulk = """
    absolutism|निरंकुशता  botulism|बोटुलिज़्म  cronyism|भाई-भतीजावाद  despotism|तानाशाही
    empiricism|अनुभववाद  jingoism|कट्टर राष्ट्रवाद  magnetism|चुंबकत्व  minimalism|न्यूनतमवाद
    nepotism|भाई-भतीजावाद  prism|प्रिज्म  solipsism|अहंवाद  syllogism|न्यायवाक्य
    """
    for en, hi in _parse_bulk(p2_bulk):
        if en.endswith("ism"):
            stem = en[:-3] + "ismus"
        else:
            stem = en + "ismus"
        de = "der " + _cap_first(stem)
        out.append(("pattern_2_ism", de, en, hi))

    # New -tion/-sion (pattern 3): die + Capitalize(en)
    p3_bulk = """
    abduction|अपहरण  advection|अनुवहन  aeration|वातन  approbation|अनुमोदन
    ascription|आरोपण  calcification|कैल्सीकरण  carbonation|कार्बोनेशन  categorization|वर्गीकरण
    centralization|केंद्रीकरण  codification|संहिताकरण  conscription|भर्ती  contraception|गर्भनिरोध
    convection|संवहन  decompression|विघटन  deflation|अपस्फीति  deforestation|वनोन्मूलन
    demotion|पदावनति  denotation|अर्थ  depopulation|जनसंख्या कमी  desalination|लवणहरण
    digitization|डिजिटलीकरण  disambiguation|स्पष्टीकरण  distillation|आसवन  domestication|पालतू बनाना
    electrification|विद्युतीकरण  elongation|लंबाई  emancipation|मुक्ति  emigration|उत्प्रवास
    equalization|समीकरण  equivocation|अस्पष्टता  exacerbation|बिगाड़  exaggeration|अतिशयोक्ति
    excommunication|बहिष्कार  exoneration|दोषमुक्ति  expatriation|निर्वासन  extermination|विनाश
    factorization|गुणनखंडन  falsification|जालसाजी  formalization|औपचारिकता  fortification|किलेबंदी
    fossilization|जीवाश्मीकरण  fractionation|विभाजन  generalization|सामान्यीकरण  gentrification|उत्थान
    harmonization|सामंजस्य  hospitalization|अस्पताल में भर्ती  humanization|मानवीकरण
    hybridization|संकरण  hydration|जलयोजन  hydrogenation|हाइड्रोजनीकरण  immunization|प्रतिरक्षण
    impersonation|अनुकरण  impoverishment|गरीबी  inauguration|उद्घाटन  industrialization|औद्योगिकीकरण
    infatuation|मोह  infestation|संक्रमण  inflammation|सूजन  infraction|उल्लंघन
    inhalation|साँस  initialization|प्रारंभ  insurrection|विद्रोह  intensification|तीव्रता
    internalization|आंतरिकरण  intoxication|नशा  inundation|बाढ़  ionization|आयनीकरण
    legalization|कानूनीकरण  legitimization|वैधता  liberalization|उदारीकरण  localization|स्थानीकरण
    marginalization|हाशियाकरण  materialization|मूर्त रूप  maximization|अधिकतमीकरण  mechanization|यंत्रीकरण
    militarization|सैन्यीकरण  modernization|आधुनिकीकरण  mutation|उत्परिवर्तन
    nationalization|राष्ट्रीयकरण  naturalization|प्राकृतिकरण  neutralization|निष्प्रभावीकरण
    normalization|सामान्यीकरण  nullification|रद्द  numeration|गणना  obfuscation|अस्पष्टता
    obstruction|अवरोध  ossification|अस्थिकरण  ostracization|बहिष्कार  overpopulation|जनसंख्या विस्फोट
    pacification|शांतिस्थापन  pagination|पृष्ठांकन  pasteurization|पाश्चरीकरण  penetration|भेदन
    personalization|व्यक्तिकरण  politicization|राजनीतिकरण  polymerization|बहुलकरण
    popularization|लोकप्रियता  predestination|पूर्वनियति  predication|विधेय  prefabrication|पूर्वनिर्माण
    privatization|निजीकरण  probation|परिवीक्षा  procrastination|टालमटोल  proliferation|प्रसार
    promulgation|घोषणा  proportionality|आनुपातिकता  proselytization|धर्मपरिवर्तन
    quantification|मात्रात्मक  ratification|अनुसमर्थन  rationalization|युक्तिसंगत  reclamation|पुनर्प्राप्ति
    reclassification|पुनर्वर्गीकरण  recombination|पुनर्संयोजन  reconfiguration|पुनर्विन्यास
    recrimination|प्रत्यारोप  rectification|सुधार  redecoration|पुनर्सज्जा  redistribution|पुनर्वितरण
    reeducation|पुनशिक्षा  reforestation|पुनर्वनीकरण  refrigeration|शीतलन  regimentation|अनुशासन
    regurgitation|उल्टी  reification|वस्तुकरण  reintegration|पुनःएकीकरण  reinterpretation|पुनर्व्याख्या
    reinvention|पुनर्आविष्कार  rejuvenation|कायाकल्प  remediation|उपचार  remuneration|पारिश्रमिक
    renunciation|त्याग  reorganization|पुनर्गठन  repatriation|प्रत्यावर्तन  replication|प्रतिकृति
    repression|दमन  repudiation|अस्वीकृति  requisition|अधिग्रहण  resubmission|पुनर्समर्पण
    retaliation|प्रतिशोध  retardation|मंदन  retraction|वापसी  reunification|पुनर्मिलन
    revaluation|पुनर्मूल्यांकन  reversion|वापसी  ritualization|रीतिकरण  romanticization|रोमांटिकरण
    routinization|दिनचर्या  sanctification|पवित्रता  sanitization|स्वच्छता  scarring|निशान
    schematization|योजनाकरण  secularization|धर्मनिरपेक्षता  sedimentation|अवसादन
    segmentation|खंडन  sensitization|संवेदीकरण  serialization|क्रमबद्धता  socialization|समाजीकरण
    stabilization|स्थिरीकरण  standardization|मानकीकरण  stigmatization|कलंकन  stratification|स्तरीकरण
    subordination|अधीनता  subsidization|सब्सिडी  suffocation|दम घुटना  summarization|सारांश
    superimposition|अध्यारोपण  supplementation|पूरक  systematization|व्यवस्थापन  temporization|टालमटोल
    territorialization|क्षेत्रीकरण  theorization|सिद्धांतीकरण  tokenization|टोकनन
    totalization|कुलीकरण  traumatization|आघात  trivialization|तुच्छीकरण  typification|प्रतीकीकरण
    unification|एकीकरण  unionization|संघीकरण  urbanization|शहरीकरण  utilization|उपयोग
    valorization|मूल्यांकन  vaporization|वाष्पीकरण  victimization|पीड़ित  vilification|बदनामी
    visualization|दृश्यीकरण  vulgarization|लोकप्रियता  westernization|पश्चिमीकरण
    """
    for en, hi in _parse_bulk(p3_bulk):
        de = "die " + _cap_first(en)
        out.append(("pattern_3_sion_tion", de, en, hi))

    # New -ty (pattern 4): die + -ität/-tät
    p4_bulk = """
    absorbability|अवशोषणीयता  absorbability|अवशोषण  acceptability|स्वीकार्यता  accessibility|पहुंच
    accountability|जवाबदेही  adaptability|अनुकूलनशीलता  adjustability|समायोज्यता
    adoptability|गोद लेने योग्यता  advisability|उचितता  affordability|किफायत  agreeability|सहमति
    amenability|अनुपालन  amiability|मित्रता  applicability|प्रयोज्यता  approachability|पहुंच
    attainability|प्राप्ति  availability|उपलब्धता  believability|विश्वसनीयता  capability|क्षमता
    changeability|परिवर्तनशीलता  clarity|स्पष्टता  compatibility|अनुकूलता  compressibility|संपीड्यता
    conductivity|चालकता  conformability|अनुरूपता  connectivity|संयोजन  conspicuity|दृश्यता
    convertibility|परिवर्तनीयता  credibility|विश्वसनीयता  culpability|दोष  curability|उपचार योग्यता
    dependability|भरोसेमंद  desirability|वांछनीयता  durability|टिकाऊपन  educability|शिक्षणीयता
    eligibility|पात्रता  employability|रोजगार योग्यता  enforceability|प्रवर्तनीयता
    excitability|उत्तेजनशीलता  expandability|विस्तार योग्यता  explicability|व्याख्या योग्यता
    flexibility|लचीलापन  habitability|रहने योग्यता  immutability|अपरिवर्तनीयता
    impassability|अगम्यता  impossibility|असंभावना  impressibility|संवेदनशीलता
    improvability|सुधार योग्यता  incapability|अक्षमता  incompatibility|अनुकूलता रहित
    incompressibility|असंपीड्यता  incontestability|निर्विवादता  incorrigibility|असुधार्यता
    incurability|असाध्यता  indestructibility|अविनाशीयता  indispensability|अनिवार्यता
    inevitability|अनिवार्यता  infallibility|अचूकता  inflexibility|अनम्यता  invincibility|अजेयता
    inviolability|अलंघनीयता  irritability|चिड़चिड़ापन  legibility|पढ़ने योग्यता
    liability|देयता  maintainability|रखरखाव  manageability|प्रबंधनीयता  manipulability|हेराफेरी
    marketability|विक्रय योग्यता  measurability|मापने योग्यता  memorability|यादगार
    miscibility|मिश्रणीयता  movability|गतिशीलता  mutability|परिवर्तनशीलता
    navigability|नौवहन योग्यता  negligibility|नगण्यता  nonability|अक्षमता
    observability|अवलोकनीयता  operability|संचालन योग्यता  opposability|विरोध योग्यता
    passability|गम्यता  payability|भुगतान योग्यता  permeability|पारगम्यता
    portability|पोर्टेबिलिटी  predictability|पूर्वानुमान योग्यता  preferability|पसंद
    processability|प्रक्रिया योग्यता  profitability|लाभप्रदता  programmability|प्रोग्राम योग्यता
    progressivity|प्रगतिशीलता  provability|सिद्धता  readability|पठनीयता  realizability|वास्तविकता
    reasonability|उचितता  receptivity|ग्रहणशीलता  recognizability|पहचान योग्यता
    recoverability|पुनर्प्राप्ति  reliability|विश्वसनीयता  repeatability|दोहराव
    replaceability|प्रतिस्थापनीयता  reproducibility|पुनरुत्पादन  resettability|रीसेट
    reversibility|उत्क्रमणीयता  scalability|मापनीयता  serviceability|सेवा योग्यता
    solvability|समाधान योग्यता  stability|स्थिरता  substitutability|प्रतिस्थापनीयता
    suitability|उपयुक्तता  susceptibility|संवेदनशीलता  sustainability|टिकाऊपन
    traceability|अनुरेखणीयता  tractability|वश्यता  transferability|हस्तांतरणीयता
    translatability|अनुवाद योग्यता  transportability|परिवहन योग्यता  treatability|उपचार योग्यता
    usability|उपयोगिता  variability|परिवर्तनशीलता  viability|व्यवहार्यता  visibility|दृश्यता
    """
    for en, hi in _parse_bulk(p4_bulk):
        if en.endswith("ity"):
            de_stem = en[:-3] + "ität"
        elif en.endswith("ty"):
            de_stem = en[:-2] + "tät"
        else:
            de_stem = en + "tät"
        de = "die " + _cap_first(de_stem)
        out.append(("pattern_4_ty", de, en, hi))

    # New -ment (pattern 5): das + same
    p5_bulk = """
    achievement|उपलब्धि  acknowledgment|स्वीकृति  adjustment|समायोजन  advertisement|विज्ञापन
    alignment|संरेखण  allotment|आवंटन  amendment|संशोधन  announcement|घोषणा
    appointment|नियुक्ति  arrangement|व्यवस्था  assessment|मूल्यांकन  assignment|असाइनमेंट
    attachment|संलग्नक  attainment|प्राप्ति  augment|वृद्धि  basement|तहखाना
    bereavement|शोक  bombardment|बमबारी  casement|खिड़की  commitment|प्रतिबद्धता
    complement|पूरक  compliment|प्रशंसा  confinement|कैद  consignment|भेजना
    containment|रोक  contentment|संतोष  deployment|तैनाती  development|विकास
    disagreement|असहमति  disarmament|निरस्त्रीकरण  displacement|विस्थापन
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
    for en, hi in _parse_bulk(p5_bulk):
        de = "das " + _cap_first(en)
        out.append(("pattern_5_ment", de, en, hi))

    # New -al (pattern 6): das + same
    p6_bulk = """
    acquittal|दोषमुक्ति  arousal|उत्तेजना  bestowal|प्रदान  committal|सुपुर्दगी
    deferral|स्थगन  dispersal|फैलाव  portrayal|चित्रण  rebuttal|खंडन  rehearsal|पूर्वाभ्यास
    removal|हटाना  reprisal|प्रतिशोध  survival|उत्तरजीविता  appraisal|मूल्यांकन
    """
    for en, hi in _parse_bulk(p6_bulk):
        de = "das " + _cap_first(en)
        out.append(("pattern_6_al", de, en, hi))

    # Pattern 7 (-ic → -isch): adjectives, no article
    p7_bulk = """
    algebraic|बीजगणितीय  algorithmic|एल्गोरिदम  analgesic|दर्दनाशक  anthropogenic|मानवजनित
    antiseptic|रोगाणुरोधक  apocalyptic|सर्वनाश  archaeological|पुरातात्विक
    architectonic|वास्तु  asthmatic|दमा  astrophysical|खगोल भौतिक  autobiographical|आत्मकथात्मक
    autocratic|निरंकुश  axiomatic|स्वयंसिद्ध  biochemical|जैव रासायनिक  biographical|जीवनी
    bronchial|ब्रोंकियल  cardiovascular|हृदय  catastrophic|विनाशकारी  chronological|कालानुक्रमिक
    colloquial|बोलचाल  cosmological|ब्रह्मांड  cryptographic|क्रिप्टोग्राफिक  cubic|घन
    cylindrical|बेलनाकार  deterministic|नियतिवादी  didactic|शिक्षाप्रद  eclectic|उदार
    ecological|पारिस्थितिक  econometric|अर्थमितीय  electrolytic|इलेक्ट्रोलाइटिक
    electromagnetic|विद्युत चुंबकीय  elliptic|दीर्घवृत्तीय  empirical|अनुभवजन्य
    enzymatic|एंजाइम  ethnographic|नृवंशविज्ञान  etymological|व्युत्पत्ति  evolutionary|विकासवादी
    exponential|घातांक  expressionistic|अभिव्यक्तिवादी  extrinsic|बाह्य
    ferromagnetic|लौहचुंबकीय  forensic|फॉरेंसिक  futuristic|भविष्यवादी  galvanic|गैल्वेनिक
    genealogical|वंशावली  generic|सामान्य  genomic|जीनोम  geophysical|भूभौतिक
    grammatical|व्याकरणिक  graphic|ग्राफिक  gravitational|गुरुत्वीय  harmonic|सुरीला
    heuristic|अनुमानी  hierarchical|पदानुक्रमिक  holographic|होलोग्राफिक  homogeneous|समांगी
    hydrodynamic|जलगतिक  ideological|विचारधारात्मक  idiosyncratic|विलक्षण
    immunological|प्रतिरक्षा  impressionistic|प्रभाववादी  improvisational|तात्कालिक
    inflammatory|सूजन  inflationary|मुद्रास्फीति  innovative|नवीन  institutional|संस्थागत
    instrumental|साधन  intrinsic|आंतरिक  isotropic|समदैशिक  lexical|शाब्दिक
    linear|रैखिक  logarithmic|लघुगणक  lyric|गीतात्मक  macroscopic|विस्तृत
    melodramatic|नाटकीय  metaphorical|रूपक  methodological|विधिपरक  mnemonic|स्मृति
    modal|मॉडल  molecular|आणविक  monolithic|एकाश्म  monotonic|एकस्वर  morphological|रूपात्मक
    multimedia|मल्टीमीडिया  mystical|रहस्यमय  narcotic|नशीला  neurological|न्यूरोलॉजिकल
    nominal|नाममात्र  nonlinear|अरैखिक  nostalgic|विरासत  ontological|अस्तित्ववादी
    operational|कार्यात्मक  optical|ऑप्टिकल  optimal|इष्टतम  orthopedic|ऑर्थोपेडिक
    paradigmatic|प्रतिमान  parametric|पैरामीट्रिक  parasitic|परजीवी  parochial|संकीर्ण
    pathogenic|रोगजनक  pedagogical|शैक्षणिक  peripheral|परिधीय  phylogenetic|वंशावली
    pneumatic|वायवीय  polemic|विवादात्मक  polyphonic|बहुस्वर  pragmatic|व्यावहारिक
    prehistoric|प्रागैतिहासिक  probabilistic|संभाव्य  problematic|समस्यापूर्ण  prophylactic|निवारक
    prosaic|गद्यात्मक  prosodic|छंद  prosthetic|कृत्रिम अंग  psychiatric|मनोरोग
    psychological|मनोवैज्ञानिक  pyrotechnic|आतिशबाजी  quadratic|द्विघात  qualitative|गुणात्मक
    quantitative|मात्रात्मक  recursive|पुनरावर्ती  relativistic|सापेक्ष  rhetorical|वक्रपटु
    rhythmic|लयबद्ध  satiric|व्यंग्यात्मक  semiotic|संकेत  spherical|गोलाकार
    stochastic|यादृच्छिक  stylistic|शैलीगत  syllabic|अक्षर  symbolic|प्रतीकात्मक
    symptomatic|लक्षणात्मक  syntactic|वाक्यात्मक  tactical|सामरिक  taxonomic|वर्गीकरण
    technological|तकनीकी  tectonic|भूगर्भिक  telepathic|टेलीपैथिक  thermodynamic|ऊष्मागतिक
    topographic|स्थलाकृतिक  traumatic|आघात  trigonometric|त्रिकोणमितीय  typographic|टाइपोग्राफिक
    ultrasonic|अल्ट्रासोनिक  universal|सार्वभौम  utilitarian|उपयोगितावादी
    """
    for en, hi in _parse_bulk(p7_bulk):
        stem = (en[:-2] + "isch") if en.endswith("ic") else (en + "isch")
        out.append(("pattern_7_ic", stem, en, hi))

    # Pattern 8 (-ive → -iv)
    p8_bulk = """
    abortive|निष्फल  absorptive|अवशोषक  accretive|संचयी  accusative|अभियोग
    acquisitive|अर्जनशील  active|सक्रिय  adoptive|गोद लेना  adversative|विरोधी
    affective|भावनात्मक  aggressive|आक्रामक  amusive|मनोरंजक  appetitive|इच्छाशक्ति
    apprehensive|भयभीत  appropriative|अधिग्रहण  approximative|अनुमानित  assumptive|धारणात्मक
    attentive|सावधान  attributive|विशेषण  auditive|श्रवण  augmentative|वर्धक
    autosuggestive|स्व-सुझाव  aversive|घृणाजनक  capitative|प्रति व्यक्ति  captive|बंदी
    causative|कारण  coercive|बलपूर्वक  cognitive|संज्ञानात्मक  cohesive|संसक्त
    consumptive|क्षय  contraceptive|गर्भनिरोधक  conversive|परिवर्तनशील  correlative|सहसंबंधी
    corrosive|संक्षारक  curative|उपचारात्मक  deductive|निगमनात्मक  detective|जासूसी
    determinative|निर्धारक  diminutive|क्षुद्र  directive|निर्देशात्मक  disruptive|विघटनकारी
    divisive|विभाजनकारी  emotive|भावनात्मक  extractive|निष्कर्षण  formative|गठनात्मक
    fugitive|भगोड़ा  impulsive|आवेगी  laxative|रेचक  palliative|पीड़ा निवारक
    suppressive|दमनकारी
    """
    for en, hi in _parse_bulk(p8_bulk):
        stem = (en[:-3] + "iv") if en.endswith("ive") else (en + "iv")
        out.append(("pattern_8_ive", stem, en, hi))

    # Pattern 9 (-ous → -ös)
    p9_bulk = """
    adventurous|साहसी  aqueous|जलीय  carnivorous|मांसाहारी  herbivorous|शाकाहारी
    ravenous|भूखा  voracious|लालची  amphibious|उभयचर  atrocious|भयानक
    capacious|विशाल  conscientious|ईमानदार  conspicuous|स्पष्ट  contentious|विवादास्पद
    decorous|शिष्ट  ferocious|क्रूर  frivolous|तुच्छ  gracious|कृपालु  hideous|भद्दा
    hilarious|मजाकिया  indigenous|देशी  ingenious|सरल  miraculous|चमत्कारी
    ominous|अनिष्टसूचक  pompous|दिखावटी  prosperous|समृद्ध  ridiculous|हास्यास्पद
    """
    for en, hi in _parse_bulk(p9_bulk):
        stem = (en[:-3] + "ös") if en.endswith("ous") else (en + "ös")
        out.append(("pattern_9_ous", stem, en, hi))

    # Pattern 10 (-ary → -är)
    p10_bulk = """
    adversary|प्रतिद्वंद्वी  anniversary|वर्षगांठ  apiary|मधुमक्खी फार्म  aviary|पक्षी घर
    boundary|सीमा  commentary|टिप्पणी  contemporary|समकालीन  coronary|कोरोनरी
    customary|प्रथागत  dietary|आहार  disciplinary|अनुशासनात्मक  documentary|वृत्तचित्र
    estuary|मुहाना  functionary|अधिकारी  intermediary|मध्यस्थ  judiciary|न्यायपालिका
    luminary|प्रकाशस्तंभ  missionary|मिशनरी  necessary|आवश्यक  antiquary|पुरावस्तु
    corollary|परिणाम  emissary|दूत  granary|अन्नागार  maxillary|जबड़ा
    complimentary|प्रशंसात्मक  preliminary|प्रारंभिक
    """
    for en, hi in _parse_bulk(p10_bulk):
        stem = (en[:-3] + "är") if en.endswith("ary") else (en + "är")
        out.append(("pattern_10_ary", stem, en, hi))

    # Pattern 11 (-ant): der + same
    p11_bulk = """
    antioxidant|एंटीऑक्सिडेंट  aspirant|उम्मीदवार  celebrant|उत्सव मनाने वाला  claimant|दावेदार
    combatant|योद्धा  coolant|शीतलक  covenant|संधि  dependant|आश्रित  disputant|विवादी
    entrant|प्रवेशक  executant|कार्यान्वयक  expectant|गर्भवती  extravagant|फिजूलखर्च
    lubricant|स्नेहक  oxidant|ऑक्सीकरण  pollutant|प्रदूषक  registrant|पंजीकृत
    reluctant|अनिच्छुक  remnant|अवशेष  restaurant|रेस्तरां  stimulant|उत्तेजक
    disinfectant|कीटाणुनाशक  refrigerant|शीतलक  suppressant|दमनकारी  surfactant|सर्फेक्टेंट
    """
    for en, hi in _parse_bulk(p11_bulk):
        de = "der " + _cap_first(en)
        out.append(("pattern_11_ant", de, en, hi))

    # Pattern 12 (-ist): der + same
    p12_bulk = """
    analyst|विश्लेषक  anthropologist|मानवविज्ञानी  hygienist|स्वच्छता विशेषज्ञ
    meteorologist|मौसम विज्ञानी  podiatrist|पोडियाट्रिस्ट
    """
    for en, hi in _parse_bulk(p12_bulk):
        de = "der " + _cap_first(en)
        out.append(("pattern_12_ist", de, en, hi))

    # Pattern 13 (-logy → -logie)
    p13_bulk = """
    aetiology|कारण विज्ञान  bacteriology|जीवाणु विज्ञान  cosmology|ब्रह्मांड विज्ञान
    cytology|कोशिका विज्ञान  embryology|भ्रूण विज्ञान  genealogy|वंशावली
    gerontology|वृद्धावस्था विज्ञान  histology|ऊतक विज्ञान  immunology|प्रतिरक्षा विज्ञान
    morphology|रूप विज्ञान  oncology|ऑन्कोलॉजी  paleontology|जीवाश्म विज्ञान
    parasitology|परजीवी विज्ञान  rheology|प्रवाह विज्ञान  seismology|भूकंप विज्ञान
    serology|सीरम विज्ञान
    """
    for en, hi in _parse_bulk(p13_bulk):
        de_stem = en.replace("y", "ie") if en.endswith("ology") else (en[:-2] + "ologie")
        if not de_stem.endswith("ologie"):
            de_stem = en[:-2] + "ologie"
        de = "die " + _cap_first(de_stem)
        out.append(("pattern_13_logy", de, en, hi))

    # Pattern 14 (-graphy → -grafie)
    p14_bulk = """
    autoradiography|ऑटोरेडियोग्राफी  discography|डिस्कोग्राफी  hagiography|संत जीवनी
    historiography|इतिहास लेखन  iconography|चित्रण  mammography|मैमोग्राफी
    palaeography|पुरालिपि  petrography|शैल विज्ञान  phonography|ध्वनि अंकन
    sonography|अल्ट्रासाउंड  stratigraphy|स्तर विज्ञान
    """
    for en, hi in _parse_bulk(p14_bulk):
        de_stem = en.replace("phy", "fie").replace("ography", "ografie")
        if "ografie" not in de_stem:
            de_stem = en[:-3] + "ografie"
        de = "die " + _cap_first(de_stem)
        out.append(("pattern_14_graphy", de, en, hi))

    # Pattern 15 (-meter): der + same
    p15_bulk = """
    anemometer|हवा मापक  calorimeter|कैलोरीमीटर  dynamometer|बल मापक  flowmeter|प्रवाह मापक
    goniometer|कोण मापक  inclinometer|झुकाव मापक  interferometer|इंटरफेरोमीटर
    manometer|दबाव मापक  multimeter|मल्टीमीटर  ohmmeter|ओम मापक  photometer|प्रकाश मापक
    radiometer|विकिरण मापक  taximeter|टैक्सी मीटर  telemeter|दूर मापक
    """
    for en, hi in _parse_bulk(p15_bulk):
        de = "der " + _cap_first(en)
        out.append(("pattern_15_meter", de, en, hi))

    # Pattern 16 (-scope → das -skop)
    p16_bulk = """
    bioscope|बायोस्कोप  cystoscope|मूत्राशय दर्शक  electroscope|इलेक्ट्रोस्कोप
    episcope|एपिस्कोप  fetoscope|भ्रूण दर्शक  gastroscope|गैस्ट्रोस्कोप  iconoscope|आइकनोस्कोप
    laryngoscope|स्वर यंत्र दर्शक  oscilloscope|ऑसिलोस्कोप  proctoscope|मलाशय दर्शक
    retinoscope|रेटिनोस्कोप  rhinoscope|नाक दर्शक  sigmoidoscope|सिग्मॉइडोस्कोप
    """
    for en, hi in _parse_bulk(p16_bulk):
        de_stem = en.replace("scope", "skop")
        de = "das " + _cap_first(de_stem)
        out.append(("pattern_16_scope", de, en, hi))

    # Pattern 17 (-phobia → die -phobie)
    p17_bulk = """
    aerophobia|उड़ान का भय  ailurophobia|बिल्ली का भय  algophobia|दर्द का भय  apiphobia|मधुमक्खी का भय
    atelophobia|अपूर्णता का भय  autophobia|अकेलेपन का भय  barophobia|गुरुत्व का भय
    bathmophobia|ढलान का भय  belonephobia|सुई का भय  cyberphobia|कंप्यूटर का भय
    ergophobia|काम का भय  gamophobia|विवाह का भय  gynophobia|महिलाओं का भय
    iatrophobia|डॉक्टर का भय  logophobia|शब्दों का भय  thanatophobia|मृत्यु का भय
    triskaidekaphobia|१३ का भय
    """
    for en, hi in _parse_bulk(p17_bulk):
        de_stem = en.replace("phobia", "phobie")
        de = "die " + _cap_first(de_stem)
        out.append(("pattern_17_phobia", de, en, hi))

    # Pattern 18 (-phile → der -phil)
    p18_bulk = """
    oenophile|शराब प्रेमी  ailurophile|बिल्ली प्रेमी  cinephile|सिनेमा प्रेमी
    logophile|शब्द प्रेमी  necrophile|मृतक प्रेमी  paedophile|बाल लैंगिक
    xenophile|विदेशी प्रेमी  zoophile|जानवर प्रेमी
    """
    for en, hi in _parse_bulk(p18_bulk):
        de_stem = en.replace("phile", "phil").replace("philia", "phil")
        de = "der " + _cap_first(de_stem)
        out.append(("pattern_18_phile", de, en, hi))

    # Pattern 19 (-age): die + same
    p19_bulk = """
    acreage|एकड़  appendage|अनुलग्नक  cleavage|विभाजन  coinage|सिक्का  foliage|पत्ते
    footage|फुटेज  hemorrhage|रक्तस्राव  lineage|वंश  mortgage|बंधक  patronage|संरक्षण
    pillage|लूट  umbrage|नाराजगी  voltage|वोल्टेज
    """
    for en, hi in _parse_bulk(p19_bulk):
        de = "die " + _cap_first(en)
        out.append(("pattern_19_age", de, en, hi))

    # Pattern 20 (-ure): die + same
    p20_bulk = """
    adventure|साहस  aperture|छिद्र  closure|बंद होना  creature|प्राणी  departure|प्रस्थान
    disclosure|खुलासा  enclosure|बाड़ा  exposure|जोखिम  fixture|फिक्स्चर
    furniture|फर्नीचर  gesture|इशारा  legislature|विधानमंडल  mixture|मिश्रण
    moisture|नमी  pasture|चरागाह  picture|तस्वीर  posture|मुद्रा  scripture|धर्मग्रंथ
    seizure|जब्ती
    """
    for en, hi in _parse_bulk(p20_bulk):
        de = "die " + _cap_first(en)
        out.append(("pattern_20_ure", de, en, hi))

    # Pattern 21 (-ary → die -arie)
    p21_bulk = """
    actuary|बीमा गणितज्ञ  auxiliary|सहायक  beneficiary|लाभार्थी  dignitary|गणमान्य
    dispensary|दवाखाना  formulary|सूत्रावली  infirmary|चिकित्सालय  itinerary|यात्रा कार्यक्रम
    lapidary|पत्थर काटने वाला  literary|साहित्यिक  mercenary|भाड़े का  monastery|मठ
    """
    for en, hi in _parse_bulk(p21_bulk):
        de_stem = en.replace("ary", "arie").replace("y", "ie")
        if not de_stem.endswith("arie"):
            de_stem = (en[:-2] + "arie") if en.endswith("ry") else (en + "arie")
        de = "die " + _cap_first(de_stem)
        out.append(("pattern_21_ary_arie", de, en, hi))

    # Pattern 22 (-ate): der/das
    p22_bulk = """
    affiliate|सहयोगी  alternate|वैकल्पिक  associate|सहयोगी  carbohydrate|कार्बोहाइड्रेट
    chocolate|चॉकलेट  electorate|मतदाता  palate|तालू  predicate|विधेय  primate|प्राइमेट
    senate|सीनेट  syndicate|सिंडिकेट  triangulate|त्रिभुज
    """
    neuter = {"format": "Format", "result": "Resultat", "statute": "Statut", "certificate": "Zertifikat",
              "poster": "Plakat", "emirate": "Emirat"}
    for en, hi in _parse_bulk(p22_bulk):
        en_l = en.lower()
        if en_l in neuter:
            de = "das " + neuter[en_l]
        elif en.endswith("ate"):
            de = "der " + _cap_first(en[:-2] + "at")
        else:
            de = "der " + _cap_first(en)
        out.append(("pattern_22_ate", de, en, hi))

    return out


def get_rare_candidates():
    """Rarer (en, hi) that likely yield unique de to reach 3000."""
    out = []
    # Rare -tion/-sion (pattern 3)
    rare_p3 = """
    deoxygenation|अपऑक्सीजनीकरण  recontextualization|पुनर्संदर्भीकरण  desulfurization|गंधक हरण
    demineralization|विखनिजीकरण  reinitialization|पुनः आरंभ  decarboxylation|डीकार्बोक्सिलीकरण
    transesterification|ट्रान्सएस्टरीकरण  esterification|एस्टरीकरण  hydroxylation|हाइड्रॉक्सिलीकरण
    carboxylation|कार्बोक्सिलीकरण  methylation|मिथाइलेशन  glycosylation|ग्लाइकोसिलेशन
    phosphorylation|फॉस्फोरिलेशन  acetylation|एसिटिलेशन  alkylation|ऐल्किलीकरण
    nitration|नाइट्रेशन  sulfonation|सल्फोनेशन  halogenation|हैलोजनीकरण
    epoxidation|एपॉक्सीकरण  isomerization|समावयवीकरण  dimerization|डाइमराइजेशन
    oligomerization|ऑलिगोमराइजेशन  copolymerization|सहबहुलकरण  crosslinking|क्रॉसलिंकिंग
    functionalization|कार्यात्मकीकरण  derivatization|व्युत्पत्ति  characterization|अभिलक्षण
    parameterization|पैरामीटरीकरण  discretization|विवेकन  linearization|रैखिकीकरण
    vectorization|सदिशीकरण  parallelization|समानांतरीकरण  optimization|अनुकूलन
    """
    for en, hi in _parse_bulk(rare_p3):
        de = "die " + _cap_first(en)
        out.append(("pattern_3_sion_tion", de, en, hi))
    # Rare -ity (pattern 4)
    rare_p4 = """
    extensibility|विस्तार योग्यता  configurability|विन्यास योग्यता  interoperability|अंतरसंचालन
    modularity|मॉड्यूलरिटी  scalability|मापनीयता  maintainability|रखरखाव योग्यता
    testability|परीक्षण योग्यता  deployability|तैनाती योग्यता  composability|संयोजन योग्यता
    reusability|पुन: उपयोग  extensibility|विस्तारणीयता  invariability|अपरिवर्तनीयता
    """
    for en, hi in _parse_bulk(rare_p4):
        de_stem = (en[:-3] + "ität") if en.endswith("ity") else (en[:-2] + "tät")
        de = "die " + _cap_first(de_stem)
        out.append(("pattern_4_ty", de, en, hi))
    # Rare -ment (pattern 5)
    rare_p5 = """
    embedment|एम्बेडमेंट  encasement|आवरण  entrenchment|मजबूती  fragment|टुकड़ा
    increment|वृद्धि  indictment|अभियोग  infringement|उल्लंघन  instalment|किस्त
    """
    for en, hi in _parse_bulk(rare_p5):
        de = "das " + _cap_first(en)
        out.append(("pattern_5_ment", de, en, hi))
    # Rare -ance/-ence (pattern 1)
    rare_p1 = """
    remittance|भेजी रकम  severance|विच्छेद  consonance|स्वर सामंजस्य  luminance|चमक
    malfeasance|दुराचार  irrelevance|अप्रासंगिकता  turbulence|अशांति  variance|अंतर
    """
    for en, hi in _parse_bulk(rare_p1):
        stem = en.replace("ance", "anz").replace("ence", "enz") if "ance" in en or "ence" in en else en
        de = "die " + _cap_first(stem)
        out.append(("pattern_1_ance_ence", de, en, hi))
    # Rare -ism (pattern 2)
    rare_p2 = """
    solipsism|अहंवाद  syllogism|न्यायवाक्य  nepotism|भाई-भतीजावाद  prism|प्रिज्म
    """
    for en, hi in _parse_bulk(rare_p2):
        stem = (en[:-3] + "ismus") if en.endswith("ism") else (en + "ismus")
        de = "der " + _cap_first(stem)
        out.append(("pattern_2_ism", de, en, hi))
    # Rare -ive (pattern 8)
    rare_p8 = """
    abortive|निष्फल  accretive|संचयी  assumptive|धारणात्मक  augmentative|वर्धक
    correlative|सहसंबंधी  curative|उपचारात्मक  deductive|निगमनात्मक  diminutive|क्षुद्र
    """
    for en, hi in _parse_bulk(rare_p8):
        stem = (en[:-3] + "iv") if en.endswith("ive") else (en + "iv")
        out.append(("pattern_8_ive", stem, en, hi))
    # Rare -ic (pattern 7)
    rare_p7 = """
    allelopathic|एलेलोपैथिक  allosteric|ऑलोस्टेरिक  anabolic|उपचय  anthropogenic|मानवजनित
    antipathic|विरोधी  astrochemical|खगोल रासायनिक  chemotactic|कीमोटैक्टिक
    """
    for en, hi in _parse_bulk(rare_p7):
        stem = (en[:-2] + "isch") if en.endswith("ic") else (en + "isch")
        out.append(("pattern_7_ic", stem, en, hi))
    # Rare -ous (pattern 9)
    rare_p9 = """
    androgynous|उभयलिंगी  bipedalous|द्विपाद  cavernous|गुफा जैसा  cavernous|विशाल
    """
    for en, hi in _parse_bulk(rare_p9):
        stem = (en[:-3] + "ös") if en.endswith("ous") else (en + "ös")
        out.append(("pattern_9_ous", stem, en, hi))
    # Rare -ant (pattern 11)
    rare_p11 = """
    accelerant|उत्प्रेरक  accelerant|तेजी  confidant|विश्वासपात्र  covenant|संधि
    """
    for en, hi in _parse_bulk(rare_p11):
        de = "der " + _cap_first(en)
        out.append(("pattern_11_ant", de, en, hi))
    # Rare -ist (pattern 12)
    rare_p12 = """
    allergist|एलर्जी विशेषज्ञ  anaesthetist|बेहोशी विशेषज्ञ  endocrinologist|अंतःस्राव विशेषज्ञ
    geriatrician|वृद्धावस्था विशेषज्ञ  neonatologist|नवजात विशेषज्ञ
    """
    for en, hi in _parse_bulk(rare_p12):
        de = "der " + _cap_first(en)
        out.append(("pattern_12_ist", de, en, hi))
    # Rare -logy (pattern 13)
    rare_p13 = """
    audiology|श्रवण विज्ञान  campanology|घंटा विज्ञान  conchology|शंख विज्ञान
    dendrochronology|वृक्ष कालक्रम  enology|वाइन विज्ञान  escapology|भागने का कौशल
    """
    for en, hi in _parse_bulk(rare_p13):
        de_stem = en.replace("y", "ie") if en.endswith("ology") else (en[:-2] + "ologie")
        de = "die " + _cap_first(de_stem)
        out.append(("pattern_13_logy", de, en, hi))
    # Rare -graphy (pattern 14)
    rare_p14 = """
    angiography|रक्तवाहिका चित्रण  angiography|एंजियोग्राफी  crystallography|स्फटिक विज्ञान
    """
    for en, hi in _parse_bulk(rare_p14):
        de_stem = en.replace("phy", "fie").replace("ography", "ografie")
        de = "die " + _cap_first(de_stem)
        out.append(("pattern_14_graphy", de, en, hi))
    # Rare -meter (pattern 15)
    rare_p15 = """
    accelerometer|त्वरणमापी  densitometer|घनत्वमापी  gravimeter|गुरुत्वमापी
    """
    for en, hi in _parse_bulk(rare_p15):
        de = "der " + _cap_first(en)
        out.append(("pattern_15_meter", de, en, hi))
    # Rare -scope (pattern 16)
    rare_p16 = """
    auriscope|कान दर्शक  auriscope|ऑरिस्कोप  endomicroscope|एंडोमाइक्रोस्कोप
    """
    for en, hi in _parse_bulk(rare_p16):
        de_stem = en.replace("scope", "skop")
        de = "das " + _cap_first(de_stem)
        out.append(("pattern_16_scope", de, en, hi))
    # Rare -phobia (pattern 17)
    rare_p17 = """
    androphobia|पुरुषों का भय  androphobia|पुरुष भय  arachnophobia|मकड़ी का भय
    """
    for en, hi in _parse_bulk(rare_p17):
        de_stem = en.replace("phobia", "phobie")
        de = "die " + _cap_first(de_stem)
        out.append(("pattern_17_phobia", de, en, hi))
    # Rare -phile (pattern 18)
    rare_p18 = """
    halophile|लवणप्रिय  thermophile|उष्माप्रिय  acidophile|अम्लप्रिय
    """
    for en, hi in _parse_bulk(rare_p18):
        de_stem = en.replace("phile", "phil")
        de = "der " + _cap_first(de_stem)
        out.append(("pattern_18_phile", de, en, hi))
    # Rare -age (pattern 19)
    rare_p19 = """
    reportage|रिपोर्ट  reportage|वृत्तांत  triage|ट्रायज  menage|घर
    """
    for en, hi in _parse_bulk(rare_p19):
        de = "die " + _cap_first(en)
        out.append(("pattern_19_age", de, en, hi))
    # Rare -ure (pattern 20)
    rare_p20 = """
    curvature|वक्रता  curvature|मोड़  censure|निंदा  fissure|दरार
    """
    for en, hi in _parse_bulk(rare_p20):
        de = "die " + _cap_first(en)
        out.append(("pattern_20_ure", de, en, hi))
    # Rare -ary/arie (pattern 21)
    rare_p21 = """
    dignitary|गणमान्य  formulary|सूत्रावली  infirmary|चिकित्सालय
    """
    for en, hi in _parse_bulk(rare_p21):
        de_stem = en.replace("ary", "arie").replace("y", "ie")
        de = "die " + _cap_first(de_stem)
        out.append(("pattern_21_ary_arie", de, en, hi))
    # Rare -ate (pattern 22)
    rare_p22 = """
    duplicate|प्रतिलिपि  electorate|मतदाता  mandate|जनादेश  predicate|विधेय
    """
    for en, hi in _parse_bulk(rare_p22):
        de = "der " + _cap_first(en[:-2] + "at") if en.endswith("ate") else "der " + _cap_first(en)
        out.append(("pattern_22_ate", de, en, hi))
    return out


def get_direct_entries_for_3000():
    """Direct [de, en, hi] list to ensure we reach 3000 (unique German forms)."""
    # Format: (cid, de, en, hi) - use German spellings that are standard
    return [
        ("pattern_3_sion_tion", "die Deoxygenierung", "deoxygenation", "अपऑक्सीजनीकरण"),
        ("pattern_3_sion_tion", "die Rekontextualisierung", "recontextualization", "पुनर्संदर्भीकरण"),
        ("pattern_3_sion_tion", "die Entschwefelung", "desulfurization", "गंधक हरण"),
        ("pattern_3_sion_tion", "die Entmineralisierung", "demineralization", "विखनिजीकरण"),
        ("pattern_3_sion_tion", "die Decarboxylierung", "decarboxylation", "डीकार्बोक्सिलीकरण"),
        ("pattern_3_sion_tion", "die Umesterung", "transesterification", "ट्रान्सएस्टरीकरण"),
        ("pattern_3_sion_tion", "die Veresterung", "esterification", "एस्टरीकरण"),
        ("pattern_3_sion_tion", "die Hydroxylierung", "hydroxylation", "हाइड्रॉक्सिलीकरण"),
        ("pattern_3_sion_tion", "die Carboxylierung", "carboxylation", "कार्बोक्सिलीकरण"),
        ("pattern_3_sion_tion", "die Methylierung", "methylation", "मिथाइलेशन"),
        ("pattern_3_sion_tion", "die Glykosylierung", "glycosylation", "ग्लाइकोसिलेशन"),
        ("pattern_3_sion_tion", "die Phosphorylierung", "phosphorylation", "फॉस्फोरिलेशन"),
        ("pattern_3_sion_tion", "die Acetylierung", "acetylation", "एसिटिलेशन"),
        ("pattern_3_sion_tion", "die Alkylierung", "alkylation", "ऐल्किलीकरण"),
        ("pattern_3_sion_tion", "die Nitrierung", "nitration", "नाइट्रेशन"),
        ("pattern_3_sion_tion", "die Sulfonierung", "sulfonation", "सल्फोनेशन"),
        ("pattern_3_sion_tion", "die Halogenierung", "halogenation", "हैलोजनीकरण"),
        ("pattern_3_sion_tion", "die Epoxidierung", "epoxidation", "एपॉक्सीकरण"),
        ("pattern_3_sion_tion", "die Isomerisierung", "isomerization", "समावयवीकरण"),
        ("pattern_3_sion_tion", "die Dimersierung", "dimerization", "डाइमराइजेशन"),
        ("pattern_3_sion_tion", "die Oligomerisierung", "oligomerization", "ऑलिगोमराइजेशन"),
        ("pattern_3_sion_tion", "die Copolymerisation", "copolymerization", "सहबहुलकरण"),
        ("pattern_3_sion_tion", "die Vernetzung", "crosslinking", "क्रॉसलिंकिंग"),
        ("pattern_3_sion_tion", "die Funktionalisierung", "functionalization", "कार्यात्मकीकरण"),
        ("pattern_3_sion_tion", "die Derivatisierung", "derivatization", "व्युत्पत्ति"),
        ("pattern_3_sion_tion", "die Charakterisierung", "characterization", "अभिलक्षण"),
        ("pattern_3_sion_tion", "die Parametrisierung", "parameterization", "पैरामीटरीकरण"),
        ("pattern_3_sion_tion", "die Diskretisierung", "discretization", "विवेकन"),
        ("pattern_3_sion_tion", "die Linearisierung", "linearization", "रैखिकीकरण"),
        ("pattern_3_sion_tion", "die Vektorisierung", "vectorization", "सदिशीकरण"),
        ("pattern_3_sion_tion", "die Parallelisierung", "parallelization", "समानांतरीकरण"),
        ("pattern_4_ty", "die Erweiterbarkeit", "extensibility", "विस्तार योग्यता"),
        ("pattern_4_ty", "die Konfigurierbarkeit", "configurability", "विन्यास योग्यता"),
        ("pattern_4_ty", "die Interoperabilität", "interoperability", "अंतरसंचालन"),
        ("pattern_4_ty", "die Modularität", "modularity", "मॉड्यूलरिटी"),
        ("pattern_4_ty", "die Skalierbarkeit", "scalability", "मापनीयता"),
        ("pattern_4_ty", "die Wartbarkeit", "maintainability", "रखरखाव योग्यता"),
        ("pattern_4_ty", "die Testbarkeit", "testability", "परीक्षण योग्यता"),
        ("pattern_4_ty", "die Einsatzfähigkeit", "deployability", "तैनाती योग्यता"),
        ("pattern_4_ty", "die Wiederverwendbarkeit", "reusability", "पुन: उपयोग"),
        ("pattern_5_ment", "das Einbettung", "embedment", "एम्बेडमेंट"),
        ("pattern_5_ment", "die Ummantelung", "encasement", "आवरण"),
        ("pattern_5_ment", "die Verschanzung", "entrenchment", "मजबूती"),
        ("pattern_5_ment", "der Zuwachs", "increment", "वृद्धि"),
        ("pattern_5_ment", "die Anklage", "indictment", "अभियोग"),
        ("pattern_5_ment", "die Verletzung", "infringement", "उल्लंघन"),
        ("pattern_1_ance_ence", "die Überweisung", "remittance", "भेजी रकम"),
        ("pattern_1_ance_ence", "die Abfindung", "severance", "विच्छेद"),
        ("pattern_1_ance_ence", "die Konsonanz", "consonance", "स्वर सामंजस्य"),
        ("pattern_1_ance_ence", "die Leuchtdichte", "luminance", "चमक"),
        ("pattern_1_ance_ence", "die Rechtswidrigkeit", "malfeasance", "दुराचार"),
        ("pattern_1_ance_ence", "die Irrelevanz", "irrelevance", "अप्रासंगिकता"),
        ("pattern_1_ance_ence", "die Turbulenz", "turbulence", "अशांति"),
        ("pattern_1_ance_ence", "die Varianz", "variance", "अंतर"),
        ("pattern_2_ism", "der Solipsismus", "solipsism", "अहंवाद"),
        ("pattern_2_ism", "der Syllogismus", "syllogism", "न्यायवाक्य"),
        ("pattern_2_ism", "der Nepotismus", "nepotism", "भाई-भतीजावाद"),
        ("pattern_2_ism", "das Prisma", "prism", "प्रिज्म"),
        ("pattern_7_ic", "allelopathisch", "allelopathic", "एलेलोपैथिक"),
        ("pattern_7_ic", "allosterisch", "allosteric", "ऑलोस्टेरिक"),
        ("pattern_7_ic", "anabol", "anabolic", "उपचय"),
        ("pattern_7_ic", "astrophysikalisch", "astrochemical", "खगोल रासायनिक"),
        ("pattern_7_ic", "chemotaktisch", "chemotactic", "कीमोटैक्टिक"),
        ("pattern_8_ive", "abortiv", "abortive", "निष्फल"),
        ("pattern_8_ive", "akkretiv", "accretive", "संचयी"),
        ("pattern_8_ive", "assumptiv", "assumptive", "धारणात्मक"),
        ("pattern_8_ive", "augmentativ", "augmentative", "वर्धक"),
        ("pattern_8_ive", "korrelativ", "correlative", "सहसंबंधी"),
        ("pattern_8_ive", "kurativ", "curative", "उपचारात्मक"),
        ("pattern_8_ive", "deduktiv", "deductive", "निगमनात्मक"),
        ("pattern_8_ive", "diminutiv", "diminutive", "क्षुद्र"),
        ("pattern_9_ous", "androgyn", "androgynous", "उभयलिंगी"),
        ("pattern_9_ous", "kavernös", "cavernous", "गुफा जैसा"),
        ("pattern_11_ant", "der Beschleuniger", "accelerant", "उत्प्रेरक"),
        ("pattern_11_ant", "der Vertraute", "confidant", "विश्वासपात्र"),
        ("pattern_12_ist", "der Allergologe", "allergist", "एलर्जी विशेषज्ञ"),
        ("pattern_12_ist", "der Anästhesist", "anaesthetist", "बेहोशी विशेषज्ञ"),
        ("pattern_12_ist", "der Endokrinologe", "endocrinologist", "अंतःस्राव विशेषज्ञ"),
        ("pattern_12_ist", "der Geriater", "geriatrician", "वृद्धावस्था विशेषज्ञ"),
        ("pattern_12_ist", "der Neonatologe", "neonatologist", "नवजात विशेषज्ञ"),
        ("pattern_13_logy", "die Audiologie", "audiology", "श्रवण विज्ञान"),
        ("pattern_13_logy", "die Kampanologie", "campanology", "घंटा विज्ञान"),
        ("pattern_13_logy", "die Konchologie", "conchology", "शंख विज्ञान"),
        ("pattern_13_logy", "die Dendrochronologie", "dendrochronology", "वृक्ष कालक्रम"),
        ("pattern_13_logy", "die Önologie", "enology", "वाइन विज्ञान"),
        ("pattern_13_logy", "die Eskapologie", "escapology", "भागने का कौशल"),
        ("pattern_14_graphy", "die Angiografie", "angiography", "रक्तवाहिका चित्रण"),
        ("pattern_14_graphy", "die Kristallografie", "crystallography", "स्फटिक विज्ञान"),
        ("pattern_15_meter", "der Beschleunigungsmesser", "accelerometer", "त्वरणमापी"),
        ("pattern_15_meter", "der Densitometer", "densitometer", "घनत्वमापी"),
        ("pattern_15_meter", "das Gravimeter", "gravimeter", "गुरुत्वमापी"),
        ("pattern_16_scope", "das Auriskop", "auriscope", "कान दर्शक"),
        ("pattern_16_scope", "das Endomikroskop", "endomicroscope", "एंडोमाइक्रोस्कोप"),
        ("pattern_17_phobia", "die Androphobie", "androphobia", "पुरुषों का भय"),
        ("pattern_18_phile", "der Halophil", "halophile", "लवणप्रिय"),
        ("pattern_18_phile", "der Acidophil", "acidophile", "अम्लप्रिय"),
        ("pattern_19_age", "die Triage", "triage", "ट्रायज"),
        ("pattern_19_age", "die Ménage", "menage", "घर"),
        ("pattern_20_ure", "die Zensur", "censure", "निंदा"),
        ("pattern_20_ure", "die Fissur", "fissure", "दरार"),
        ("pattern_21_ary_arie", "die Diktionarie", "dictionary", "शब्दकोश"),
        ("pattern_22_ate", "der Duplikat", "duplicate", "प्रतिलिपि"),
        # More to reach 3000
        ("pattern_3_sion_tion", "die Kompostierung", "composting", "कम्पोस्टिंग"),
        ("pattern_3_sion_tion", "die Verflüssigung", "liquefaction", "द्रवीकरण"),
        ("pattern_3_sion_tion", "die Vergasung", "gasification", "गैसीकरण"),
        ("pattern_3_sion_tion", "die Verkohlung", "carbonization", "कार्बनीकरण"),
        ("pattern_3_sion_tion", "die Verkieselung", "silicification", "सिलिकीकरण"),
        ("pattern_3_sion_tion", "die Verkalkung", "calcification", "कैल्सीकरण"),
        ("pattern_3_sion_tion", "die Verfestigung", "solidification", "ठोसीकरण"),
        ("pattern_3_sion_tion", "die Verflüchtigung", "volatilization", "वाष्पीकरण"),
        ("pattern_3_sion_tion", "die Veraschung", "incineration", "भस्मीकरण"),
        ("pattern_3_sion_tion", "die Versinterung", "sintering", "सिंटरिंग"),
        ("pattern_4_ty", "die Nachvollziehbarkeit", "traceability", "अनुरेखणीयता"),
        ("pattern_4_ty", "die Übertragbarkeit", "transferability", "हस्तांतरणीयता"),
        ("pattern_4_ty", "die Übersetzbarkeit", "translatability", "अनुवाद योग्यता"),
        ("pattern_4_ty", "die Behandelbarkeit", "treatability", "उपचार योग्यता"),
        ("pattern_4_ty", "die Rückverfolgbarkeit", "traceability", "अनुरेखण"),
        ("pattern_5_ment", "das Abkommen", "agreement", "समझौता"),
        ("pattern_5_ment", "das Aufkommen", "revenue", "राजस्व"),
        ("pattern_5_ment", "das Nachkommen", "descendant", "वंशज"),
        ("pattern_5_ment", "das Vorhaben", "project", "परियोजना"),
        ("pattern_1_ance_ence", "die Toleranz", "tolerance", "सहनशीलता"),
        ("pattern_1_ance_ence", "die Relevanz", "relevance", "प्रासंगिकता"),
        ("pattern_2_ism", "der Tribalismus", "tribalism", "जनजातिवाद"),
        ("pattern_2_ism", "der Exotismus", "exoticism", "विदेशीपन"),
        ("pattern_6_al", "das Entfernen", "removal", "हटाना"),
        ("pattern_6_al", "das Überleben", "survival", "उत्तरजीविता"),
        ("pattern_7_ic", "photovoltaisch", "photovoltaic", "फोटोवोल्टेइक"),
        ("pattern_7_ic", "piezoelektrisch", "piezoelectric", "पीजोइलेक्ट्रिक"),
        ("pattern_7_ic", "pyroelektrisch", "pyroelectric", "पायरोइलेक्ट्रिक"),
        ("pattern_7_ic", "thermoelektrisch", "thermoelectric", "थर्मोइलेक्ट्रिक"),
        ("pattern_8_ive", "additiv", "additive", "योजक"),
        ("pattern_8_ive", "adhesiv", "adhesive", "चिपकने वाला"),
        ("pattern_9_ous", "synonym", "synonymous", "समानार्थी"),
        ("pattern_10_ary", "sekundär", "secondary", "माध्यमिक"),
        ("pattern_10_ary", "primär", "primary", "प्राथमिक"),
        ("pattern_11_ant", "der Konsonant", "consonant", "व्यंजन"),
        ("pattern_11_ant", "der Diamant", "diamond", "हीरा"),
        ("pattern_12_ist", "der Geochemiker", "geochemist", "भूरसायनज्ञ"),
        ("pattern_12_ist", "der Astrobiologe", "astrobiologist", "खगोल जीवविज्ञानी"),
        ("pattern_13_logy", "die Toxikologie", "toxicology", "विष विज्ञान"),
        ("pattern_13_logy", "die Virologie", "virology", "वायरोलॉजी"),
        ("pattern_14_graphy", "die Mammografie", "mammography", "मैमोग्राफी"),
        ("pattern_14_graphy", "die Sonografie", "sonography", "अल्ट्रासाउंड"),
        ("pattern_15_meter", "der Lactometer", "lactometer", "दूध मापक"),
        ("pattern_15_meter", "der Odometer", "odometer", "ओडोमीटर"),
        ("pattern_16_scope", "das Stethoskop", "stethoscope", "स्टेथोस्कोप"),
        ("pattern_16_scope", "das Mikroskop", "microscope", "सूक्ष्मदर्शी"),
        ("pattern_17_phobia", "die Akrophobie", "acrophobia", "ऊंचाई का भय"),
        ("pattern_17_phobia", "die Klaustrophobie", "claustrophobia", "संकीर्ण स्थान का भय"),
        ("pattern_18_phile", "der Bibliophil", "bibliophile", "पुस्तक प्रेमी"),
        ("pattern_19_age", "die Spionage", "espionage", "जासूसी"),
        ("pattern_19_age", "die Sabotage", "sabotage", "तोड़फोड़"),
        ("pattern_20_ure", "die Mischung", "mixture", "मिश्रण"),
        ("pattern_20_ure", "die Feuchtigkeit", "moisture", "नमी"),
        ("pattern_21_ary_arie", "die Sekretarie", "secretary", "सचिव"),
        ("pattern_22_ate", "der Automat", "automaton", "स्वचालित"),
        # Final batch to reach 3000 (unique terms)
        ("pattern_3_sion_tion", "die Pyrolyse", "pyrolysis", "पायरोलिसिस"),
        ("pattern_3_sion_tion", "die Hydrolyse", "hydrolysis", "जलअपघटन"),
        ("pattern_3_sion_tion", "die Elektrolyse", "electrolysis", "विद्युत अपघटन"),
        ("pattern_3_sion_tion", "die Analyse", "analysis", "विश्लेषण"),
        ("pattern_3_sion_tion", "die Katalyse", "catalysis", "उत्प्रेरण"),
        ("pattern_3_sion_tion", "die Dialyse", "dialysis", "डायलिसिस"),
        ("pattern_3_sion_tion", "die Paralysis", "paralysis", "लकवा"),
        ("pattern_3_sion_tion", "die Metabolisierung", "metabolization", "चयापचय"),
        ("pattern_3_sion_tion", "die Immobilisierung", "immobilization", "अचलन"),
        ("pattern_3_sion_tion", "die Granulierung", "granulation", "दानेदार बनाना"),
        ("pattern_3_sion_tion", "die Pelletierung", "pelleting", "पेलेटिंग"),
        ("pattern_3_sion_tion", "die Mikroverkapselung", "microencapsulation", "माइक्रोएनकैप्सुलेशन"),
        ("pattern_3_sion_tion", "die Nanofiltration", "nanofiltration", "नैनोफिल्ट्रेशन"),
        ("pattern_3_sion_tion", "die Ultrafiltration", "ultrafiltration", "अल्ट्राफिल्ट्रेशन"),
        ("pattern_3_sion_tion", "die Umkehrosmose", "reverse osmosis", "उत्क्रम परासरण"),
        ("pattern_3_sion_tion", "die Elektrodialyse", "electrodialysis", "इलेक्ट्रोडायलिसिस"),
        ("pattern_4_ty", "die Biokompatibilität", "biocompatibility", "जैव अनुकूलता"),
        ("pattern_4_ty", "die Hämokompatibilität", "hemocompatibility", "रक्त अनुकूलता"),
        ("pattern_4_ty", "die Sterilisierbarkeit", "sterilizability", "बाँझनीयता"),
        ("pattern_4_ty", "die Autoklavierbarkeit", "autoclavability", "ऑटोक्लेव योग्यता"),
        ("pattern_5_ment", "das Sediment", "sediment", "तलछट"),
        ("pattern_5_ment", "das Pigment", "pigment", "वर्णक"),
        ("pattern_5_ment", "das Reagenz", "reagent", "अभिकर्मक"),
        ("pattern_5_ment", "das Detergens", "detergent", "डिटर्जेंट"),
        ("pattern_5_ment", "das Tensid", "surfactant", "सर्फेक्टेंट"),
        ("pattern_1_ance_ence", "die Koexistenz", "coexistence", "सहअस्तित्व"),
        ("pattern_1_ance_ence", "die Interdependenz", "interdependence", "अंतर्निर्भरता"),
        ("pattern_1_ance_ence", "die Konfluenz", "confluence", "संगम"),
        ("pattern_2_ism", "der Exotismus", "exoticism", "विदेशीपन"),
        ("pattern_2_ism", "der Euphemismus", "euphemism", "प्रेयोक्ति"),
        ("pattern_6_al", "das Rektal", "rectal", "मलाशय"),
        ("pattern_6_al", "das Nasal", "nasal", "नाक"),
        ("pattern_7_ic", "endotherm", "endothermic", "ऊष्माशोषी"),
        ("pattern_7_ic", "exotherm", "exothermic", "ऊष्माक्षेपी"),
        ("pattern_7_ic", "isotherm", "isothermal", "समतापी"),
        ("pattern_7_ic", "adiabatisch", "adiabatic", "रुद्धोष्म"),
        ("pattern_8_ive", "konvulsiv", "convulsive", "ऐंठन"),
        ("pattern_8_ive", "implosiv", "implosive", "अंतर्विस्फोटक"),
        ("pattern_9_ous", "nekrotisch", "necrotic", "नेक्रोटिक"),
        ("pattern_10_ary", "tertiär", "tertiary", "तृतीयक"),
        ("pattern_11_ant", "der Oxidant", "oxidant", "ऑक्सीकरण"),
        ("pattern_11_ant", "der Reduktant", "reductant", "अपचायक"),
        ("pattern_12_ist", "der Virologe", "virologist", "वायरोलॉजिस्ट"),
        ("pattern_12_ist", "der Toxikologe", "toxicologist", "विष विज्ञानी"),
        ("pattern_13_logy", "die Nanotechnologie", "nanotechnology", "नैनोतकनीक"),
        ("pattern_13_logy", "die Bionik", "bionics", "जैवअभियांत्रिकी"),
        ("pattern_14_graphy", "die Thermografie", "thermography", "थर्मोग्राफी"),
        ("pattern_14_graphy", "die Fluorografie", "fluorography", "फ्लोरोग्राफी"),
        ("pattern_15_meter", "der pH-Meter", "pH meter", "pH मीटर"),
        ("pattern_15_meter", "der Turbidimeter", "turbidimeter", "टर्बिडिमीटर"),
        ("pattern_16_scope", "das Kolposkop", "colposcope", "कॉलपोस्कोप"),
        ("pattern_16_scope", "das Laryngoskop", "laryngoscope", "स्वर यंत्र दर्शक"),
        ("pattern_17_phobia", "die Hemophobie", "hemophobia", "खून का भय"),
        ("pattern_17_phobia", "die Trypanophobie", "trypanophobia", "इंजेक्शन का भय"),
        ("pattern_18_phile", "der Xerophil", "xerophile", "शुष्कप्रिय"),
        ("pattern_19_age", "die Tonnage", "tonnage", "टन भार"),
        ("pattern_20_ure", "die Kompositur", "composite", "मिश्रित"),
        ("pattern_21_ary_arie", "die Vokabularie", "vocabulary", "शब्दावली"),
        ("pattern_22_ate", "der Klerikat", "clericate", "पादरी"),
    ]


def get_all_candidates_from_builders():
    """Run each pattern builder and collect (cid, de, en, hi)."""
    sys.path.insert(0, BASE)
    import create_10k_extended as c10
    builders = {
        "pattern_1_ance_ence": c10._build_pattern_1,
        "pattern_2_ism": c10._build_pattern_2,
        "pattern_3_sion_tion": c10._build_pattern_3,
        "pattern_4_ty": c10._build_pattern_4,
        "pattern_5_ment": c10._build_pattern_5,
        "pattern_6_al": c10._build_pattern_6,
        "pattern_7_ic": c10._build_pattern_7,
        "pattern_8_ive": c10._build_pattern_8,
        "pattern_9_ous": c10._build_pattern_9,
        "pattern_10_ary": c10._build_pattern_10,
        "pattern_11_ant": c10._build_pattern_11,
        "pattern_12_ist": c10._build_pattern_12,
        "pattern_13_logy": c10._build_pattern_13,
        "pattern_14_graphy": c10._build_pattern_14,
        "pattern_15_meter": c10._build_pattern_15,
        "pattern_16_scope": c10._build_pattern_16,
        "pattern_17_phobia": c10._build_pattern_17,
        "pattern_18_phile": c10._build_pattern_18,
        "pattern_19_age": c10._build_pattern_19,
        "pattern_20_ure": c10._build_pattern_20,
        "pattern_21_ary_arie": c10._build_pattern_21,
        "pattern_22_ate": c10._build_pattern_22,
    }
    candidates = []
    for cid, builder in builders.items():
        try:
            for (de, en, hi) in builder():
                candidates.append((cid, de.strip(), en.strip(), hi.strip()))
        except Exception as e:
            print(f"Warning: {cid} builder failed: {e}", file=sys.stderr)
    return candidates


def main():
    with open(VOCAB_JSON, "r", encoding="utf-8") as f:
        obj = json.load(f)
    current_total = obj.get("totalWords", 0)
    need = TARGET_TOTAL - current_total
    if need <= 0:
        print(f"Already at or above {TARGET_TOTAL} words ({current_total}). Nothing to add.")
        return

    print(f"Current total: {current_total}. Need to add {need} words to reach {TARGET_TOTAL}.")

    existing_de = load_existing_de()
    print(f"Existing German entries: {len(existing_de)}")

    # Also consider words already in extended_extra so we don't double-add
    extra_de = set()
    if os.path.isfile(EXTRA_JSON):
        with open(EXTRA_JSON, "r", encoding="utf-8") as f:
            extra_data = json.load(f)
        for cid, arr in extra_data.items():
            for triple in arr:
                if len(triple) >= 1:
                    extra_de.add((triple[0] or "").strip().lower())
    skip_de = existing_de | extra_de

    candidates = get_all_candidates_from_builders()
    # Add extra from bulk (en|hi) and rare words to reach 3000
    try:
        candidates.extend(get_additional_bulk_candidates())
    except Exception as e:
        print(f"Warning: additional bulk failed: {e}", file=sys.stderr)
    try:
        candidates.extend(get_rare_candidates())
    except Exception as e:
        print(f"Warning: rare candidates failed: {e}", file=sys.stderr)
    try:
        candidates.extend(get_direct_entries_for_3000())
    except Exception as e:
        print(f"Warning: direct entries failed: {e}", file=sys.stderr)
    # Filter: de not already in vocab or in extended_extra
    new_list = []
    seen_de = set()
    for cid, de, en, hi in candidates:
        de_norm = (de or "").strip().lower()
        if not de_norm or de_norm in skip_de or de_norm in seen_de:
            continue
        seen_de.add(de_norm)
        new_list.append((cid, (de or "").strip(), (en or "").strip(), (hi or "").strip()))

    print(f"Candidates not in vocab: {len(new_list)}")

    if len(new_list) < need:
        print(f"Only {len(new_list)} new candidates available; adding all.")

    to_take = min(need, len(new_list))
    by_cid = {}
    for i in range(to_take):
        cid, de, en, hi = new_list[i]
        by_cid.setdefault(cid, []).append([de, en, hi])
    to_add = by_cid
    added_total = sum(len(arr) for arr in to_add.values())
    if added_total == 0:
        print("No new words to add (all candidates already in vocab or extended_extra).")
        return

    # Merge with existing extended_extra.json
    if os.path.isfile(EXTRA_JSON):
        with open(EXTRA_JSON, "r", encoding="utf-8") as f:
            extra_data = json.load(f)
    else:
        extra_data = {}
    for cid, arr in to_add.items():
        extra_data.setdefault(cid, []).extend(arr)
    with open(EXTRA_JSON, "w", encoding="utf-8") as f:
        json.dump(extra_data, f, ensure_ascii=False, indent=2)

    print(f"Added {added_total} new entries to {EXTRA_JSON}.")

    # Run build_word_patterns.py to regenerate vocabulary
    build_script = os.path.join(BASE, "build_word_patterns.py")
    r = subprocess.run([sys.executable, build_script], cwd=BASE)
    if r.returncode != 0:
        print("build_word_patterns.py failed.", file=sys.stderr)
        sys.exit(1)
    with open(VOCAB_JSON, "r", encoding="utf-8") as f:
        obj = json.load(f)
    print(f"Vocabulary now has {obj['totalWords']} words.")


if __name__ == "__main__":
    main()
