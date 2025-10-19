#!/usr/bin/env python3
"""
Minimal SMTP test that progressively adds main app components
to identify what breaks SMTP connectivity
"""

import os
import sys
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def test_smtp_basic():
    """Test basic SMTP without any Flask imports"""
    print("=== Testing Basic SMTP (No Flask) ===")
    
    sender_email = os.getenv('SENDER_EMAIL', 'dylan@thefreewebsitewizards.com')
    sender_password = os.getenv('SENDER_PASSWORD', '')
    
    if not sender_password:
        print("❌ SENDER_PASSWORD not found")
        return False
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=3)
        server.login(sender_email, sender_password)
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email
        msg['Subject'] = f'Basic SMTP Test - {time.strftime("%Y-%m-%d %H:%M:%S")}'
        msg.attach(MIMEText('Basic SMTP test without Flask', 'plain'))
        
        server.send_message(msg)
        server.quit()
        
        print("✅ Basic SMTP test succeeded")
        return True
        
    except Exception as e:
        print(f"❌ Basic SMTP test failed: {e}")
        return False

def test_smtp_with_flask():
    """Test SMTP with Flask imports"""
    print("\n=== Testing SMTP with Flask Imports ===")
    
    from flask import Flask
    from flask_cors import CORS
    
    sender_email = os.getenv('SENDER_EMAIL', 'dylan@thefreewebsitewizards.com')
    sender_password = os.getenv('SENDER_PASSWORD', '')
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=3)
        server.login(sender_email, sender_password)
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email
        msg['Subject'] = f'Flask SMTP Test - {time.strftime("%Y-%m-%d %H:%M:%S")}'
        msg.attach(MIMEText('SMTP test with Flask imports', 'plain'))
        
        server.send_message(msg)
        server.quit()
        
        print("✅ Flask SMTP test succeeded")
        return True
        
    except Exception as e:
        print(f"❌ Flask SMTP test failed: {e}")
        return False

def test_smtp_with_gspread():
    """Test SMTP with gspread imports"""
    print("\n=== Testing SMTP with gspread Imports ===")
    
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    
    sender_email = os.getenv('SENDER_EMAIL', 'dylan@thefreewebsitewizards.com')
    sender_password = os.getenv('SENDER_PASSWORD', '')
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=3)
        server.login(sender_email, sender_password)
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email
        msg['Subject'] = f'gspread SMTP Test - {time.strftime("%Y-%m-%d %H:%M:%S")}'
        msg.attach(MIMEText('SMTP test with gspread imports', 'plain'))
        
        server.send_message(msg)
        server.quit()
        
        print("✅ gspread SMTP test succeeded")
        return True
        
    except Exception as e:
        print(f"❌ gspread SMTP test failed: {e}")
        return False

def test_smtp_with_backend_imports():
    """Test SMTP with backend module imports"""
    print("\n=== Testing SMTP with Backend Imports ===")
    
    # Add parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    try:
        from backend.sms import send_sms
        from backend.database import insert_lead
        from backend.scheduler import book_appointment
        from backend.agent import AI_Sales_Agent
        print("✅ Backend imports successful")
    except ImportError as e:
        print(f"⚠️ Backend import warning: {e}")
    
    sender_email = os.getenv('SENDER_EMAIL', 'dylan@thefreewebsitewizards.com')
    sender_password = os.getenv('SENDER_PASSWORD', '')
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=3)
        server.login(sender_email, sender_password)
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email
        msg['Subject'] = f'Backend SMTP Test - {time.strftime("%Y-%m-%d %H:%M:%S")}'
        msg.attach(MIMEText('SMTP test with backend imports', 'plain'))
        
        server.send_message(msg)
        server.quit()
        
        print("✅ Backend SMTP test succeeded")
        return True
        
    except Exception as e:
        print(f"❌ Backend SMTP test failed: {e}")
        return False

def test_smtp_with_google_auth():
    """Test SMTP with Google auth imports"""
    print("\n=== Testing SMTP with Google Auth Imports ===")
    
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google.oauth2 import service_account
        print("✅ Google auth imports successful")
    except ImportError as e:
        print(f"⚠️ Google auth import warning: {e}")
    
    sender_email = os.getenv('SENDER_EMAIL', 'dylan@thefreewebsitewizards.com')
    sender_password = os.getenv('SENDER_PASSWORD', '')
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=3)
        server.login(sender_email, sender_password)
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email
        msg['Subject'] = f'Google Auth SMTP Test - {time.strftime("%Y-%m-%d %H:%M:%S")}'
        msg.attach(MIMEText('SMTP test with Google auth imports', 'plain'))
        
        server.send_message(msg)
        server.quit()
        
        print("✅ Google Auth SMTP test succeeded")
        return True
        
    except Exception as e:
        print(f"❌ Google Auth SMTP test failed: {e}")
        return False

if __name__ == '__main__':
    print("🔍 Progressive SMTP Testing to Identify Network Issue")
    print("=" * 60)
    
    results = []
    
    # Test 1: Basic SMTP
    results.append(("Basic SMTP", test_smtp_basic()))
    
    # Test 2: SMTP with Flask
    results.append(("Flask SMTP", test_smtp_with_flask()))
    
    # Test 3: SMTP with gspread
    results.append(("gspread SMTP", test_smtp_with_gspread()))
    
    # Test 4: SMTP with backend imports
    results.append(("Backend SMTP", test_smtp_with_backend_imports()))
    
    # Test 5: SMTP with Google auth
    results.append(("Google Auth SMTP", test_smtp_with_google_auth()))
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY OF RESULTS:")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    # Identify the breaking point
    failed_tests = [name for name, success in results if not success]
    if failed_tests:
        print(f"\n🚨 First failure at: {failed_tests[0]}")
        print("This indicates where the network issue is introduced.")
    else:
        print("\n🎉 All tests passed! The issue may be request-context specific.")