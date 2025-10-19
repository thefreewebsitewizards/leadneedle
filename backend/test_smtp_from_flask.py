#!/usr/bin/env python3
"""
Test SMTP from Flask Environment
This script runs SMTP tests within the Flask application context
"""

import os
import sys
import smtplib
import socket
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Flask app to get environment variables
from app import app

def test_smtp_in_flask_context():
    """Test SMTP within Flask application context"""
    with app.app_context():
        print("🚀 Testing SMTP within Flask Environment...")
        print("=" * 50)
        
        # Get environment variables (using same names as Flask app)
        email = os.getenv('SENDER_EMAIL')
        password = os.getenv('SENDER_PASSWORD')
        
        print(f"📧 SMTP Email: {email}")
        print(f"🔑 Password available: {'Yes' if password else 'No'}")
        if password:
            print(f"🔑 Password length: {len(password)}")
        
        if not email or not password:
            print("❌ Missing SMTP credentials in environment")
            return
        
        # Test different configurations
        configurations = [
            {
                'name': 'Current Flask Config (STARTTLS + localhost)',
                'server': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True,
                'use_ssl': False,
                'local_hostname': 'localhost'
            },
            {
                'name': 'Gmail SSL (465)',
                'server': 'smtp.gmail.com',
                'port': 465,
                'use_tls': False,
                'use_ssl': True,
                'local_hostname': None
            },
            {
                'name': 'Gmail STARTTLS without localhost',
                'server': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True,
                'use_ssl': False,
                'local_hostname': None
            }
        ]
        
        for config in configurations:
            print(f"\n🧪 Testing: {config['name']}")
            test_config(email, password, config)

def test_config(email, password, config):
    """Test a specific SMTP configuration"""
    try:
        print(f"   🔗 Connecting to {config['server']}:{config['port']}...")
        
        # Create connection with timeout
        if config['use_ssl']:
            server = smtplib.SMTP_SSL(config['server'], config['port'], timeout=5)
        else:
            if config['local_hostname']:
                server = smtplib.SMTP(config['server'], config['port'], timeout=5, local_hostname=config['local_hostname'])
            else:
                server = smtplib.SMTP(config['server'], config['port'], timeout=5)
        
        print(f"   ✅ Connected successfully")
        
        # Start TLS if needed
        if config['use_tls']:
            print("   🔐 Starting TLS...")
            server.starttls()
            print("   ✅ TLS enabled")
        
        # Login
        print("   🔑 Attempting login...")
        server.login(email, password)
        print("   ✅ Login successful")
        
        # Send test email
        print("   📧 Sending test email...")
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = email
        msg['Subject'] = f"Flask SMTP Test - {config['name']}"
        
        body = f"Test email from Flask environment using {config['name']} at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        msg.attach(MIMEText(body, 'plain'))
        
        server.send_message(msg)
        print("   ✅ Test email sent successfully")
        
        server.quit()
        print(f"   🎉 {config['name']} - ALL TESTS PASSED!")
        
        return True
        
    except Exception as e:
        print(f"   ❌ {config['name']} - Failed: {e}")
        print(f"   📝 Error type: {type(e).__name__}")
        return False

def test_network_from_flask():
    """Test network connectivity from Flask context"""
    print("\n🔍 Testing Network Connectivity from Flask...")
    
    hosts_to_test = [
        ('smtp.gmail.com', 587),
        ('smtp.gmail.com', 465),
        ('google.com', 80)
    ]
    
    for host, port in hosts_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"   ✅ {host}:{port} - Connection successful")
            else:
                print(f"   ❌ {host}:{port} - Connection failed (error {result})")
        except Exception as e:
            print(f"   ❌ {host}:{port} - Exception: {e}")

if __name__ == "__main__":
    test_network_from_flask()
    test_smtp_in_flask_context()