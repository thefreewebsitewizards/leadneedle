#!/usr/bin/env python3
"""
Test network access within Flask app context
"""
import threading
import smtplib
import ssl
import socket
import os
import sys
import time
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import Flask app
from app import app

# Load environment like Flask does
from dotenv import load_dotenv
load_dotenv()

def test_smtp_in_flask_context(thread_type, use_app_context=True):
    """Test SMTP connection from within Flask app context"""
    print(f"\n🧵 Testing SMTP from {thread_type} thread (Flask context: {use_app_context})...")
    print(f"   Thread ID: {threading.current_thread().ident}")
    print(f"   Thread name: {threading.current_thread().name}")
    print(f"   Is daemon: {threading.current_thread().daemon}")
    
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    def run_test():
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
                return
                
            print(f"   🔗 Testing SSL SMTP connection...")
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=10) as server:
                print(f"   ✅ SSL connection established")
                
                print(f"   🔐 Testing SMTP login...")
                server.login(sender_email, sender_password)
                print(f"   ✅ SMTP login successful")
                
                print(f"   ✅ {thread_type} thread (Flask context: {use_app_context}): ALL TESTS PASSED")
                
        except socket.gaierror as e:
            print(f"   ❌ {thread_type} thread DNS resolution failed: {e}")
        except socket.timeout as e:
            print(f"   ❌ {thread_type} thread connection timeout: {e}")
        except ConnectionRefusedError as e:
            print(f"   ❌ {thread_type} thread connection refused: {e}")
        except OSError as e:
            print(f"   ❌ {thread_type} thread network error: {e}")
            if e.errno == 101:
                print(f"   💀 {thread_type} thread: 'Network is unreachable' - FOUND THE ISSUE!")
        except Exception as e:
            print(f"   ❌ {thread_type} thread unexpected error: {e}")
    
    if use_app_context:
        with app.app_context():
            run_test()
    else:
        run_test()

def main():
    print("🔍 Testing network access within Flask app context...")
    
    # Test in main thread without Flask context
    print("\n📍 Testing in MAIN thread (NO Flask context):")
    test_smtp_in_flask_context("MAIN", use_app_context=False)
    
    # Test in main thread with Flask context
    print("\n📍 Testing in MAIN thread (WITH Flask context):")
    test_smtp_in_flask_context("MAIN", use_app_context=True)
    
    # Test in daemon thread without Flask context
    print("\n👻 Starting DAEMON thread test (NO Flask context)...")
    daemon_thread_no_context = threading.Thread(
        target=test_smtp_in_flask_context, 
        args=("DAEMON", False), 
        daemon=True
    )
    daemon_thread_no_context.start()
    daemon_thread_no_context.join()
    
    # Test in daemon thread with Flask context
    print("\n👻 Starting DAEMON thread test (WITH Flask context)...")
    daemon_thread_with_context = threading.Thread(
        target=test_smtp_in_flask_context, 
        args=("DAEMON", True), 
        daemon=True
    )
    daemon_thread_with_context.start()
    daemon_thread_with_context.join()
    
    print("\n🏁 All Flask context tests completed!")

if __name__ == "__main__":
    main()