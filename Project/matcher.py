"""
matcher.py - Core CSE Intelligent Matching Engine
Calculates multi-factor similarity between Lost and Found items.
Factors:
- Category (20 pts)
- Brand (15 pts)
- Color (15 pts)
- Campus Location (15 pts)
- Date & Time Proximity (15 pts)
- Description NLP Similarity (10 pts)
- Unique Marks / Identifying Features (10 pts)
Total Base Score: 100 points
Plus optional Image Similarity (Pillow perceptual dHash + RGB histogram)
"""

import math
import re
from datetime import datetime
from PIL import Image
import os

# ---------------------------------------------------------
# Taxonomy & Synonym Dictionaries
# ---------------------------------------------------------

CATEGORY_GROUPS = {
    "electronics": ["laptop", "phone", "tablet", "headphones", "earphones", "airpods", "smartwatch", "charger", "powerbank", "calculator"],
    "bags": ["backpack", "laptop bag", "handbag", "duffel bag", "tote bag", "wallet", "purse", "pouch"],
    "stationery": ["notebook", "book", "textbook", "binder", "pencil case", "pen"],
    "cards": ["id card", "id ccard", "idcard", "identity card", "student id", "smart card", "campus id", "id badge", "college id", "vit id", "card holder", "debit card", "atm card", "library card", "card"],
    "accessories": ["water bottle", "umbrella", "glasses", "sunglasses", "jacket", "hoodie", "cap", "watch", "ring", "keys"]
}

COLOR_SYNONYMS = {
    "black": ["black", "dark", "charcoal", "pitch black", "matte black"],
    "white": ["white", "ivory", "cream", "pearl"],
    "silver": ["silver", "grey", "gray", "metallic", "space grey", "space gray", "platinum", "ash"],
    "blue": ["blue", "navy", "royal blue", "sky blue", "cyan", "indigo", "teal", "cobalt"],
    "red": ["red", "maroon", "crimson", "burgundy", "ruby", "scarlet"],
    "green": ["green", "olive", "forest green", "mint", "emerald", "lime"],
    "yellow": ["yellow", "gold", "golden", "amber", "mustard"],
    "brown": ["brown", "tan", "beige", "khaki", "chocolate", "bronze"],
    "purple": ["purple", "violet", "lavender", "magenta", "plum"],
    "pink": ["pink", "rose", "coral", "salmon", "blush"],
    "orange": ["orange", "peach", "rust", "tangerine"]
}

BRAND_ALIASES = {
    "apple": ["apple", "macbook", "iphone", "ipad", "airpods"],
    "hp": ["hp", "hewlett packard", "hewlett-packard", "omen", "victus", "pavilion"],
    "dell": ["dell", "xps", "alienware", "inspiron", "latitude"],
    "lenovo": ["lenovo", "thinkpad", "ideapad", "legion", "yoga"],
    "asus": ["asus", "rog", "tuf", "zenbook"],
    "samsung": ["samsung", "galaxy"],
    "sony": ["sony", "playstation", "wh-1000", "bravia"],
    "wildcraft": ["wildcraft"],
    "nike": ["nike", "jordan"],
    "adidas": ["adidas", "originals"],
    "casio": ["casio", "g-shock", "fx-991"],
    "hydro flask": ["hydro flask", "hydroflask"],
    "milton": ["milton"],
    "boat": ["boat", "boAt", "rockerz", "airdopes"],
    "vit bhopal": ["vit bhopal", "vit", "vitb", "vellore institute", "campus"]
}

# Campus Locations & Spatial Proximity (VIT Bhopal Campus Locations)
CAMPUS_LOCATIONS = {
    # Academic & Auditoriums
    "ab1 hall": {"zone": "academic_core", "coords": (170, 140)},
    "ab1": {"zone": "academic_core", "coords": (170, 140)},
    "academic block 1": {"zone": "academic_core", "coords": (170, 140)},
    "ab2": {"zone": "academic_core", "coords": (290, 140)},
    "academic block 2": {"zone": "academic_core", "coords": (290, 140)},
    "mph": {"zone": "events", "coords": (230, 240)},
    "multipurpose hall": {"zone": "events", "coords": (230, 240)},
    "open audi": {"zone": "events", "coords": (340, 240)},
    "open auditorium": {"zone": "events", "coords": (340, 240)},
    "central library": {"zone": "academic_core", "coords": (230, 80)},
    "library": {"zone": "academic_core", "coords": (230, 80)},

    # Healthcare & Facilities
    "hospital": {"zone": "healthcare", "coords": (140, 370)},
    "health center": {"zone": "healthcare", "coords": (140, 370)},
    "parking gate / parcel point": {"zone": "facilities", "coords": (270, 430)},
    "parking gate": {"zone": "facilities", "coords": (270, 430)},
    "parcel point": {"zone": "facilities", "coords": (270, 430)},
    "main gate of entrence": {"zone": "gate", "coords": (420, 430)},
    "main gate entrance": {"zone": "gate", "coords": (420, 430)},
    "main gate": {"zone": "gate", "coords": (420, 430)},

    # Boys Hostels (BH 1-6, 7A, 7B, 8A, 8B)
    "boys hostel 1": {"zone": "boys_hostels", "coords": (470, 100)},
    "bh 1": {"zone": "boys_hostels", "coords": (470, 100)},
    "boys hostel 2": {"zone": "boys_hostels", "coords": (510, 100)},
    "bh 2": {"zone": "boys_hostels", "coords": (510, 100)},
    "boys hostel 3": {"zone": "boys_hostels", "coords": (550, 100)},
    "bh 3": {"zone": "boys_hostels", "coords": (550, 100)},
    "boys hostel 4": {"zone": "boys_hostels", "coords": (470, 160)},
    "bh 4": {"zone": "boys_hostels", "coords": (470, 160)},
    "boys hostel 5": {"zone": "boys_hostels", "coords": (510, 160)},
    "bh 5": {"zone": "boys_hostels", "coords": (510, 160)},
    "boys hostel 6": {"zone": "boys_hostels", "coords": (550, 160)},
    "bh 6": {"zone": "boys_hostels", "coords": (550, 160)},
    "boys hostel 7a": {"zone": "boys_hostels", "coords": (470, 230)},
    "bh 7a": {"zone": "boys_hostels", "coords": (470, 230)},
    "boys hostel 7b": {"zone": "boys_hostels", "coords": (520, 230)},
    "bh 7b": {"zone": "boys_hostels", "coords": (520, 230)},
    "boys hostel 8a": {"zone": "boys_hostels", "coords": (470, 300)},
    "bh 8a": {"zone": "boys_hostels", "coords": (470, 300)},
    "boys hostel 8b": {"zone": "boys_hostels", "coords": (520, 300)},
    "bh 8b": {"zone": "boys_hostels", "coords": (520, 300)},
    "boys hostel complex": {"zone": "boys_hostels", "coords": (500, 180)},
    "boys hostel": {"zone": "boys_hostels", "coords": (500, 180)},

    # Girls Hostels (GH 1, GH 2, Block A, Block B)
    "girls hostel 1": {"zone": "girls_hostels", "coords": (70, 150)},
    "gh 1": {"zone": "girls_hostels", "coords": (70, 150)},
    "girls hostel 2": {"zone": "girls_hostels", "coords": (70, 200)},
    "gh 2": {"zone": "girls_hostels", "coords": (70, 200)},
    "girls hostel block a": {"zone": "girls_hostels", "coords": (70, 260)},
    "gh a": {"zone": "girls_hostels", "coords": (70, 260)},
    "girls hostel block b": {"zone": "girls_hostels", "coords": (70, 310)},
    "gh b": {"zone": "girls_hostels", "coords": (70, 310)},
    "girls hostel complex": {"zone": "girls_hostels", "coords": (70, 220)},
    "girls hostel": {"zone": "girls_hostels", "coords": (70, 220)},

    # Dining, Sports & Grounds
    "underbelly food court": {"zone": "student_hub", "coords": (270, 300)},
    "underbelly": {"zone": "student_hub", "coords": (270, 300)},
    "sports arena & grounds": {"zone": "recreation", "coords": (70, 420)},
    "sports arena": {"zone": "recreation", "coords": (70, 420)},
    "sports complex": {"zone": "recreation", "coords": (70, 420)},
    "campus grounds": {"zone": "general", "coords": (270, 250)}
}

# ---------------------------------------------------------
# Utility NLP & Text Cleaning Functions
# ---------------------------------------------------------

STOPWORDS = {
    "a", "an", "the", "in", "on", "at", "near", "by", "with", "and", "or", "of", "to", "for",
    "is", "was", "it", "my", "i", "found", "lost", "some", "someone", "around", "about",
    "item", "this", "that", "there", "here", "please", "help", "color", "brand"
}

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return text.strip()

def tokenize(text: str) -> set:
    words = clean_text(text).split()
    return {w for w in words if w not in STOPWORDS and len(w) > 1}

def normalize_string(s: str) -> str:
    return clean_text(s)

# ---------------------------------------------------------
# Factor Matching Functions
# ---------------------------------------------------------

def match_category(cat1: str, cat2: str, title1: str = "", title2: str = "") -> tuple[float, str]:
    """Score Category up to 20 points"""
    c1, c2 = normalize_string(cat1), normalize_string(cat2)
    if not c1 or not c2:
        return 0.0, "Category missing"
    
    # Direct match or substring
    if c1 == c2:
        return 20.0, f"Exact match: {cat1}"
    if c1 in c2 or c2 in c1:
        return 18.0, f"High overlap: {cat1} ~ {cat2}"
    
    # Check title mentions
    t1, t2 = normalize_string(title1), normalize_string(title2)
    if c1 in t2 or c2 in t1:
        return 18.0, f"Cross-referenced in title: {cat1} / {cat2}"
        
    # Same category taxonomy group
    for group, items in CATEGORY_GROUPS.items():
        in_c1 = any(item in c1 for item in items)
        in_c2 = any(item in c2 for item in items)
        if in_c1 and in_c2:
            return 14.0, f"Same general category ({group.capitalize()})"
            
    return 0.0, f"Category mismatch: {cat1} vs {cat2}"

def match_brand(b1: str, b2: str, title1: str = "", title2: str = "", desc1: str = "", desc2: str = "") -> tuple[float, str]:
    """Score Brand up to 15 points"""
    norm1, norm2 = normalize_string(b1), normalize_string(b2)
    combined_text1 = f"{norm1} {normalize_string(title1)} {normalize_string(desc1)}"
    combined_text2 = f"{norm2} {normalize_string(title2)} {normalize_string(desc2)}"
    
    # If neither specified a brand
    if not norm1 and not norm2:
        return 10.0, "Unbranded / generic item"
        
    # Check direct brand match
    if norm1 and norm2:
        if norm1 == norm2:
            return 15.0, f"Brand match: {b1.upper()}"
        if norm1 in norm2 or norm2 in norm1:
            return 14.0, f"Brand close match: {b1} ~ {b2}"
            
    # Check brand alias dictionary
    for brand_key, aliases in BRAND_ALIASES.items():
        has_alias1 = any(alias in combined_text1 for alias in aliases)
        has_alias2 = any(alias in combined_text2 for alias in aliases)
        if has_alias1 and has_alias2:
            return 15.0, f"Brand alias match: {brand_key.upper()}"
            
    # If one specified a brand and it appears in other's title or description
    if norm1 and norm1 in combined_text2:
        return 13.0, f"Brand '{b1}' detected in found report"
    if norm2 and norm2 in combined_text1:
        return 13.0, f"Brand '{b2}' detected in lost report"
        
    if not norm1 or not norm2:
        return 6.0, "One report missing brand"
        
    return 0.0, f"Brand mismatch: {b1} vs {b2}"

def match_color(c1: str, c2: str, desc1: str = "", desc2: str = "") -> tuple[float, str]:
    """Score Color up to 15 points"""
    norm1, norm2 = normalize_string(c1), normalize_string(c2)
    full_text1 = f"{norm1} {normalize_string(desc1)}"
    full_text2 = f"{norm2} {normalize_string(desc2)}"
    
    if not norm1 and not norm2:
        return 8.0, "Colors not specified"
        
    if norm1 and norm2 and norm1 == norm2:
        return 15.0, f"Color exact match: {c1.capitalize()}"
        
    # Check color synonyms (e.g. silver and grey)
    for color_family, synonyms in COLOR_SYNONYMS.items():
        found1 = any(s in full_text1 for s in synonyms)
        found2 = any(s in full_text2 for s in synonyms)
        if found1 and found2:
            return 15.0, f"Color match: {color_family.capitalize()} family"
            
    # Check cross-mention
    if norm1 and norm1 in full_text2:
        return 12.0, f"Color '{c1}' mentioned in description"
    if norm2 and norm2 in full_text1:
        return 12.0, f"Color '{c2}' mentioned in description"
        
    if not norm1 or not norm2:
        return 6.0, "One report missing color"
        
    return 0.0, f"Color mismatch: {c1} vs {c2}"

def get_location_coords(loc_name: str) -> tuple[float, float, str]:
    cleaned = normalize_string(loc_name)
    for key, data in CAMPUS_LOCATIONS.items():
        if key in cleaned or cleaned in key:
            return data["coords"][0], data["coords"][1], data["zone"]
    # Fallback to campus center
    return 270.0, 300.0, "general"

def match_location(loc1: str, loc2: str) -> tuple[float, str]:
    """Score Campus Location up to 15 points"""
    n1, n2 = normalize_string(loc1), normalize_string(loc2)
    if not n1 or not n2:
        return 7.0, "Location partially specified"
        
    # Exact or near string match (e.g., "Library" and "Central Library")
    if n1 == n2:
        return 15.0, f"Same location: {loc1}"
    if n1 in n2 or n2 in n1:
        return 15.0, f"Location match: {loc1} ~ {loc2}"
        
    # Spatial coordinates distance
    x1, y1, z1 = get_location_coords(loc1)
    x2, y2, z2 = get_location_coords(loc2)
    
    if z1 != "general" and z1 == z2:
        return 12.0, f"Same campus zone ({z1.replace('_', ' ').title()})"
        
    dist = math.hypot(x1 - x2, y1 - y2)
    if dist < 80:
        return 12.0, "Adjacent campus buildings"
    elif dist < 160:
        return 8.0, "Nearby campus area"
    elif dist < 260:
        return 5.0, "Within 5-minute walk"
    else:
        return 2.0, f"Different campus zones ({loc1} vs {loc2})"

def match_date_time(date1: str, time1: str, date2: str, time2: str) -> tuple[float, str]:
    """Score Date & Time Proximity up to 15 points"""
    try:
        d1 = datetime.strptime(date1.strip(), "%Y-%m-%d").date()
        d2 = datetime.strptime(date2.strip(), "%Y-%m-%d").date()
        diff_days = abs((d1 - d2).days)
        
        diff_hours = 0.0
        if time1 and time2:
            t1_parts = str(time1).split(":")
            t2_parts = str(time2).split(":")
            if len(t1_parts) >= 2 and len(t2_parts) >= 2:
                h1 = int(t1_parts[0]) + int(t1_parts[1]) / 60.0
                h2 = int(t2_parts[0]) + int(t2_parts[1]) / 60.0
                diff_hours = abs(h1 - h2)
                
        if diff_days == 0:
            if diff_hours <= 1.0:
                return 15.0, "Same day & within 1 hour"
            elif diff_hours <= 3.0:
                return 14.0, "Same day & within 3 hours"
            else:
                return 13.0, "Reported on the same day"
        elif diff_days == 1:
            return 11.0, "Within 24-48 hours"
        elif diff_days <= 3:
            return 8.0, f"Within {diff_days} days"
        elif diff_days <= 7:
            return 5.0, "Within 1 week"
        else:
            return 2.0, f"Over {diff_days} days apart"
    except Exception:
        if date1 and date2 and str(date1).strip() == str(date2).strip():
            return 14.0, "Matching date string"
        return 7.0, "Approximate date comparison"

def match_description(desc1: str, desc2: str, title1: str = "", title2: str = "") -> tuple[float, str]:
    """Score Description & Title NLP token overlap up to 10 points"""
    text1 = f"{title1} {desc1}"
    text2 = f"{title2} {desc2}"
    
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)
    
    if not tokens1 or not tokens2:
        return 5.0, "Limited description provided"
        
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    
    if not union:
        return 5.0, "No common terms"
        
    jaccard = len(intersection) / len(union)
    overlap_count = len(intersection)
    
    score = min(10.0, round(jaccard * 16.0 + (overlap_count * 1.5), 1))
    score = max(2.0 if overlap_count > 0 else 0.0, score)
    
    matching_terms = ", ".join(list(intersection)[:4]) if intersection else "none"
    if score >= 7.0:
        return score, f"Strong semantic similarity (keywords: {matching_terms})"
    elif score >= 4.0:
        return score, f"Moderate keyword overlap ({matching_terms})"
    else:
        return score, "Low semantic overlap"

def match_unique_marks(mark1: str, mark2: str, desc1: str = "", desc2: str = "") -> tuple[float, str]:
    """Score Unique Identifier / Mark up to 10 points"""
    norm1, norm2 = normalize_string(mark1), normalize_string(mark2)
    full1 = f"{norm1} {normalize_string(desc1)}"
    full2 = f"{norm2} {normalize_string(desc2)}"
    
    # If both explicitly provided unique marks
    if norm1 and norm2:
        t1, t2 = tokenize(norm1), tokenize(norm2)
        common = t1.intersection(t2)
        if norm1 == norm2:
            return 10.0, f"Exact unique mark match: '{mark1}'"
        if len(common) > 0:
            return 8.0, f"Identifying mark overlap: {', '.join(common)}"
        if norm1 in full2 or norm2 in full1:
            return 7.0, "Identifying mark mentioned in report"
            
    # Check if mark from one is mentioned in the other's description
    if norm1 and norm1 in full2:
        return 7.0, f"Unique mark '{mark1}' matched in details"
    if norm2 and norm2 in full1:
        return 7.0, f"Found mark '{mark2}' matched in lost description"
        
    signatures = ["sticker", "scratch", "keychain", "case", "cover", "crack", "wallpaper", "initials", "name", "tag"]
    has_sig1 = any(s in full1 for s in signatures)
    has_sig2 = any(s in full2 for s in signatures)
    if has_sig1 and has_sig2:
        return 5.0, "Both reports note physical distinguishing marks"
        
    if not norm1 and not norm2:
        return 5.0, "No unique markings specified"
        
    return 3.0, "Mark details unconfirmed"

# ---------------------------------------------------------
# Image Perceptual Similarity (dHash & Color Palette)
# ---------------------------------------------------------

def compute_dhash(image_path: str, hash_size: int = 8) -> str:
    """Computes difference hash (dHash) of an image using Pillow."""
    try:
        if not image_path or not os.path.exists(image_path):
            return ""
        with Image.open(image_path) as img:
            img = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.BILINEAR)
            pixels = list(img.getdata())
            diff = []
            for row in range(hash_size):
                for col in range(hash_size):
                    left = pixels[row * (hash_size + 1) + col]
                    right = pixels[row * (hash_size + 1) + col + 1]
                    diff.append("1" if left > right else "0")
            return "".join(diff)
    except Exception:
        return ""

def hamming_distance(s1: str, s2: str) -> int:
    if len(s1) != len(s2) or not s1:
        return 64
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

def compute_color_histogram_similarity(image_path1: str, image_path2: str) -> float:
    """Compares basic RGB color histograms."""
    try:
        if not os.path.exists(image_path1) or not os.path.exists(image_path2):
            return 0.5
        with Image.open(image_path1) as img1, Image.open(image_path2) as img2:
            img1 = img1.convert("RGB").resize((64, 64))
            img2 = img2.convert("RGB").resize((64, 64))
            h1 = img1.histogram()
            h2 = img2.histogram()
            
            sum1 = sum(h1) or 1
            sum2 = sum(h2) or 1
            norm_h1 = [v / sum1 for v in h1]
            norm_h2 = [v / sum2 for v in h2]
            
            intersection = sum(min(v1, v2) for v1, v2 in zip(norm_h1, norm_h2))
            return intersection
    except Exception:
        return 0.5

def calculate_image_similarity(img_path1: str, img_path2: str) -> tuple[float, str]:
    """Returns visual similarity percentage (0-100%) and reason."""
    if not img_path1 or not img_path2:
        return 0.0, "No photos compared"
        
    hash1 = compute_dhash(img_path1)
    hash2 = compute_dhash(img_path2)
    
    if hash1 and hash2:
        h_dist = hamming_distance(hash1, hash2)
        hash_score = max(0.0, (1.0 - (h_dist / 32.0))) * 100.0
        hist_sim = compute_color_histogram_similarity(img_path1, img_path2) * 100.0
        combined_visual = round(0.6 * hash_score + 0.4 * hist_sim, 1)
        return combined_visual, f"Visual dHash distance: {h_dist}/64, Color match: {hist_sim:.0f}%"
        
    return 0.0, "Image processing unavailable"

# ---------------------------------------------------------
# Master Match Calculator
# ---------------------------------------------------------

def calculate_match_score(lost_item: dict, found_item: dict) -> dict:
    """
    Computes multi-factor match score between a Lost item and a Found item.
    """
    # Factor 1: Category (20)
    cat_score, cat_reason = match_category(
        lost_item.get("category", ""),
        found_item.get("category", ""),
        lost_item.get("title", ""),
        found_item.get("title", "")
    )
    
    # Factor 2: Brand (15)
    brand_score, brand_reason = match_brand(
        lost_item.get("brand", ""),
        found_item.get("brand", ""),
        lost_item.get("title", ""),
        found_item.get("title", ""),
        lost_item.get("description", ""),
        found_item.get("description", "")
    )
    
    # Factor 3: Color (15)
    color_score, color_reason = match_color(
        lost_item.get("color", ""),
        found_item.get("color", ""),
        lost_item.get("description", ""),
        found_item.get("description", "")
    )
    
    # Factor 4: Location (15)
    loc_score, loc_reason = match_location(
        lost_item.get("location", ""),
        found_item.get("location", "")
    )
    
    # Factor 5: Date & Time (15)
    date_score, date_reason = match_date_time(
        lost_item.get("date_lost_found", ""),
        lost_item.get("time_lost_found", ""),
        found_item.get("date_lost_found", ""),
        found_item.get("time_lost_found", "")
    )
    
    # Factor 6: Description NLP (10)
    desc_score, desc_reason = match_description(
        lost_item.get("description", ""),
        found_item.get("description", ""),
        lost_item.get("title", ""),
        found_item.get("title", "")
    )
    
    # Factor 7: Unique Marks (10)
    mark_score, mark_reason = match_unique_marks(
        lost_item.get("unique_marks", ""),
        found_item.get("unique_marks", ""),
        lost_item.get("description", ""),
        found_item.get("description", "")
    )
    
    raw_total = cat_score + brand_score + color_score + loc_score + date_score + desc_score + mark_score
    total_score = min(100, max(0, int(round(raw_total))))
    
    # Category gating rule: if category is a complete mismatch (e.g. laptop vs water bottle),
    # penalize total score so unrelated items don't score high on coincidental color or location
    if cat_score == 0:
        total_score = min(total_score, 25)
        
    # Image similarity check if both items have photos
    img1 = lost_item.get("image_path", "")
    img2 = found_item.get("image_path", "")
    img_has_both = bool(img1 and img2 and os.path.exists(img1) and os.path.exists(img2))
    
    img_score = 0.0
    img_reason = "No image comparison"
    if img_has_both:
        img_score, img_reason = calculate_image_similarity(img1, img2)
        if img_score >= 80:
            total_score = min(100, total_score + 4)
            
    # Confidence Level
    if total_score >= 80:
        confidence = "HIGH"
        status_text = "POSSIBLE MATCH"
    elif total_score >= 55:
        confidence = "MEDIUM"
        status_text = "POTENTIAL CANDIDATE"
    else:
        confidence = "LOW"
        status_text = "UNLIKELY MATCH"
        
    return {
        "total_score": total_score,
        "confidence": confidence,
        "status_text": status_text,
        "breakdown": {
            "category": {"score": int(round(cat_score)), "max": 20, "label": "Category", "reason": cat_reason},
            "color": {"score": int(round(color_score)), "max": 15, "label": "Color", "reason": color_reason},
            "brand": {"score": int(round(brand_score)), "max": 15, "label": "Brand", "reason": brand_reason},
            "location": {"score": int(round(loc_score)), "max": 15, "label": "Location", "reason": loc_reason},
            "date": {"score": int(round(date_score)), "max": 15, "label": "Date & Time", "reason": date_reason},
            "description": {"score": int(round(desc_score)), "max": 10, "label": "Description NLP", "reason": desc_reason},
            "unique_mark": {"score": int(round(mark_score)), "max": 10, "label": "Unique Mark", "reason": mark_reason}
        },
        "image_similarity": {
            "available": img_has_both,
            "score": round(img_score, 1),
            "reason": img_reason
        }
    }
