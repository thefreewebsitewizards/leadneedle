#!/usr/bin/env python3
"""
Test what environment variables the Flask app is actually seeing
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment like Flask does
from dotenv import load_dotenv
load_dotenv()

def test_current_env():
    print("🔍 Testing current environment variables...")
    
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    print(f"📧 SENDER_EMAIL: {sender_email}")
    print(f"🔑 SENDER_PASSWORD: {sender_password[:4]}...{sender_password[-4:] if sender_password else 'None'}")
    print(f"🔑 Password length: {len(sender_password) if sender_password else 0}")
    
    # Check if it matches the expected new password
    expected_new = "zwwm ntzf dbhj qwri"
    if sender_password == expected_new:
        print("✅ Flask app is using the NEW password")
    else:
        print("❌ Flask app is NOT using the new password")
        print(f"Expected: {expected_new}")
        print(f"Actual:   {sender_password}")

if __name__ == "__main__":
    test_current_env()