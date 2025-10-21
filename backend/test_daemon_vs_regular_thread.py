#!/usr/bin/env python3
"""
Test network access in daemon vs regular threads
"""
import threading
import smtplib
import ssl
import socket
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment like Flask does
from dotenv import load_dotenv
load_dotenv()

def test_smtp_connection(thread_type):
    """Test SMTP connection from within a thread"""
    print(f"\n🧵 Testing SMTP from {thread_type} thread...")
    print(f"   Thread ID: {threading.current_thread().ident}")
    print(f"   Thread name: {threading.current_thread().name}")
    print(f"   Is daemon: {threading.current_thread().daemon}")
    
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
            return
            
        print(f"   🔗 Testing SSL SMTP connection...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=10) as server:
            print(f"   ✅ SSL connection established")
            
            print(f"   🔐 Testing SMTP login...")
            server.login(sender_email, sender_password)
            print(f"   ✅ SMTP login successful")
            
            print(f"   ✅ {thread_type} thread: ALL TESTS PASSED")
            
    except socket.gaierror as e:
        print(f"   ❌ {thread_type} thread DNS resolution failed: {e}")
    except socket.timeout as e:
        print(f"   ❌ {thread_type} thread connection timeout: {e}")
    except ConnectionRefusedError as e:
        print(f"   ❌ {thread_type} thread connection refused: {e}")
    except OSError as e:
        print(f"   ❌ {thread_type} thread network error: {e}")
        if e.errno == 101:
            print(f"   💀 {thread_type} thread: 'Network is unreachable' - SAME ERROR AS FLASK!")
    except Exception as e:
        print(f"   ❌ {thread_type} thread unexpected error: {e}")

def main():
    print("🔍 Testing network access in different thread types...")
    
    # Test in main thread
    print("\n📍 Testing in MAIN thread:")
    test_smtp_connection("MAIN")
    
    # Test in regular (non-daemon) thread
    print("\n🧵 Starting REGULAR thread test...")
    regular_thread = threading.Thread(
        target=test_smtp_connection, 
        args=("REGULAR",), 
        daemon=False
    )
    regular_thread.start()
    regular_thread.join()
    
    # Test in daemon thread (like Flask email worker)
    print("\n👻 Starting DAEMON thread test...")
    daemon_thread = threading.Thread(
        target=test_smtp_connection, 
        args=("DAEMON",), 
        daemon=True
    )
    daemon_thread.start()
    daemon_thread.join()
    
    print("\n🏁 All thread tests completed!")

if __name__ == "__main__":
    main()