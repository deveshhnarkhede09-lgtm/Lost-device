# 📡 FindIt — Campus Lost & Found Intelligent Matching System
### *CSE Capstone Project • Multi-Factor Heuristic Matching Engine for VIT Bhopal University*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.0-lightgrey.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57.svg?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Campus](https://img.shields.io/badge/Campus-VIT%20Bhopal-orange.svg)](https://vitbhopal.ac.in)
[![Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()

> A full-stack university portal where students report lost or found items, and an intelligent multi-factor matching algorithm detects matches automatically, displays transparent points breakdowns, protects student privacy through ownership challenge questions, and visualizes reports across an interactive 2D spatial map of VIT Bhopal University.

---

## 🎯 The Core Problem & CSE Motivation

Traditional campus lost-and-found portals are nothing more than basic CRUD message boards (*Add Item &rarr; Search &rarr; Contact*). Students must manually scroll through hundreds of posts or rely on cluttered WhatsApp/Telegram groups.

**FindIt makes the matching algorithm the primary CSE innovation:**
When a student reports:
> **Lost:** *Black HP laptop bag near AB1 Hall on Sept 17 around 2:00 PM*

And another student reports:
> **Found:** *Black laptop bag outside AB1 Hall on Sept 17 around 2:30 PM*

The algorithm computes a composite similarity score (**98% HIGH Match**) and flags both reports immediately.

---

## 🧠 Multi-Factor Matching Algorithm Breakdown

The scoring engine (`matcher.py`) evaluates candidate pairs across **7 weighted heuristic dimensions** totaling **100 base points**:

| Dimension | Max Points | Evaluation Methodology & Heuristics |
| :--- | :---: | :--- |
| **Category** | **20 pts** | Exact string matching, substring checks, and cross-taxonomy clustering (`electronics`, `bags`, `cards`, `stationery`, `accessories`). |
| **Brand** | **15 pts** | Normalized matching with brand alias resolution (e.g. *HP &harr; Hewlett Packard*, *Apple &harr; MacBook*, *Casio &harr; fx-991*). |
| **Color** | **15 pts** | Semantic synonym mapping (e.g., *Silver &harr; Gray/Metallic/Space Grey*, *Navy &harr; Blue*). |
| **Location & Spatial Proximity** | **15 pts** | Euclidean coordinate distance and zone classification across VIT Bhopal facilities. |
| **Date & Time Proximity** | **15 pts** | Day difference decay penalty & time delta proximity scoring. |
| **Description NLP** | **10 pts** | Text normalization, stopword filtering, tokenization, and semantic keyword overlap. |
| **Unique Marks / Distinguishing Features** | **10 pts** | Keyword and token overlap for physical markers (stickers, keychains, scratches, initials). |
| **Total Base Score** | **100 pts** | **High (&ge;75%)** &bull; **Medium (50–74%)** &bull; **Low (&lt;50%)** |

---

## 🌟 Key Features

### 1. 🤖 Instant Matching & Real-Time Alert Ticker
- Automated scan triggers whenever a new report is created.
- Instant match popup appears if a high-confidence match is discovered right after form submission.

### 2. 🔐 Privacy & Ownership Verification Challenge
- Protects student privacy and prevents fraudulent claims.
- Finders do **not** reveal contact info publicly. Instead, the finder sets a secret security question (e.g., *"What sticker was on the laptop?"* or *"What are the last 5 digits of the registration number on the ID card?"*).
- Contact details remain securely locked until the claimant submits the matching answer.

### 3. 🗺️ Interactive VIT Bhopal Spatial Map
Visual 2D SVG university map depicting exact campus facilities:
- **Academic & Auditoriums**: `AB1 Hall`, `AB2`, `MPH (Multipurpose Hall)`, `Open Audi`
- **Healthcare & Gates**: `Hospital (Health Centre)`, `Parking Gate / Parcel Point`, `Main Gate of Entrance`
- **Boys Hostels**: `Boys Hostel 1, 2, 3, 4, 5, 6, 7A, 7B, 8A, 8B`
- **Girls Hostels**: `Girls Hostel 1, 2, Block A, Block B`
- Interactive building click inspection and pulsing coordinate pins for 🟥 *Lost* and 🟢 *Found* items.

### 4. 🔬 CSE Algorithm Lab (Interactive Sandbox)
- Built-in playground for recruiters, professors, and students to experiment with the algorithm.
- Plug in custom attributes or choose from 6 instant presets:
  1. *Laptop Bag Scenario (98%)*
  2. *HP Laptop Scenario (96%)*
  3. *AirPods Pro in Hospital (92%)*
  4. *Casio FX-991 Calculator in Open Audi (90%)*
  5. *Student ID Card in MPH (98%)*
  6. *Complete Mismatch (9%)*

### 5. 📊 Repository Analytics & Claims Dashboard
- Real-time counters for active lost reports, items in custody, automated matches, and resolved claims.
- Status management to approve or resolve student ownership claims.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, Flask 3.0, Werkzeug
- **Database**: SQLite3 (lightweight, zero-config relational database)
- **Frontend**: HTML5, Vanilla CSS3 (Custom Dark Theme, Glassmorphism, Responsive Grid), Vanilla JavaScript (ES6+ SPA)
- **Icons & Typography**: FontAwesome 6, Google Fonts (*Outfit*, *Plus Jakarta Sans*, *JetBrains Mono*)
- **Image Processing**: Pillow (Perceptual dHash + RGB Histogram)

---

## 📂 Project Structure

```
Project/
├── app.py                  # Flask application & REST API controllers
├── database.py             # SQLite schema initialization & VIT Bhopal seed data
├── matcher.py              # Core CSE multi-factor similarity matching engine
├── test_matcher.py         # Automated unit test suite verifying matching accuracy
├── generate_assets.py      # Vector SVG asset generator for item icons
├── requirements.txt        # Python dependency manifest
├── .gitignore              # Git ignore rules for virtualenvs and temporary files
├── templates/
│   └── index.html          # Modern single-page web app with interactive tabs & modals
└── static/
    ├── css/
    │   └── style.css       # Design system, glassmorphism, responsive styles
    ├── js/
    │   └── app.js          # Client controller, API consumer, map pin renderer
    ├── images/
    │   └── items/          # SVG item icons (laptops, bags, airpods, cards, etc.)
    └── uploads/            # User-uploaded item photos directory
```

---

## ⚡ Getting Started (Local Setup)

### Prerequisites
- Python 3.8 or higher installed
- `pip` (Python package installer)
- `git`

### 1. Clone Repository
```bash
git clone https://github.com/your-username/lost-and-found-matcher.git
cd lost-and-found-matcher
```

### 2. Create and Activate Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Unit Tests
Verify the algorithm heuristics pass all validation suites:
```bash
python test_matcher.py
```

### 5. Start the Web Server
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `GET /api/items` | `GET` | Fetch all active reports (supports `type`, `category`, `location`, `search` query params) |
| `GET /api/items/<id>` | `GET` | Retrieve single item details |
| `POST /api/items` | `POST` | Create a new lost or found report (supports multipart file upload) |
| `GET /api/matches/<id>` | `GET` | Run multi-factor algorithm to find ranked candidate matches for an item |
| `POST /api/test-match` | `POST` | Sandbox endpoint to evaluate two arbitrary item payloads |
| `GET /api/claims` | `GET` | Retrieve ownership claims history |
| `POST /api/claims` | `POST` | Submit ownership verification answer for a found item |
| `POST /api/claims/<id>/resolve` | `POST` | Approve or reject a claim and mark items as resolved |
| `GET /api/stats` | `GET` | Get aggregate analytics (counts of lost, found, resolved, top locations) |

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
