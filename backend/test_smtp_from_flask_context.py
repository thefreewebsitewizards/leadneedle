#!/usr/bin/env python3
"""
Test SMTP connectivity from within Flask app context
"""
import os
import sys
import smtplib
import ssl
import socket
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment like Flask does
from dotenv import load_dotenv
load_dotenv()

def test_smtp_from_flask_context():
    print("🔍 Testing SMTP from Flask context...")
    
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    print(f"📧 Using email: {sender_email}")
    print(f"🔑 Using password: {sender_password[:4]}...{sender_password[-4:]}")
    
    try:
        print("🔗 Testing raw socket connection to smtp.gmail.com:465...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('smtp.gmail.com', 465))
        sock.close()
        
        if result == 0:
            print("✅ Raw socket connection successful")
        else:
            print(f"❌ Raw socket connection failed: {result}")
            return
            
        print("🔗 Testing SSL SMTP connection...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=10) as server:
            print("✅ SSL connection established")
            
            print("🔐 Testing SMTP login...")
            server.login(sender_email, sender_password)
            print("✅ SMTP login successful")
            
            print("📧 Testing email send...")
            msg = f"""From: {sender_email}
To: {sender_email}
Subject: Test from Flask Context

This is a test email from Flask context.
"""
            server.sendmail(sender_email, [sender_email], msg)
            print("✅ Email sent successfully")
            
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
    except socket.timeout as e:
        print(f"❌ Connection timeout: {e}")
    except ConnectionRefusedError as e:
        print(f"❌ Connection refused: {e}")
    except OSError as e:
        print(f"❌ Network error: {e}")
        if e.errno == 101:
            print("   This is 'Network is unreachable' - same error as Flask!")
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP authentication failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"   Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_smtp_from_flask_context()