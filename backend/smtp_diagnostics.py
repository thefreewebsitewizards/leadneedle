#!/usr/bin/env python3
"""
Comprehensive SMTP Diagnostics Script
Tests various SMTP configurations to identify network connectivity issues
"""

import smtplib
import socket
import os
import sys
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_basic_connectivity():
    """Test basic network connectivity"""
    print("🔍 Testing Basic Network Connectivity...")
    
    hosts_to_test = [
        ('smtp.gmail.com', 587),
        ('smtp.gmail.com', 465),
        ('smtp.gmail.com', 25),
        ('google.com', 80),
        ('8.8.8.8', 53)
    ]
    
    for host, port in hosts_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {host}:{port} - Connection successful")
            else:
                print(f"❌ {host}:{port} - Connection failed (error {result})")
        except Exception as e:
            print(f"❌ {host}:{port} - Exception: {e}")

def test_smtp_configurations():
    """Test different SMTP configurations"""
    print("\n🔍 Testing SMTP Configurations...")
    
    email = os.getenv('SMTP_EMAIL', 'dylan@thefreewebsitewizards.com')
    password = os.getenv('SMTP_PASSWORD', '')
    
    if not password:
        print("❌ SMTP_PASSWORD not found in environment variables")
        return
    
    print(f"📧 Using email: {email}")
    print(f"🔑 Password length: {len(password)}")
    
    configurations = [
        {
            'name': 'Gmail STARTTLS (587)',
            'server': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'use_ssl': False
        },
        {
            'name': 'Gmail SSL (465)',
            'server': 'smtp.gmail.com',
            'port': 465,
            'use_tls': False,
            'use_ssl': True
        },
        {
            'name': 'Gmail Plain (25)',
            'server': 'smtp.gmail.com',
            'port': 25,
            'use_tls': False,
            'use_ssl': False
        }
    ]
    
    for config in configurations:
        print(f"\n🧪 Testing: {config['name']}")
        test_smtp_config(email, password, config)

def test_smtp_config(email, password, config):
    """Test a specific SMTP configuration"""
    try:
        # Create connection
        if config['use_ssl']:
            server = smtplib.SMTP_SSL(config['server'], config['port'], timeout=10)
        else:
            server = smtplib.SMTP(config['server'], config['port'], timeout=10, local_hostname='localhost')
        
        print(f"   ✅ Connected to {config['server']}:{config['port']}")
        
        # Enable debug output
        server.set_debuglevel(1)
        
        # Start TLS if needed
        if config['use_tls']:
            server.starttls()
            print("   ✅ STARTTLS enabled")
        
        # Login
        server.login(email, password)
        print("   ✅ Login successful")
        
        # Send test email
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = email
        msg['Subject'] = f"SMTP Test - {config['name']}"
        
        body = f"Test email sent using {config['name']} configuration at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        msg.attach(MIMEText(body, 'plain'))
        
        server.send_message(msg)
        print("   ✅ Test email sent successfully")
        
        server.quit()
        print(f"   ✅ {config['name']} - ALL TESTS PASSED")
        
    except Exception as e:
        print(f"   ❌ {config['name']} - Failed: {e}")

def test_dns_resolution():
    """Test DNS resolution for SMTP servers"""
    print("\n🔍 Testing DNS Resolution...")
    
    domains = ['smtp.gmail.com', 'gmail.com', 'google.com']
    
    for domain in domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"✅ {domain} resolves to {ip}")
        except Exception as e:
            print(f"❌ {domain} - DNS resolution failed: {e}")

def test_firewall_ports():
    """Test if common SMTP ports are blocked"""
    print("\n🔍 Testing Firewall/Port Blocking...")
    
    smtp_servers = [
        ('smtp.gmail.com', [25, 465, 587]),
        ('smtp.outlook.com', [25, 465, 587]),
        ('smtp.yahoo.com', [25, 465, 587])
    ]
    
    for server, ports in smtp_servers:
        print(f"\n📡 Testing {server}:")
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((server, port))
                sock.close()
                
                if result == 0:
                    print(f"   ✅ Port {port} - Open")
                else:
                    print(f"   ❌ Port {port} - Blocked/Filtered")
            except Exception as e:
                print(f"   ❌ Port {port} - Error: {e}")

def main():
    """Run all diagnostic tests"""
    print("🚀 SMTP Diagnostics Starting...")
    print("=" * 50)
    
    # Test basic connectivity
    test_basic_connectivity()
    
    # Test DNS resolution
    test_dns_resolution()
    
    # Test firewall/ports
    test_firewall_ports()
    
    # Test SMTP configurations
    test_smtp_configurations()
    
    print("\n" + "=" * 50)
    print("🏁 SMTP Diagnostics Complete")

if __name__ == "__main__":
    main()