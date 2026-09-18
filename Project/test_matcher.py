"""
test_matcher.py - Verify CSE Matching Engine with User Scenarios
"""
from matcher import calculate_match_score

def test_user_laptop_bag_scenario():
    print("\n--- Test 1: User Prompt Laptop Bag Scenario ---")
    lost = {
        "title": "Black HP laptop bag",
        "category": "laptop bag",
        "brand": "HP",
        "color": "black",
        "location": "Library",
        "date_lost_found": "2026-09-17",
        "time_lost_found": "14:00",
        "description": "Lost my black HP laptop bag near the library reading section.",
        "unique_marks": "Small red keychain on the zipper"
    }
    
    found = {
        "title": "Black laptop bag",
        "category": "laptop bag",
        "brand": "HP",
        "color": "black",
        "location": "Central Library",
        "date_lost_found": "2026-09-17",
        "time_lost_found": "14:30",
        "description": "Found a black HP laptop bag on a bench near Central Library.",
        "unique_marks": "Red tag or keychain attached"
    }
    
    result = calculate_match_score(lost, found)
    print(f"Total Score: {result['total_score']}/100")
    print(f"Status: {result['status_text']} ({result['confidence']})")
    print("Factor Breakdown:")
    for key, f in result["breakdown"].items():
        print(f"  {f['label']:<18} {f['score']:>2}/{f['max']} pts | {f['reason']}")
        
    assert result['total_score'] >= 85, f"Expected >= 85, got {result['total_score']}"
    assert result['confidence'] == "HIGH"
    print("[PASS] Test 1 Passed successfully!")

def test_silver_hp_laptop_scenario():
    print("\n--- Test 2: User Prompt Silver HP Laptop Scenario ---")
    lost = {
        "title": "Silver HP Laptop",
        "category": "laptop",
        "brand": "HP",
        "color": "silver",
        "location": "Library",
        "date_lost_found": "2026-09-17",
        "time_lost_found": "11:00",
        "description": "Silver HP laptop left at 2nd floor desk. Has stickers.",
        "unique_marks": "Sticker near keyboard"
    }
    
    found = {
        "title": "HP silver laptop",
        "category": "laptop",
        "brand": "HP",
        "color": "silver",
        "location": "Library",
        "date_lost_found": "2026-09-17",
        "time_lost_found": "11:45",
        "description": "Found an HP silver laptop in library. Small sticker visible.",
        "unique_marks": "Small sticker near keyboard"
    }
    
    result = calculate_match_score(lost, found)
    print(f"Total Score: {result['total_score']}/100")
    print(f"Status: {result['status_text']} ({result['confidence']})")
    for key, f in result["breakdown"].items():
        print(f"  {f['label']:<18} {f['score']:>2}/{f['max']} pts | {f['reason']}")
        
    assert result['total_score'] >= 90, f"Expected >= 90, got {result['total_score']}"
    print("[PASS] Test 2 Passed successfully!")

def test_mismatch_scenario():
    print("\n--- Test 3: Complete Mismatch (Water Bottle vs Laptop) ---")
    lost = {
        "title": "MacBook Air",
        "category": "laptop",
        "brand": "Apple",
        "color": "silver",
        "location": "Library",
        "date_lost_found": "2026-09-17",
        "time_lost_found": "14:00",
        "description": "Lost laptop",
        "unique_marks": ""
    }
    
    found = {
        "title": "Blue Hydro Flask bottle",
        "category": "water bottle",
        "brand": "Hydro Flask",
        "color": "blue",
        "location": "Sports Complex",
        "date_lost_found": "2026-09-02",
        "time_lost_found": "09:00",
        "description": "Found bottle at gym",
        "unique_marks": ""
    }
    
    result = calculate_match_score(lost, found)
    print(f"Total Score: {result['total_score']}/100")
    print(f"Status: {result['status_text']} ({result['confidence']})")
    assert result['total_score'] < 30, f"Expected < 30, got {result['total_score']}"
    print("[PASS] Test 3 Passed successfully!")

if __name__ == "__main__":
    test_user_laptop_bag_scenario()
    test_silver_hp_laptop_scenario()
    test_mismatch_scenario()
    print("\n[ALL TESTS PASSED] Matcher algorithm verified!")
