#!/usr/bin/env python3
"""
Test SMTP with original sender email to isolate the issue
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_original_sender():
    """Test SMTP with dylan@thefreewebsitewizards.com sender"""
    
    # Gmail SMTP configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    sender_email = "dylan@thefreewebsitewizards.com"  # Original sender
    sender_password = os.getenv('SENDER_PASSWORD')
    recipient_email = "gaminggeek987@gmail.com"
    
    print(f"🔧 Testing SMTP with original sender: {sender_email}")
    print(f"📧 Recipient: {recipient_email}")
    print(f"🔑 Password: {'*' * len(sender_password) if sender_password else 'NOT SET'}")
    print("-" * 50)
    
    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "Test Email - Original Sender Domain"
    
    body = """
    This is a test email to verify if the original sender email works.
    
    Sender: dylan@thefreewebsitewizards.com
    Gmail Account: thefreewebsitewizard@gmail.com
    
    If you receive this, the domain mismatch is NOT the issue.
    """
    
    message.attach(MIMEText(body, "plain"))
    
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        print("🔌 Connecting to Gmail SMTP...")
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.set_debuglevel(1)  # Enable debug output
            
            print("🔐 Authenticating...")
            server.login("thefreewebsitewizard@gmail.com", sender_password)  # Login with Gmail account
            
            print("📤 Sending email...")
            text = message.as_string()
            result = server.sendmail(sender_email, recipient_email, text)
            
            print("✅ Email sent successfully!")
            print(f"📊 Server response: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Testing Original Sender Email Configuration")
    print("=" * 60)
    success = test_original_sender()
    print("=" * 60)
    if success:
        print("✅ Test completed successfully - Check your email!")
    else:
        print("❌ Test failed - Check the error messages above")