"""
app.py - Flask Web Application for Campus Lost & Found Intelligent Matching System
Compatible with local execution and Serverless deployments (Vercel, AWS Lambda, Render).
"""

import os
import re
import shutil
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

import database
from matcher import calculate_match_score, compute_dhash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    template_folder=os.path.join(BASE_DIR, "templates")
)
app.config["SECRET_KEY"] = "findit-campus-intelligent-matching-secret-2026"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max

# Determine UPLOAD_FOLDER safely (writable tempdir on serverless / read-only environments)
if database.is_serverless_or_readonly():
    app.config["UPLOAD_FOLDER"] = os.path.join(tempfile.gettempdir(), "findit_uploads")
else:
    app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "static", "uploads")

try:
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
except Exception as e:
    print(f"Notice: Upload folder creation: {e}")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "svg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Ensure DB is created and seeded safely
try:
    database.init_db()
    database.seed_data()
except Exception as e:
    print(f"Notice during DB initialization: {e}")

@app.route("/static/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve uploaded images safely from either UPLOAD_FOLDER or local static/uploads."""
    if os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], filename)):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    bundled = os.path.join(BASE_DIR, "static", "uploads")
    if os.path.exists(os.path.join(bundled, filename)):
        return send_from_directory(bundled, filename)
    return "File not found", 404

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint for cloud monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "FindIt Campus Matching Engine",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/")
def index():
    return render_template("index.html")

# ---------------------------------------------------------
# Items API
# ---------------------------------------------------------

@app.route("/api/items", methods=["GET"])
def get_items():
    item_type = request.args.get("type", "")
    category = request.args.get("category", "")
    location = request.args.get("location", "")
    search = request.args.get("search", "").strip().lower()
    
    query = "SELECT * FROM items WHERE 1=1"
    params = []
    
    if item_type in ["lost", "found"]:
        query += " AND type = ?"
        params.append(item_type)
        
    if category:
        query += " AND category LIKE ?"
        params.append(f"%{category}%")
        
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
        
    query += " ORDER BY created_at DESC"
    
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    items = []
    for r in rows:
        d = dict(r)
        if search:
            combined = f"{d['title']} {d['category']} {d['brand']} {d['color']} {d['location']} {d['description']}".lower()
            if search not in combined:
                continue
        items.append(d)
        
    conn.close()
    return jsonify({"success": True, "count": len(items), "items": items})

@app.route("/api/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"success": False, "error": "Item not found"}), 404
        
    return jsonify({"success": True, "item": dict(row)})

@app.route("/api/items", methods=["POST"])
def create_item():
    data = request.form if request.form else request.get_json(silent=True) or {}
    
    item_type = data.get("type", "").lower()
    if item_type not in ["lost", "found"]:
        return jsonify({"success": False, "error": "Type must be 'lost' or 'found'"}), 400
        
    title = data.get("title", "").strip()
    category = data.get("category", "").strip()
    brand = data.get("brand", "").strip()
    color = data.get("color", "").strip()
    location = data.get("location", "").strip()
    date_lost_found = data.get("date_lost_found", "").strip()
    time_lost_found = data.get("time_lost_found", "").strip()
    description = data.get("description", "").strip()
    unique_marks = data.get("unique_marks", "").strip()
    
    verification_question = data.get("verification_question", "").strip()
    verification_answer = data.get("verification_answer", "").strip()
    
    contact_name = data.get("contact_name", "").strip()
    contact_email = data.get("contact_email", "").strip()
    contact_phone = data.get("contact_phone", "").strip()
    
    if not title or not category or not location or not date_lost_found or not contact_name or not contact_email:
        return jsonify({"success": False, "error": "Please fill in all required fields (title, category, location, date, contact info)."}), 400

    # Image upload handling
    image_url = ""
    if "photo" in request.files:
        file = request.files["photo"]
        if file and file.filename and allowed_file(file.filename):
            sec_name = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_name = f"{timestamp}_{sec_name}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], saved_name)
            file.save(save_path)
            image_url = f"/static/uploads/{saved_name}"
            
    # Default fallback SVG if no photo uploaded
    if not image_url:
        cat_lower = category.lower()
        if "laptop bag" in cat_lower or "bag" in cat_lower or "backpack" in cat_lower:
            image_url = "/static/images/items/laptop_bag.svg"
        elif "laptop" in cat_lower or "computer" in cat_lower:
            image_url = "/static/images/items/silver_laptop.svg"
        elif "airpods" in cat_lower or "earphone" in cat_lower or "headphone" in cat_lower:
            image_url = "/static/images/items/airpods.svg"
        elif "calculator" in cat_lower:
            image_url = "/static/images/items/calculator.svg"
        elif "bottle" in cat_lower:
            image_url = "/static/images/items/water_bottle.svg"
        else:
            image_url = "/static/images/items/id_card.svg"

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO items (
        type, title, category, brand, color, location,
        date_lost_found, time_lost_found, description, unique_marks,
        image_path, verification_question, verification_answer,
        contact_name, contact_email, contact_phone, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
    """, (
        item_type, title, category, brand, color, location,
        date_lost_found, time_lost_found, description, unique_marks,
        image_url, verification_question, verification_answer,
        contact_name, contact_email, contact_phone
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Automatically check for immediate matches against the new report
    matches_summary = find_matches_for_item_id(new_id)
    top_match = matches_summary[0] if matches_summary else None

    return jsonify({
        "success": True,
        "item_id": new_id,
        "message": f"Successfully reported {item_type} item!",
        "has_top_match": top_match is not None and top_match["score"] >= 75,
        "top_match": top_match
    })

# ---------------------------------------------------------
# Intelligent Matching Engine API
# ---------------------------------------------------------

def find_matches_for_item_id(item_id: int):
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    target_row = cursor.fetchone()
    if not target_row:
        conn.close()
        return []
        
    target_item = dict(target_row)
    opp_type = "found" if target_item["type"] == "lost" else "lost"
    
    cursor.execute("SELECT * FROM items WHERE type = ?", (opp_type,))
    candidate_rows = cursor.fetchall()
    conn.close()
    
    matches = []
    for cand_row in candidate_rows:
        cand_item = dict(cand_row)
        
        # Prepare item dicts with actual file paths for image similarity if available
        lost_dict = target_item if target_item["type"] == "lost" else cand_item
        found_dict = cand_item if target_item["type"] == "lost" else target_item
        
        analysis = calculate_match_score(lost_dict, found_dict)
        score = analysis["total_score"]
        
        if score >= 30:  # Threshold for considering as possible candidate
            matches.append({
                "target_item_id": item_id,
                "matched_item": cand_item,
                "score": score,
                "confidence": analysis["confidence"],
                "status_text": analysis["status_text"],
                "breakdown": analysis["breakdown"],
                "image_similarity": analysis["image_similarity"]
            })
            
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches

@app.route("/api/matches/<int:item_id>", methods=["GET"])
def get_matches(item_id):
    matches = find_matches_for_item_id(item_id)
    return jsonify({
        "success": True,
        "item_id": item_id,
        "matches_count": len(matches),
        "matches": matches
    })

# ---------------------------------------------------------
# Privacy & Ownership Claim Challenge API
# ---------------------------------------------------------

@app.route("/api/claims", methods=["GET"])
def get_claims():
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT c.*, 
           l.title AS lost_title, l.category AS lost_category, l.contact_name AS lost_owner_name,
           f.title AS found_title, f.location AS found_location, f.verification_question,
           f.contact_name AS finder_name, f.contact_email AS finder_email, f.contact_phone AS finder_phone
    FROM claims c
    LEFT JOIN items l ON c.lost_item_id = l.id
    LEFT JOIN items f ON c.found_item_id = f.id
    ORDER BY c.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return jsonify({"success": True, "claims": [dict(r) for r in rows]})

@app.route("/api/claims", methods=["POST"])
def submit_claim():
    data = request.get_json() or {}
    lost_item_id = data.get("lost_item_id")
    found_item_id = data.get("found_item_id")
    claimant_name = data.get("claimant_name", "").strip()
    claimant_email = data.get("claimant_email", "").strip()
    claimant_phone = data.get("claimant_phone", "").strip()
    claimant_answer = data.get("claimant_answer", "").strip()
    match_score = data.get("match_score", 0)
    
    if not found_item_id or not claimant_name or not claimant_email or not claimant_answer:
        return jsonify({"success": False, "error": "Please provide your name, email, and answer the verification question."}), 400
        
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (found_item_id,))
    found_item = cursor.fetchone()
    
    if not found_item:
        conn.close()
        return jsonify({"success": False, "error": "Found item not found"}), 404
        
    found_dict = dict(found_item)
    expected_ans = (found_dict.get("verification_answer") or "").lower().strip()
    provided_ans = claimant_answer.lower().strip()
    
    # Automated verification check
    is_auto_verified = False
    if expected_ans:
        exp_tokens = set(re.sub(r"[^\w\s]", "", expected_ans).split())
        prov_tokens = set(re.sub(r"[^\w\s]", "", provided_ans).split())
        overlap = exp_tokens.intersection(prov_tokens)
        if expected_ans in provided_ans or provided_ans in expected_ans or len(overlap) >= max(1, len(exp_tokens) // 2):
            is_auto_verified = True
    else:
        # If finder didn't set a secret answer, requires manual verification
        is_auto_verified = False
        
    claim_status = "approved" if is_auto_verified else "pending"
    notes = "Automated verification passed: secret question answer matched." if is_auto_verified else "Pending review by finder / campus desk."

    cursor.execute("""
    INSERT INTO claims (
        lost_item_id, found_item_id, claimant_name, claimant_email,
        claimant_phone, claimant_answer, match_score, status, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lost_item_id, found_item_id, claimant_name, claimant_email,
        claimant_phone, claimant_answer, match_score, claim_status, notes
    ))
    claim_id = cursor.lastrowid
    
    if is_auto_verified:
        # Update items status
        cursor.execute("UPDATE items SET status = 'claimed' WHERE id = ?", (found_item_id,))
        if lost_item_id:
            cursor.execute("UPDATE items SET status = 'claimed' WHERE id = ?", (lost_item_id,))
            
    conn.commit()
    conn.close()
    
    response_data = {
        "success": True,
        "claim_id": claim_id,
        "is_verified": is_auto_verified,
        "status": claim_status,
        "message": "Verification answer verified! Contact unlocked." if is_auto_verified else "Claim submitted! Waiting for finder to verify your answer."
    }
    
    if is_auto_verified:
        response_data["contact_info"] = {
            "name": found_dict["contact_name"],
            "email": found_dict["contact_email"],
            "phone": found_dict["contact_phone"],
            "location": found_dict["location"]
        }
        
    return jsonify(response_data)

@app.route("/api/claims/<int:claim_id>/resolve", methods=["POST"])
def resolve_claim(claim_id):
    data = request.get_json() or {}
    decision = data.get("decision", "approved") # 'approved' or 'rejected'
    
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM claims WHERE id = ?", (claim_id,))
    claim = cursor.fetchone()
    if not claim:
        conn.close()
        return jsonify({"success": False, "error": "Claim not found"}), 404
        
    claim_dict = dict(claim)
    new_status = "approved" if decision == "approved" else "rejected"
    cursor.execute("UPDATE claims SET status = ? WHERE id = ?", (new_status, claim_id))
    
    if decision == "approved":
        cursor.execute("UPDATE items SET status = 'resolved' WHERE id = ?", (claim_dict["found_item_id"],))
        if claim_dict.get("lost_item_id"):
            cursor.execute("UPDATE items SET status = 'resolved' WHERE id = ?", (claim_dict["lost_item_id"],))
            
    conn.commit()
    conn.close()
    return jsonify({"success": True, "status": new_status})

# ---------------------------------------------------------
# Dashboard & Stats API
# ---------------------------------------------------------

@app.route("/api/stats", methods=["GET"])
def get_stats():
    conn = database.get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM items WHERE type = 'lost'")
    lost_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM items WHERE type = 'found'")
    found_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM claims WHERE status = 'approved'")
    resolved_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT category, COUNT(*) as c FROM items GROUP BY category ORDER BY c DESC LIMIT 4")
    top_categories = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT location, COUNT(*) as c FROM items GROUP BY location ORDER BY c DESC LIMIT 4")
    top_locations = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        "success": True,
        "stats": {
            "lost_count": lost_count,
            "found_count": found_count,
            "resolved_count": resolved_count,
            "top_categories": top_categories,
            "top_locations": top_locations
        }
    })

# ---------------------------------------------------------
# Live CSE Algorithm Sandbox Tester API
# ---------------------------------------------------------

@app.route("/api/test-match", methods=["POST"])
def test_match_sandbox():
    data = request.get_json() or {}
    lost = data.get("lost_item", {})
    found = data.get("found_item", {})
    
    result = calculate_match_score(lost, found)
    return jsonify({
        "success": True,
        "result": result
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
