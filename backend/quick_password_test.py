#!/usr/bin/env python3
"""
Quick test to verify if current password works
"""
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

def test_password():
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    print(f"Testing: {sender_email}")
    print(f"Password: {sender_password}")
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        server.login(sender_email, sender_password)
        print("✅ Password works!")
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Password failed: {e}")
        return False

if __name__ == "__main__":
    test_password()