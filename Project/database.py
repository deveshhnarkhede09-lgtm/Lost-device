"""
database.py - SQLite Database Management & Data Seeding
Handles storage for lost and found items, matches, and claims.
Compatible with local environments and serverless platforms (Vercel/AWS Lambda).
"""

import sqlite3
import os
import shutil
import tempfile
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_DB_PATH = os.path.join(BASE_DIR, "findit.db")

def is_serverless_or_readonly():
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return True
    try:
        test_file = os.path.join(BASE_DIR, ".perm_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return False
    except (IOError, OSError, PermissionError):
        return True

def get_db_path():
    if is_serverless_or_readonly():
        tmp_dir = tempfile.gettempdir()
        tmp_db = os.path.join(tmp_dir, "findit.db")
        # If /tmp/findit.db does not exist yet, copy initial findit.db from repo
        if not os.path.exists(tmp_db) and os.path.exists(LOCAL_DB_PATH):
            try:
                shutil.copy2(LOCAL_DB_PATH, tmp_db)
            except Exception as e:
                print(f"Notice: Could not copy initial db to /tmp: {e}")
        return tmp_db
    return LOCAL_DB_PATH

DB_PATH = LOCAL_DB_PATH

def get_db():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Items table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,                  -- 'lost' or 'found'
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            brand TEXT DEFAULT '',
            color TEXT DEFAULT '',
            location TEXT NOT NULL,
            date_lost_found TEXT NOT NULL,
            time_lost_found TEXT DEFAULT '',
            description TEXT DEFAULT '',
            unique_marks TEXT DEFAULT '',
            image_path TEXT DEFAULT '',
            verification_question TEXT DEFAULT '',
            verification_answer TEXT DEFAULT '',
            contact_name TEXT NOT NULL,
            contact_email TEXT NOT NULL,
            contact_phone TEXT DEFAULT '',
            status TEXT DEFAULT 'active',        -- 'active', 'matched', 'claimed', 'resolved'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Claims table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lost_item_id INTEGER,
            found_item_id INTEGER,
            claimant_name TEXT NOT NULL,
            claimant_email TEXT NOT NULL,
            claimant_phone TEXT DEFAULT '',
            claimant_answer TEXT NOT NULL,
            match_score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',       -- 'pending', 'approved', 'rejected'
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lost_item_id) REFERENCES items (id),
            FOREIGN KEY (found_item_id) REFERENCES items (id)
        );
        """)
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Notice during init_db: {e}")

def seed_data():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM items")
        count = cursor.fetchone()[0]
        
        if count == 0:
            sample_items = [
            # Pair 1: Laptop Bag in AB1 Hall
            (
                "lost",
                "Black HP laptop bag",
                "laptop bag",
                "HP",
                "black",
                "AB1 Hall",
                "2026-09-17",
                "14:00",
                "Black HP laptop bag with red keychain lost near AB1 Hall quiet study area.",
                "Red keychain tag attached to main zipper",
                "/static/images/items/laptop_bag.svg",
                "",
                "",
                "Aarav Sharma",
                "aarav.sharma2023@vitbhopal.ac.in",
                "+91 98765 01111",
                "matched"
            ),
            (
                "found",
                "Black laptop bag",
                "laptop bag",
                "HP",
                "black",
                "AB1 Hall",
                "2026-09-17",
                "14:30",
                "Black laptop bag found on a bench outside AB1 Hall entrance.",
                "Red keychain attached to zipper",
                "/static/images/items/laptop_bag.svg",
                "What color or item is attached to the zipper?",
                "red keychain",
                "AB1 Floor Security",
                "security@vitbhopal.ac.in",
                "+91 98765 01112",
                "active"
            ),
            
            # Pair 2: Silver HP Laptop Scenario in AB2
            (
                "lost",
                "Silver HP Pavilion Laptop",
                "laptop",
                "HP",
                "silver",
                "AB2",
                "2026-09-17",
                "11:00",
                "Silver HP 15-inch laptop forgotten in AB2 2nd floor lab. Urgent, contains final project!",
                "Sticker near keyboard (GitHub Octocat)",
                "/static/images/items/silver_laptop.svg",
                "",
                "",
                "Rohan Patel",
                "rohan.patel2022@vitbhopal.ac.in",
                "+91 98765 02222",
                "matched"
            ),
            (
                "found",
                "HP Silver Laptop",
                "laptop",
                "HP",
                "silver",
                "AB2",
                "2026-09-17",
                "11:45",
                "HP silver laptop found on desk in AB2 Room 204.",
                "Small sticker near keyboard",
                "/static/images/items/silver_laptop.svg",
                "What character or logo is on the sticker near the keyboard?",
                "github octocat",
                "AB2 Lab Assistant",
                "labs@vitbhopal.ac.in",
                "+91 98765 02223",
                "active"
            ),
            
            # Pair 3: Apple AirPods Pro in Hospital
            (
                "lost",
                "Apple AirPods Pro (2nd Gen)",
                "earphones",
                "Apple",
                "white",
                "Hospital",
                "2026-09-18",
                "12:30",
                "White AirPods Pro in charging case left in Hospital health center waiting lounge.",
                "Astronaut silicone sleeve cover",
                "/static/images/items/airpods.svg",
                "",
                "",
                "Priya Nair",
                "priya.nair2024@vitbhopal.ac.in",
                "+91 98765 43210",
                "active"
            ),
            (
                "found",
                "White Wireless Earbuds Case",
                "earphones",
                "Apple",
                "white",
                "Hospital",
                "2026-09-18",
                "13:00",
                "White Apple AirPods charging case found under seat in Hospital reception.",
                "Blue silicone cover with astronaut graphic",
                "/static/images/items/airpods.svg",
                "What graphic or design is on the silicone case sleeve?",
                "astronaut",
                "Hospital Receptionist",
                "health@vitbhopal.ac.in",
                "+91 98765 01234",
                "active"
            ),
            
            # Pair 4: Casio Calculator in Open Audi
            (
                "lost",
                "Casio FX-991CW Calculator",
                "calculator",
                "Casio",
                "black",
                "Open Audi",
                "2026-09-16",
                "15:00",
                "Scientific calculator left behind in Open Audi stepped seats after club meeting.",
                "Initials 'RN' marked on battery cover",
                "/static/images/items/calculator.svg",
                "",
                "",
                "Riya Verma",
                "riya.verma2024@vitbhopal.ac.in",
                "+91 98765 12345",
                "active"
            ),
            (
                "found",
                "Casio Scientific Calculator",
                "calculator",
                "Casio",
                "black",
                "Open Audi",
                "2026-09-16",
                "15:45",
                "Black Casio calculator discovered on stepped seat in Open Audi.",
                "Handwritten initials on battery cover",
                "/static/images/items/calculator.svg",
                "What two letters are written on the battery lid on the back?",
                "RN",
                "Open Audi Coordinator",
                "events@vitbhopal.ac.in",
                "+91 98765 23456",
                "active"
            ),
            
            # Pair 5: Hydro Flask at Parking Gate / Parcel Point
            (
                "lost",
                "Hydro Flask 32oz Water Bottle",
                "water bottle",
                "Hydro Flask",
                "blue",
                "Parking Gate / Parcel Point",
                "2026-09-15",
                "17:30",
                "Cobalt blue metal water bottle forgotten near parcel pickup counter.",
                "Small dent on the bottom edge",
                "/static/images/items/water_bottle.svg",
                "",
                "",
                "Kunal Sen",
                "kunal.sen2023@vitbhopal.ac.in",
                "+91 98765 34567",
                "active"
            ),
            (
                "found",
                "Blue Metal Water Bottle",
                "water bottle",
                "Hydro Flask",
                "blue",
                "Parking Gate / Parcel Point",
                "2026-09-15",
                "18:15",
                "Blue insulated water bottle retrieved from Parking Gate parcel counter.",
                "Dent on bottom metal base",
                "/static/images/items/water_bottle.svg",
                "Where is the dent or physical damage on this bottle?",
                "bottom base",
                "Parcel Desk Supervisor",
                "parcels@vitbhopal.ac.in",
                "+91 98765 45678",
                "active"
            ),
            
            # Pair 6: Student ID Card (Lost & Found Pair)
            (
                "lost",
                "VIT Bhopal Student ID Card",
                "id card",
                "VIT Bhopal",
                "blue and white",
                "Multipurpose Hall (MPH)",
                "2026-09-18",
                "10:00",
                "Student ID card lost during morning orientation in Multipurpose Hall. Urgent, needed for hostel entry and exams!",
                "Blue lanyard with registration number 22BCE10045",
                "/static/images/items/id_card.svg",
                "",
                "",
                "Dev Singh",
                "dev.singh2022@vitbhopal.ac.in",
                "+91 98765 56789",
                "matched"
            ),
            (
                "found",
                "Found Student ID Card with Blue Lanyard",
                "id card",
                "VIT Bhopal",
                "blue and white",
                "Multipurpose Hall (MPH)",
                "2026-09-18",
                "10:45",
                "Found a student ID card on row 12 chair in Multipurpose Hall auditorium after orientation.",
                "Blue lanyard with registration number ending in 10045",
                "/static/images/items/id_card.svg",
                "What are the last 5 digits of the registration number or student name on the card?",
                "10045",
                "MPH Security Guard",
                "security@vitbhopal.ac.in",
                "+91 98765 67890",
                "active"
            )
            ]
            
            cursor.executemany("""
            INSERT INTO items (
                type, title, category, brand, color, location,
                date_lost_found, time_lost_found, description, unique_marks,
                image_path, verification_question, verification_answer,
                contact_name, contact_email, contact_phone, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_items)
            
            # Add sample approved/resolved claim to demonstrate dashboard resolution
            cursor.execute("""
            INSERT INTO claims (
                lost_item_id, found_item_id, claimant_name, claimant_email,
                claimant_phone, claimant_answer, match_score, status, notes
            ) VALUES (1, 2, 'Aarav Sharma', 'aarav.sharma@campus.edu', '+1 (555) 234-8901', 'red keychain', 98, 'approved', 'Identity verified, bag returned at library security desk.')
            """)
            
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Notice during seed_data: {e}")

if __name__ == "__main__":
    init_db()
    seed_data()
    print("Database initialized and seeded successfully.")
