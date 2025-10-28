#!/usr/bin/env python3
"""
Final autotester with unique data for each test run
"""

import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://openapi.nocodebackend.com"
INSTANCE_ID = "41300_teste"
API_KEY = os.getenv("API_KEY")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Generate unique identifiers for each test run
timestamp = int(time.time())
unique_id = f"test_{timestamp}"

# ========================
# TEST FUNCTIONS
# ========================

def test_create_user():
    print("👤 Creating user...")
    payload = {
        "email": f"{unique_id}@example.com",
        "password_hash": "123456",
        "api_key": f"test_api_key_{unique_id}",
        "plan_level": "free",
        "is_supporter": 0,
        "name": f"Tester Bot {unique_id}"
    }
    
    endpoint = f"{BASE_URL}/create/users?Instance={INSTANCE_ID}"
    r = requests.post(endpoint, headers=HEADERS, json=payload)
    print(f"→ Status: {r.status_code}")
    print(f"→ Response: {r.text}")
    
    if r.status_code in [200, 201]:
        response_data = r.json()
        user_id = response_data.get("id")
        print(f"✅ User created with ID: {user_id}")
        return user_id
    else:
        print(f"❌ Failed to create user")
        return None

def test_create_thread(user_id):
    print("🧵 Creating thread...")
    payload = {
        "usuario_proprietario_id": user_id,
        "external_page_id": f"test-page-{unique_id}",
        "url": f"https://example.com/test-page-{unique_id}",
        "title": f"Test Thread {unique_id}"
    }
    
    endpoint = f"{BASE_URL}/create/threads?Instance={INSTANCE_ID}"
    r = requests.post(endpoint, headers=HEADERS, json=payload)
    print(f"→ Status: {r.status_code}")
    print(f"→ Response: {r.text}")
    
    if r.status_code in [200, 201]:
        response_data = r.json()
        thread_id = response_data.get("id")
        print(f"✅ Thread created with ID: {thread_id}")
        return thread_id
    else:
        print(f"❌ Failed to create thread")
        return None

def test_create_comment(thread_id, parent_id=None):
    print("💬 Creating comment...")
    payload = {
        "thread_referencia_id": thread_id,
        "author_name": f"Bot {unique_id}",
        "author_email_hash": f"bot-{unique_id}@example.com",
        "content": f"Hello world from {unique_id}!",
        "is_approved": 1
    }
    
    if parent_id:
        payload["parent_id"] = parent_id
    
    endpoint = f"{BASE_URL}/create/comments?Instance={INSTANCE_ID}"
    r = requests.post(endpoint, headers=HEADERS, json=payload)
    print(f"→ Status: {r.status_code}")
    print(f"→ Response: {r.text}")
    
    if r.status_code in [200, 201]:
        response_data = r.json()
        comment_id = response_data.get("id")
        print(f"✅ Comment created with ID: {comment_id}")
        return comment_id
    else:
        print(f"❌ Failed to create comment")
        return None

def test_update_comment(comment_id):
    print("🛠 Updating comment...")
    payload = {
        "content": f"Updated comment content from {unique_id}!",
        "is_approved": 1
    }
    
    endpoint = f"{BASE_URL}/update/comments/{comment_id}?Instance={INSTANCE_ID}"
    r = requests.put(endpoint, headers=HEADERS, json=payload)
    print(f"→ Status: {r.status_code}")
    print(f"→ Response: {r.text}")
    
    if r.status_code == 200:
        print(f"✅ Comment updated successfully")
        return True
    else:
        print(f"❌ Failed to update comment")
        return False

def test_read_comments():
    print("📖 Reading comments...")
    endpoint = f"{BASE_URL}/read/comments?Instance={INSTANCE_ID}"
    r = requests.get(endpoint, headers=HEADERS)
    print(f"→ Status: {r.status_code}")
    
    if r.status_code == 200:
        response_data = r.json()
        comments = response_data.get("data", [])
        print(f"✅ Found {len(comments)} comments")
        return comments
    else:
        print(f"❌ Failed to read comments")
        return []

def test_read_threads():
    print("📖 Reading threads...")
    endpoint = f"{BASE_URL}/read/threads?Instance={INSTANCE_ID}"
    r = requests.get(endpoint, headers=HEADERS)
    print(f"→ Status: {r.status_code}")
    
    if r.status_code == 200:
        response_data = r.json()
        threads = response_data.get("data", [])
        print(f"✅ Found {len(threads)} threads")
        return threads
    else:
        print(f"❌ Failed to read threads")
        return []

# ========================
# MAIN TEST FLOW
# ========================

def run_tests(mode="basic"):
    print(f"🚀 Running tests in mode: {mode}\n")
    print(f"API Key: {API_KEY[:10]}...")
    print(f"Instance ID: {INSTANCE_ID}")
    print(f"Base URL: {BASE_URL}")
    print(f"Unique ID: {unique_id}\n")

    # Test 1: Create user
    user_id = test_create_user()
    
    if not user_id:
        print("❌ Failed to create user. Cannot proceed with tests.")
        return

    if mode == "basic":
        print("✅ Basic test completed (user creation only)")
        return

    # Test 2: Create thread
    thread_id = test_create_thread(user_id)
    if not thread_id:
        print("❌ Failed to create thread. Cannot proceed with full test.")
        return

    # Test 3: Create root comment
    print("\n--- Creating root comment ---")
    comment_id = test_create_comment(thread_id)

    # Test 4: Create reply (level 2)
    print("\n--- Creating reply (level 2) ---")
    reply1 = test_create_comment(thread_id, parent_id=comment_id)

    # Test 5: Create reply to reply (level 3)
    print("\n--- Creating reply to reply (level 3) ---")
    reply2 = test_create_comment(thread_id, parent_id=reply1)

    # Test 6: Test nesting limit (level 4)
    print("\n--- Testing comment nesting limit (level 4) ---")
    test_create_comment(thread_id, parent_id=reply2)

    # Test 7: Update comment
    print("\n--- Updating comment ---")
    if comment_id:
        test_update_comment(comment_id)

    # Test 8: Read all comments
    print("\n--- Reading all comments ---")
    test_read_comments()

    # Test 9: Read all threads
    print("\n--- Reading all threads ---")
    test_read_threads()

    print("\n✅ Full test flow completed!")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Final autotester for NoCodeBackend API")
    parser.add_argument("--mode", choices=["basic", "full"], default="basic", help="Tipo de teste: basic ou full")
    args = parser.parse_args()

    run_tests(args.mode)