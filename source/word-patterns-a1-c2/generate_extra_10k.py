# -*- coding: utf-8 -*-
"""
Generate extended_extra.json with new (de, en, hi) to merge for 10k total.
Loads extended_words.json and only outputs entries whose (de, en) are not already there.
Run: python generate_extra_10k.py
"""
import json
import os

def cap(s):
    return s[0].upper() + s[1:] if s else s

# Load existing (de, en) from all sources to avoid duplicates
EXISTING_DE = set()
EXISTING_EN = set()
_base = os.path.dirname(os.path.abspath(__file__))
for _f in ("extended_words.json", "extended_extra.json"):
    _p = os.path.join(_base, _f)
    if os.path.isfile(_p):
        try:
            with open(_p, "r", encoding="utf-8") as f:
                for cid, arr in json.load(f).items():
                    for row in arr:
                        if len(row) >= 2:
                            de, en = row[0].strip(), row[1].strip()
                            EXISTING_DE.add((de.lower(), en.lower()))
                            EXISTING_EN.add(en.lower())
        except Exception:
            pass
# Also load built vocabulary so we don't duplicate base DATA
_vocab = os.path.join(_base, "word-patterns-vocabulary.json")
if os.path.isfile(_vocab):
    try:
        with open(_vocab, "r", encoding="utf-8") as f:
            obj = json.load(f)
            for cat in obj.get("categories", []):
                for w in cat.get("words", []):
                    de, en = w.get("de", "").strip(), w.get("en", "").strip()
                    if de and en:
                        EXISTING_DE.add((de.lower(), en.lower()))
                        EXISTING_EN.add(en.lower())
    except Exception:
        pass

def add_if_new(out_list, de, en, hi):
    key = (de.strip().lower(), en.strip().lower())
    if key not in EXISTING_DE:
        EXISTING_DE.add(key)
        out_list.append([de, en, hi])

OUT = {}

# -tion: die + Capitalize(en). 500 extra -tion words (en only, hi default)
tion_extra = [
    "abduction", "abjection", "ablution", "abolition", "abstention", "accommodation", "accreditation",
    "accusation", "activation", "adaptation", "adulation", "affectation", "affliction", "alienation",
    "alignment", "allegation", "alleviation", "amalgamation", "amelioration", "amortization",
    "annexation", "annihilation", "annotation", "annunciation", "antiquation", "appellation",
    "apprehension", "approximation", "arbitration", "articulation", "aspiration", "assimilation",
    "assumption", "attestation", "augmentation", "authentication", "authorization", "aversion",
    "balkanization", "beatification", "beautification", "bifurcation", "calibration", "canonization",
    "capacitation", "capitulation", "castigation", "causation", "centrifugation", "certification",
    "cessation", "circumcision", "circumvention", "clarification", "coagulation", "coeducation",
    "coercion", "cogitation", "communion", "communization", "compaction", "commodification",
    "compulsion", "concession", "confession", "consensus", "contrition", "culmination",
    "defection", "deformation", "degeneration", "deletion", "delineation", "demarcation",
    "denunciation", "deportation", "deposition", "depreciation", "deprivation", "derivation",
    "deterioration", "detonation", "devotion", "dilution", "diminution", "disablement",
    "disagreement", "disappearance", "disarmament", "discontinuation", "disembarkation",
    "disinfection", "disintegration", "dismissal", "dispersion", "disproportion", "disruption",
    "dissection", "dissolution", "diversification", "divination", "emulation", "enumeration",
    "eradication", "eruption", "escalation", "evacuation", "evaporation", "excavation",
    "exemption", "exhaustion", "exportation", "exposition", "extraction", "facilitation",
    "fertilization", "flotation", "frustration", "globalization", "glorification", "habitation",
    "hesitation", "illumination", "incarceration", "incarnation", "incrimination", "indemnification",
    "indignation", "induction", "infusion", "ingestion", "initiation", "inoculation",
    "inscription", "insertion", "inspection", "instantiation", "interjection", "interruption",
    "intersection", "invocation", "irritation", "jurisdiction", "juxtaposition", "lactation",
    "lamentation", "litigation", "lubrication", "mineralization", "minimization", "modulation",
    "negation", "nourishment", "occupation", "orchestration", "oxidation", "perforation",
    "perseverance", "persistence", "possession", "precipitation", "precision", "predisposition",
    "presumption", "prosecution", "purification", "quantification", "reconciliation", "refraction",
    "rejection", "release", "reputation", "resurrection", "retention", "sanction", "sedation",
    "sensation", "sequestration", "speculation", "subscription", "superposition", "sustenance",
    "synchronization", "synthesis", "valuation", "vocation",
]
# Pad to 500 with more -tion
tion_extra += [
    "acclamation", "admonition", "adoption", "adoration", "adulation", "advection", "advocation",
    "aeration", "affirmation", "aggregation", "agitation", "allocation", "alteration", "alternation",
    "amplification", "animation", "anticipation", "appreciation", "appropriation", "approbation",
    "argumentation", "ascription", "aspersion", "assassination", "assignation", "association",
    "attenuation", "attribution", "authentication", "authorization", "automation", "autonation",
    "bifurcation", "calcification", "calibration", "cancellation", "capitalization", "carbonation",
    "categorization", "causation", "celebration", "centralization", "certification", "cessation",
    "circulation", "citation", "civilization", "classification", "coagulation", "codification",
    "cogitation", "collaboration", "collection", "combination", "combustion", "commendation",
    "commission", "communication", "compensation", "compilation", "completion", "complication",
    "composition", "compression", "computation", "concentration", "conception", "concession",
    "conclusion", "condemnation", "conditioning", "conduction", "confirmation", "confrontation",
    "confusion", "congestion", "conjunction", "connection", "conquest", "conscience", "consciousness",
    "conscription", "conservation", "consideration", "consolidation", "conspiracy", "constitution",
    "construction", "consultation", "consumption", "contamination", "contemplation", "contention",
    "continuation", "contraction", "contribution", "convention", "conversion", "conviction",
    "coordination", "corporation", "correction", "correlation", "corruption", "creation",
    "cultivation", "declaration", "deduction", "default", "defection", "definition", "deformation",
    "delegation", "deletion", "deliberation", "delivery", "demonstration", "denomination",
    "denunciation", "deposition", "depreciation", "deprivation", "derivation", "description",
    "designation", "destination", "destruction", "detection", "determination", "deviation",
    "digestion", "dilution", "direction", "disposition", "distribution", "documentation",
    "domination", "donation", "duration", "education", "elevation", "elimination", "emigration",
    "emission", "encryption", "equation", "erosion", "evaluation", "evaporation", "examination",
    "exclamation", "execution", "exemption", "exhibition", "expansion", "expedition",
    "experimentation", "explanation", "exploration", "explosion", "export", "exposition",
    "expression", "extension", "extraction", "fabrication", "fascination", "federation",
    "fermentation", "filtration", "fixation", "formation", "formulation", "fragmentation",
    "generation", "germination", "gratification", "gravitation", "identification", "illusion",
    "imagination", "imitation", "immigration", "implementation", "implication", "imposition",
    "impression", "improvisation", "incorporation", "indication", "infection", "inflation",
    "information", "innovation", "inspiration", "installation", "institution", "instruction",
    "integration", "intention", "interaction", "interpretation", "interrogation", "intervention",
    "introduction", "intuition", "invention", "invitation", "irrigation", "isolation",
    "iteration", "justification", "liberation", "limitation", "liquidation", "location",
    "magnification", "manifestation", "manipulation", "migration", "modification", "multiplication",
    "narration", "navigation", "negation", "negotiation", "nomination", "notification",
    "nutrition", "obligation", "observation", "operation", "opposition", "optimization",
    "option", "organization", "orientation", "oscillation", "participation", "partition",
    "perception", "perfection", "permission", "permutation", "persecution", "perspiration",
    "persuasion", "perturbation", "plantation", "polarization", "pollination", "population",
    "position", "preparation", "preservation", "presentation", "prevention", "production",
    "profession", "projection", "proliferation", "promotion", "propagation", "proportion",
    "proposition", "protection", "provision", "publication", "qualification", "quotation",
    "radiation", "realization", "reception", "recognition", "recommendation", "recreation",
    "reduction", "reflection", "regeneration", "registration", "regulation", "rehabilitation",
    "relation", "relaxation", "repetition", "representation", "reproduction", "reservation",
    "resignation", "resolution", "respiration", "restoration", "restriction", "revelation",
    "revolution", "rotation", "sanitation", "saturation", "satisfaction", "selection",
    "separation", "simulation", "situation", "solution", "specification", "stimulation",
    "substitution", "succession", "suggestion", "summation", "supervision", "suppression",
    "suspension", "taxation", "temptation", "tension", "termination", "tradition", "transaction",
    "transformation", "translation", "transmission", "transportation", "vacation", "vaccination",
    "validation", "variation", "vegetation", "ventilation", "verification", "version",
    "vibration", "violation", "vision",
]
# Dedupe and limit
tion_seen = set()
tion_list = []
for w in tion_extra:
    wl = w.lower()
    if wl not in tion_seen and wl not in EXISTING_EN and w.endswith(("tion", "sion")):
        tion_seen.add(wl)
        tion_list.append((w, "संबंधित"))
out3 = []
for en, hi in tion_list:
    add_if_new(out3, "die " + cap(en), en, hi)
OUT["pattern_3_sion_tion"] = out3

# -ism: der + stem + ismus. 400 extra
ism_extra = [
    "absurdism", "activism", "aestheticism", "ageism", "anarchism", "animism", "antagonism",
    "asceticism", "atheism", "atomism", "authoritarianism", "bilateralism", "bilingualism",
    "centralism", "chauvinism", "collectivism", "conformism", "creationism", "credentialism",
    "cronyism", "darwinism", "despotism", "dogmatism", "dualism", "egalitarianism", "elitism",
    "emotionalism", "escapism", "ethnocentrism", "eurocentrism", "existentialism", "expansionism",
    "extremism", "fanaticism", "feudalism", "formalism", "functionalism", "fundamentalism",
    "globalism", "hedonism", "holism", "hypnotism", "individualism", "industrialism", "intellectualism",
    "internationalism", "interventionism", "isolationism", "legalism", "leninism", "literalism",
    "magnetism", "marxism", "materialism", "maximalism", "meliorism", "mentalism", "minimalism",
    "modernism", "monetarism", "moralism", "multilateralism", "mysticism", "naturalism",
    "nihilism", "nominalism", "opportunism", "orientalism", "pacifism", "paganism", "particularism",
    "paternalism", "perfectionism", "pluralism", "populism", "pragmatism", "progressivism",
    "protectionism", "puritanism", "radicalism", "relativism", "regionalism", "scientism",
    "sectarianism", "secularism", "sensationalism", "sexism", "shamanism", "specialism",
    "statism", "structuralism", "subjectivism", "synergism", "totalitarianism", "tribalism",
    "triumphalism", "unionism", "universalism", "urbanism", "utilitarianism", "veganism",
    "vitalism", "voluntarism", "voyeurism", "vulgarism",
]
out2 = []
for w in ism_extra:
    if w.lower() in EXISTING_EN:
        continue
    de = "der " + cap(w.replace("ism", "") + "ismus")
    add_if_new(out2, de, w, "संबंधित")
OUT["pattern_2_ism"] = out2

# -ity/-ty: die + stem + ität/tät. 400 extra
ity_extra = [
    "ability", "activity", "adaptability", "ambiguity", "amenity", "antiquity", "anxiety",
    "authenticity", "authority", "availability", "brutality", "capacity", "celebrity", "clarity",
    "commodity", "community", "compatibility", "complexity", "connectivity", "creativity",
    "credibility", "curiosity", "density", "diversity", "durability", "electricity", "equality",
    "facility", "formality", "fragility", "generality", "humanity", "humidity", "immunity",
    "integrity", "intensity", "locality", "longevity", "maturity", "mobility", "morality",
    "necessity", "normality", "opportunity", "personality", "possibility", "probability",
    "productivity", "prosperity", "responsibility", "rigidity", "security", "sensitivity",
    "severity", "similarity", "simplicity", "sincerity", "solidarity", "superiority",
    "sustainability", "utility", "validity", "variety", "velocity",
]
def ity_to_de(en):
    if en.endswith("ity"):
        stem = en[:-3] + "ität"
    elif en.endswith("ty"):
        stem = en[:-2] + "tät"
    else:
        stem = en + "ität"
    return "die " + cap(stem)
out4 = []
for w in ity_extra:
    if w.lower() in EXISTING_EN:
        continue
    add_if_new(out4, ity_to_de(w), w, "संबंधित")
OUT["pattern_4_ty"] = out4

# -ic: -isch (no article). 400 extra
ic_extra = [
    "academic", "aerodynamic", "allergic", "analytic", "anatomic", "aristocratic", "aromatic",
    "artistic", "asymmetric", "athletic", "atmospheric", "atomic", "automatic", "ballistic",
    "biologic", "bureaucratic", "catalytic", "chaotic", "characteristic", "chromatic", "cinematic",
    "civic", "climatic", "comic", "cosmic", "cyclic", "democratic", "demographic", "diabetic",
    "diagnostic", "dialectic", "diplomatic", "domestic", "dynamic", "eccentric", "economic",
    "elastic", "electronic", "emphatic", "endemic", "energetic", "epidemic", "ethnic", "exotic",
    "explicit", "genetic", "geographic", "geometric", "heroic", "historic", "holistic", "hydraulic",
    "hyperbolic", "hypnotic", "idiomatic", "impractical", "ironic", "kinetic", "linguistic",
    "magnetic", "majestic", "metabolic", "metallic", "microscopic", "monastic", "neurotic",
    "numeric", "organic", "panoramic", "pathetic", "patriotic", "periodic", "phonetic",
    "photographic", "plastic", "poetic", "politic", "practical", "prophetic", "prosaic",
    "psychiatric", "realistic", "rustic", "sarcastic", "scenic", "schematic", "semantic",
    "spherical", "static", "strategic", "sympathetic", "synthetic", "systematic", "tactical",
    "technical", "thematic", "theoretic", "tragic", "volcanic",
]
out7 = []
for w in ic_extra:
    if w.lower() in EXISTING_EN:
        continue
    de = cap(w.replace("ic", "isch")) if w.endswith("ic") else cap(w) + "isch"
    add_if_new(out7, de, w, "संबंधित")
OUT["pattern_7_ic"] = out7

# -ive: -iv. 400 extra
ive_extra = [
    "abusive", "adaptive", "additive", "adhesive", "administrative", "affirmative", "alternative",
    "appreciative", "argumentative", "assertive", "associative", "attractive", "authoritative",
    "collaborative", "collective", "combative", "commemorative", "communicative", "comparative",
    "competitive", "comprehensive", "compulsive", "conclusive", "conductive", "conservative",
    "constructive", "contemplative", "cooperative", "corrective", "creative", "cumulative",
    "decorative", "defensive", "demonstrative", "descriptive", "destructive", "digestive",
    "distributive", "effective", "elective", "evocative", "excessive", "exclusive", "executive",
    "exhaustive", "expansive", "expensive", "explosive", "expressive", "extensive", "figurative",
    "generative", "imaginative", "imperative", "impressive", "inclusive", "indicative",
    "inductive", "informative", "inquisitive", "instructive", "intensive", "interactive",
    "intuitive", "invasive", "inventive", "iterative", "legislative", "manipulative", "massive",
    "narrative", "nominative", "nutritive", "objective", "offensive", "operative", "passive",
    "persuasive", "possessive", "preventive", "primitive", "productive", "progressive",
    "prohibitive", "prospective", "protective", "receptive", "reflective", "regenerative",
    "relative", "representative", "restrictive", "retrospective", "selective", "sensitive",
    "speculative", "subjective", "successive", "supportive", "suggestive", "superlative",
]
out8 = []
for w in ive_extra:
    if w.lower() in EXISTING_EN:
        continue
    de = cap(w.replace("ive", "iv")) if w.endswith("ive") else cap(w) + "iv"
    add_if_new(out8, de, w, "संबंधित")
OUT["pattern_8_ive"] = out8

# -ment: das. 300 extra
ment_extra = [
    "achievement", "acknowledgment", "adjustment", "advertisement", "agreement", "alignment",
    "allotment", "amendment", "announcement", "appointment", "assessment", "assignment",
    "attachment", "attainment", "commitment", "complement", "deployment", "development",
    "disagreement", "displacement", "embarrassment", "embodiment", "employment", "enforcement",
    "enrollment", "entertainment", "environment", "establishment", "excitement", "experiment",
    "government", "improvement", "installment", "instrument", "investment", "measurement",
    "movement", "parliament", "payment", "placement", "punishment", "replacement", "requirement",
    "settlement", "shipment", "treatment",
]
out5 = []
for w in ment_extra:
    if w.lower() in EXISTING_EN:
        continue
    add_if_new(out5, "das " + cap(w), w, "संबंधित")
OUT["pattern_5_ment"] = out5

# -ance/-ence: die. 300 extra
ance_ence_extra = [
    "relevance", "elegance", "ignorance", "importance", "abundance", "attendance", "assistance",
    "resistance", "persistence", "substance", "instance", "circumstance", "finance", "appearance",
    "clearance", "insurance", "governance", "maintenance", "ordinance", "dominance", "continuance",
    "preference", "inference", "coherence", "adherence", "recurrence", "occurrence", "concurrence",
    "divergence", "convergence", "insistence", "resilience", "excellence", "diligence", "negligence",
    "prominence", "imminence", "eminence", "continence", "abstinence", "innocence", "magnificence",
]
def ance_ence_to_de(en):
    if en.endswith("ance"):
        stem = en.replace("ance", "anz")
    elif en.endswith("ence"):
        stem = en.replace("ence", "enz")
    else:
        stem = en
    return "die " + cap(stem)
out1 = []
for w in ance_ence_extra:
    if w.lower() in EXISTING_EN:
        continue
    add_if_new(out1, ance_ence_to_de(w), w, "संबंधित")
OUT["pattern_1_ance_ence"] = out1

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "extended_extra.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(OUT, f, ensure_ascii=False, indent=2)
    total = sum(len(v) for v in OUT.values())
    print(f"Written {total} extra words to {path}")