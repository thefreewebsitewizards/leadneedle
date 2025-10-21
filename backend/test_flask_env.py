#!/usr/bin/env python3
"""
Test Flask environment variable loading
"""
import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path (same as Flask app)
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_env_loading():
    """Test environment variable loading like Flask does"""
    print("🔧 Testing Environment Variable Loading")
    print("=" * 50)
    
    # Load environment variables (same as Flask app)
    load_dotenv()
    
    # Check critical environment variables
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    print(f"📧 SENDER_EMAIL: {sender_email}")
    print(f"🔑 SENDER_PASSWORD: {'*' * len(sender_password) if sender_password else 'NOT SET'}")
    
    # Check if they match expected values
    expected_email = "dylan@thefreewebsitewizards.com"
    expected_password_length = 19  # "ynif tjya wzvx axep" length
    
    print("-" * 30)
    print("✅ Environment Check Results:")
    
    if sender_email == expected_email:
        print(f"✅ SENDER_EMAIL correct: {sender_email}")
    else:
        print(f"❌ SENDER_EMAIL incorrect: Expected '{expected_email}', got '{sender_email}'")
    
    if sender_password and len(sender_password) == expected_password_length:
        print(f"✅ SENDER_PASSWORD appears correct (length: {len(sender_password)})")
    else:
        print(f"❌ SENDER_PASSWORD issue: Length {len(sender_password) if sender_password else 0}")
    
    # Test if we can import Flask modules
    print("-" * 30)
    print("📦 Testing Flask Module Imports:")
    
    try:
        from backend.email_queue import send_notification_email, send_confirmation_email
        print("✅ Email queue functions imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import email queue functions: {e}")
    
    # Check current working directory
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"📁 Script location: {__file__}")
    
    return sender_email == expected_email and sender_password and len(sender_password) == expected_password_length

if __name__ == "__main__":
    success = test_env_loading()
    print("=" * 50)
    if success:
        print("✅ Environment loading test PASSED")
    else:
        print("❌ Environment loading test FAILED")