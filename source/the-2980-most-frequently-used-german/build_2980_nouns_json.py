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
    entries = full_list
    print(f"Total entries: {len(entries)}")
    # Assign categories
    by_category = defaultdict(list)
    for e in entries:
        cat = assign_category(e["en"], e.get("de"))
        by_category[cat].append(e)
    for cat in by_category:
        by_category[cat].sort(key=lambda x: x["rank"])
    sorted_cats = sorted(by_category.keys())
    out = {
        "source": URL,
        "title": "The 2980 Most Frequently Used German Nouns (With Plural)",
        "total_entries": len(entries),
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
