#!/usr/bin/env python3
"""
Test to verify the sender email issue with Gmail SMTP
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_gmail_sender_mismatch():
    """Test sending with non-Gmail address through Gmail SMTP"""
    
    # Current configuration (problematic)
    sender_email = os.getenv('SENDER_EMAIL', 'dylan@thefreewebsitewizards.com')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    print(f"🔍 Environment check:")
    print(f"   SENDER_EMAIL: {sender_email}")
    print(f"   SENDER_PASSWORD: {'*' * len(sender_password) if sender_password else 'NOT SET'}")
    
    if not sender_password:
        print("❌ SENDER_PASSWORD not found in environment variables")
        return
    
    print(f"🧪 Testing Gmail SMTP with non-Gmail sender: {sender_email}")
    print("📋 This should demonstrate the silent failure issue")
    
    try:
        # Connect to Gmail SMTP
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        print("✅ Connected to Gmail SMTP")
        
        # Try to authenticate with non-Gmail address
        server.login(sender_email, sender_password)
        print("✅ Authentication appeared successful")
        
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email  # Send to self
        msg['Subject'] = "Test: Non-Gmail sender through Gmail SMTP"
        msg.attach(MIMEText("This is a test of sending with non-Gmail address through Gmail SMTP", 'plain'))
        
        # Send message
        result = server.send_message(msg)
        print(f"📬 Send result: {result}")
        
        if result:
            print("⚠️ Some recipients were refused!")
            print(f"Refused: {result}")
        else:
            print("✅ All recipients accepted by SMTP server")
            print("🔍 But this doesn't guarantee delivery!")
        
        server.quit()
        print("🔌 Connection closed")
        
        print("\n📝 DIAGNOSIS:")
        print("- Gmail SMTP accepts the message but may silently drop it")
        print("- Gmail requires sender email to match authenticated Gmail account")
        print("- Solution: Use a Gmail address as sender or use different SMTP server")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_gmail_sender_mismatch()