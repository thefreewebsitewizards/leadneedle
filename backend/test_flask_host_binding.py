#!/usr/bin/env python3
"""
Test if Flask's host binding affects daemon thread network access
"""
import threading
import smtplib
import ssl
import socket
import os
import sys
import time
import queue
from pathlib import Path
from flask import Flask

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment like Flask does
from dotenv import load_dotenv
load_dotenv()

def test_smtp_connection(test_name):
    """Test SMTP connection with detailed logging"""
    print(f"\n🧵 {test_name}")
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
            return False
            
        print(f"   🔗 Testing SSL SMTP connection...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=10) as server:
            print(f"   ✅ SSL connection established")
            
            print(f"   🔐 Testing SMTP login...")
            server.login(sender_email, sender_password)
            print(f"   ✅ SMTP login successful")
            
            print(f"   ✅ {test_name}: ALL TESTS PASSED")
            return True
            
    except socket.gaierror as e:
        print(f"   ❌ {test_name} DNS resolution failed: {e}")
    except socket.timeout as e:
        print(f"   ❌ {test_name} connection timeout: {e}")
    except ConnectionRefusedError as e:
        print(f"   ❌ {test_name} connection refused: {e}")
    except OSError as e:
        print(f"   ❌ {test_name} network error: {e}")
        if e.errno == 101:
            print(f"   💀 {test_name}: 'Network is unreachable' - REPRODUCED!")
    except Exception as e:
        print(f"   ❌ {test_name} unexpected error: {e}")
    
    return False

def test_with_flask_app(host_binding):
    """Test network access with different Flask host bindings"""
    print(f"\n🌐 Testing with Flask app bound to: {host_binding}")
    
    # Create Flask app with specific host binding
    app = Flask(__name__)
    
    @app.route('/test')
    def test_route():
        return "Test"
    
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(
        target=lambda: app.run(host=host_binding, port=10002, debug=False, use_reloader=False),
        daemon=True
    )
    flask_thread.start()
    
    # Wait for Flask to start
    time.sleep(2)
    
    # Test network access in daemon thread while Flask is running
    daemon_thread = threading.Thread(
        target=test_smtp_connection,
        args=(f"Daemon thread with Flask on {host_binding}",),
        daemon=True
    )
    daemon_thread.start()
    daemon_thread.join()
    
    # Stop Flask (it will stop when main thread exits since it's daemon)
    print(f"   Flask app on {host_binding} test completed")

def main():
    print("🔍 Testing Flask host binding effects on daemon thread network access...")
    
    # Test 1: No Flask app running
    print("\n📍 Baseline test - No Flask app running:")
    daemon_thread = threading.Thread(
        target=test_smtp_connection,
        args=("Daemon thread - No Flask",),
        daemon=True
    )
    daemon_thread.start()
    daemon_thread.join()
    
    # Test 2: Flask bound to localhost (127.0.0.1)
    test_with_flask_app("127.0.0.1")
    
    # Test 3: Flask bound to all interfaces (0.0.0.0) - like production
    test_with_flask_app("0.0.0.0")
    
    # Test 4: Flask bound to specific local IP
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"\n🏠 Local IP detected: {local_ip}")
        test_with_flask_app(local_ip)
    except Exception as e:
        print(f"❌ Could not determine local IP: {e}")
    
    print("\n🏁 Flask host binding tests completed!")

if __name__ == "__main__":
    main()