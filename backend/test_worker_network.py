#!/usr/bin/env python3
"""
Test network connectivity from within a worker thread context
This mimics the exact environment where the Flask email worker runs
"""

import os
import threading
import time
import smtplib
import socket
import ssl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_network_in_thread():
    """Test network connectivity from within a thread (like Flask worker)"""
    print(f"🧵 Thread ID: {threading.current_thread().ident}")
    print(f"🧵 Thread name: {threading.current_thread().name}")
    print(f"🧵 Is daemon thread: {threading.current_thread().daemon}")
    
    # Test 1: Basic socket connection
    print("\n1️⃣ Testing raw socket connection to smtp.gmail.com:465...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('smtp.gmail.com', 465))
        sock.close()
        if result == 0:
            print("✅ Raw socket connection successful")
        else:
            print(f"❌ Raw socket connection failed with code: {result}")
    except Exception as e:
        print(f"❌ Raw socket connection error: {e}")
    
    # Test 2: SSL socket connection
    print("\n2️⃣ Testing SSL socket connection...")
    try:
        context = ssl.create_default_context()
        with socket.create_connection(('smtp.gmail.com', 465), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname='smtp.gmail.com') as ssock:
                print("✅ SSL socket connection successful")
                print(f"📋 SSL version: {ssock.version()}")
                print(f"📋 Cipher: {ssock.cipher()}")
    except Exception as e:
        print(f"❌ SSL socket connection error: {e}")
    
    # Test 3: SMTP connection
    print("\n3️⃣ Testing SMTP connection...")
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        print("✅ SMTP SSL connection established")
        
        # Test EHLO
        ehlo_response = server.ehlo()
        print(f"✅ EHLO response: {ehlo_response}")
        
        # Test authentication
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        
        if sender_email and sender_password:
            server.login(sender_email, sender_password)
            print("✅ SMTP authentication successful")
        else:
            print("⚠️ No credentials found, skipping auth test")
        
        server.quit()
        print("✅ SMTP connection closed cleanly")
        
    except Exception as e:
        print(f"❌ SMTP connection error: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")

def main():
    print("🧪 Testing Network Connectivity in Worker Thread Context")
    print("=" * 60)
    
    # Test in main thread first
    print("🔧 Testing in MAIN thread:")
    test_network_in_thread()
    
    print("\n" + "=" * 60)
    
    # Test in daemon thread (like Flask worker)
    print("🔧 Testing in DAEMON thread (Flask worker simulation):")
    worker_thread = threading.Thread(target=test_network_in_thread, daemon=True)
    worker_thread.start()
    worker_thread.join(timeout=30)  # Wait up to 30 seconds
    
    if worker_thread.is_alive():
        print("⚠️ Worker thread is still running (possible hang)")
    else:
        print("✅ Worker thread completed")

if __name__ == '__main__':
    main()