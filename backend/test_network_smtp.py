#!/usr/bin/env python3
"""
Network diagnostic script to test SMTP connectivity issues
"""
import socket
import ssl
import smtplib
from dotenv import load_dotenv
import os

load_dotenv()

def test_socket_connection():
    """Test raw socket connection to Gmail SMTP"""
    print("🔌 Testing raw socket connection to smtp.gmail.com:465...")
    
    try:
        # Test IPv4 connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('smtp.gmail.com', 465))
        sock.close()
        
        if result == 0:
            print("✅ IPv4 socket connection successful")
            return True
        else:
            print(f"❌ IPv4 socket connection failed: Error {result}")
            return False
            
    except Exception as e:
        print(f"❌ Socket connection error: {e}")
        return False

def test_ssl_connection():
    """Test SSL connection to Gmail SMTP"""
    print("🔐 Testing SSL connection to smtp.gmail.com:465...")
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection(('smtp.gmail.com', 465), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname='smtp.gmail.com') as ssock:
                print("✅ SSL connection successful")
                print(f"📜 SSL Certificate: {ssock.getpeercert()['subject']}")
                return True
                
    except Exception as e:
        print(f"❌ SSL connection error: {e}")
        return False

def test_smtp_connection():
    """Test SMTP connection and authentication"""
    print("📧 Testing SMTP connection and authentication...")
    
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=10)
        server.set_debuglevel(0)  # Disable debug for cleaner output
        
        print("✅ SMTP connection established")
        
        # Test authentication
        sender_password = os.getenv('SENDER_PASSWORD')
        if sender_password:
            server.login("thefreewebsitewizard@gmail.com", sender_password)
            print("✅ SMTP authentication successful")
        else:
            print("❌ No sender password found in environment")
            
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ SMTP connection/auth error: {e}")
        return False

def test_network_interfaces():
    """Check network interface information"""
    print("🌐 Network interface information:")
    
    try:
        # Get local IP addresses
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"🏠 Hostname: {hostname}")
        print(f"🏠 Local IP: {local_ip}")
        
        # Test external connectivity
        external_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        external_sock.settimeout(5)
        result = external_sock.connect_ex(('8.8.8.8', 53))  # Google DNS
        external_sock.close()
        
        if result == 0:
            print("✅ External internet connectivity working")
        else:
            print("❌ External internet connectivity failed")
            
    except Exception as e:
        print(f"❌ Network interface error: {e}")

if __name__ == "__main__":
    print("🧪 Network SMTP Diagnostic Test")
    print("=" * 50)
    
    test_network_interfaces()
    print("-" * 30)
    
    socket_ok = test_socket_connection()
    print("-" * 30)
    
    if socket_ok:
        ssl_ok = test_ssl_connection()
        print("-" * 30)
        
        if ssl_ok:
            smtp_ok = test_smtp_connection()
        else:
            smtp_ok = False
    else:
        ssl_ok = False
        smtp_ok = False
    
    print("=" * 50)
    print("📊 Test Results Summary:")
    print(f"🔌 Socket Connection: {'✅ PASS' if socket_ok else '❌ FAIL'}")
    print(f"🔐 SSL Connection: {'✅ PASS' if ssl_ok else '❌ FAIL'}")
    print(f"📧 SMTP Auth: {'✅ PASS' if smtp_ok else '❌ FAIL'}")
    
    if not socket_ok:
        print("\n🔍 Troubleshooting suggestions:")
        print("- Check firewall settings")
        print("- Verify internet connection")
        print("- Try different network (mobile hotspot)")
        print("- Check if antivirus is blocking connections")