#!/usr/bin/env python3
"""
Quick test to verify current SMTP configuration is working
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_smtp_sending():
    """Test SMTP sending with current configuration"""
    
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    print(f"🔍 Testing SMTP with:")
    print(f"📧 Sender: {sender_email}")
    print(f"🔑 Password: {'*' * len(sender_password) if sender_password else 'NOT SET'}")
    
    if not sender_email or not sender_password:
        print("❌ Missing email credentials in .env file")
        return False
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = "gaminggeek987@gmail.com"  # Test recipient
        msg['Subject'] = "🧪 SMTP Test - " + str(os.getpid())
        
        body = f"""
        This is a test email to verify SMTP is working.
        
        Sender: {sender_email}
        Time: {os.popen('date /t & time /t').read().strip()}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        print("🔗 Connecting to Gmail SMTP...")
        
        # Connect to Gmail SMTP
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.set_debuglevel(1)  # Enable debug output
        
        print("🔐 Logging in...")
        server.login(sender_email, sender_password)
        
        print("📤 Sending email...")
        text = msg.as_string()
        server.sendmail(sender_email, "gaminggeek987@gmail.com", text)
        
        print("✅ Email sent successfully!")
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ SMTP Error: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("🧪 Testing current SMTP configuration...")
    success = test_smtp_sending()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")