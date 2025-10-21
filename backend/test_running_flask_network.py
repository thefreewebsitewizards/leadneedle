#!/usr/bin/env python3
"""
Test network access by connecting to the running Flask app
"""
import requests
import time
import threading
import smtplib
import ssl
import socket
import os
from dotenv import load_dotenv

load_dotenv()

def test_smtp_in_current_process():
    """Test SMTP in the current process (not the Flask process)"""
    print("\n🧵 Testing SMTP in current process...")
    print(f"   Process ID: {os.getpid()}")
    print(f"   Thread ID: {threading.current_thread().ident}")
    
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    try:
        print(f"   🔗 Testing raw socket connection...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('smtp.gmail.com', 465))
        sock.close()
        
        if result == 0:
            print(f"   ✅ Raw socket connection successful")
        else:
            print(f"   ❌ Raw socket connection failed: {result}")
            return False
            
        print(f"   🔗 Testing SSL SMTP connection...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=10) as server:
            print(f"   ✅ SSL connection established")
            
            print(f"   🔐 Testing SMTP login...")
            server.login(sender_email, sender_password)
            print(f"   ✅ SMTP login successful")
            
            print(f"   ✅ Current process: ALL TESTS PASSED")
            return True
            
    except Exception as e:
        print(f"   ❌ Current process error: {e}")
        if hasattr(e, 'errno') and e.errno == 101:
            print(f"   💀 Current process: 'Network is unreachable'")
    
    return False

def trigger_flask_email():
    """Trigger an email through the Flask app to see what happens"""
    print("\n📧 Triggering email through Flask app...")
    
    # Submit a test form to trigger email
    form_data = {
        'firstName': 'Network Test',
        'email': 'test@example.com',
        'phoneNumber': '+1234567890',
        'countryCode': 'US',
        'countryName': 'United States',
        'hasWebHosting': 'No',
        'websiteDescription': 'Network connectivity test submission',
        'source': 'Network Test',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:10000/submit-wizard',
            json=form_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("   ✅ Form submission successful")
            print("   📧 Email should be queued - check Flask logs for network errors")
        else:
            print(f"   ❌ Form submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

def main():
    print("🔍 Testing network access in running Flask app...")
    
    # Test 1: SMTP in current process
    test_smtp_in_current_process()
    
    # Test 2: Trigger email through Flask
    trigger_flask_email()
    
    print("\n⏳ Waiting 15 seconds for Flask to process email...")
    time.sleep(15)
    
    print("\n🏁 Test completed! Check Flask app logs for email processing results.")

if __name__ == "__main__":
    main()