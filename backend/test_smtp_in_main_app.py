#!/usr/bin/env python3
"""
Test SMTP within the exact same Flask configuration as the main app
"""

import os
import sys
import time
import threading
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Import the website blueprint from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from website import website_bp 

# Dummy imports to match main app
try:
    from backend.sms import send_sms
    from backend.database import insert_lead
    from backend.scheduler import book_appointment
    from backend.agent import AI_Sales_Agent
except ImportError as e:
    print(f"Warning: Could not import backend modules: {e}")
    def send_sms(*args, **kwargs): print("Dummy send_sms called")
    def insert_lead(*args, **kwargs): print("Dummy insert_lead called")
    def book_appointment(*args, **kwargs): print("Dummy book_appointment called")
    class AI_Sales_Agent:
        def process_sms(self, *args, **kwargs): return {"status": "dummy"}

# Create Flask app with EXACT same configuration as main app
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static')
)

CORS(app, 
     origins=["https://thefreewebsitewizards.com", "https://leadneedle.onrender.com", "http://localhost:*", "http://127.0.0.1:*"],
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     supports_credentials=True)

# Register the website blueprint
app.register_blueprint(website_bp)

def send_notification_email_test():
    """Test notification email sending with exact same logic as main app"""
    sender_email = os.getenv('SENDER_EMAIL', 'dylan@thefreewebsitewizards.com')
    sender_password = os.getenv('SENDER_PASSWORD', '')
    
    print(f"[Test Notification Email] Using: {sender_email}")
    print(f"[Test Notification Email] Password length: {len(sender_password)}")
    print(f"[Test Notification Email] Thread ID: {threading.get_ident()}")
    
    if not sender_password:
        return {"error": "SENDER_PASSWORD not found"}
    
    max_retries = 2
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Test Notification Email] Attempt {attempt}/{max_retries}")
            
            # Use SSL method (port 465) - same as main app
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=3)
            server.login(sender_email, sender_password)
            
            # Create test message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = sender_email
            msg['Subject'] = f'Test Notification Email - Main App Config - {time.strftime("%Y-%m-%d %H:%M:%S")}'
            
            body = f"""
            Test notification email from main app configuration.
            
            Thread ID: {threading.get_ident()}
            Process ID: {os.getpid()}
            Attempt: {attempt}/{max_retries}
            Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            server.send_message(msg)
            server.quit()
            
            print(f"[Test Notification Email] ✅ Attempt {attempt} succeeded")
            return {"success": True, "attempt": attempt, "thread_id": threading.get_ident()}
            
        except Exception as e:
            print(f"[Test Notification Email] Attempt {attempt} failed: {e}")
            if attempt == max_retries:
                print(f"[Test Notification Email] ❌ Failed after all retries: {e}")
                return {"error": str(e), "attempts": max_retries, "thread_id": threading.get_ident()}
            time.sleep(1)  # Wait before retry

@app.route('/test-smtp-main-config', methods=['GET', 'POST'])
def test_smtp_main_config():
    """Test SMTP with main app configuration"""
    
    results = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'thread_id': threading.get_ident(),
        'process_id': os.getpid(),
        'request_method': request.method,
        'flask_config': {
            'template_folder': app.template_folder,
            'static_folder': app.static_folder,
            'cors_enabled': True
        },
        'environment': {
            'SENDER_EMAIL': os.getenv('SENDER_EMAIL', 'NOT_SET'),
            'SENDER_PASSWORD_LENGTH': len(os.getenv('SENDER_PASSWORD', '')),
            'PORT': os.getenv('PORT', 'NOT_SET')
        }
    }
    
    print(f"[DEBUG] Testing SMTP with main app config in thread {threading.get_ident()}")
    
    # Test notification email
    results['notification_email_test'] = send_notification_email_test()
    
    print(f"[DEBUG] Main app config test results: {results}")
    
    return jsonify(results)

if __name__ == '__main__':
    print("Starting Flask SMTP Test Server with Main App Configuration...")
    print("Test endpoint: GET/POST /test-smtp-main-config")
    
    port = int(os.environ.get("PORT", 10002))
    app.run(host="0.0.0.0", port=port, debug=False)  # Match main app debug setting