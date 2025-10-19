#!/usr/bin/env python3
"""
Flask Network Debugging Script
Tests SMTP connectivity within Flask request context to identify network binding issues
"""

import os
import socket
import smtplib
import threading
from flask import Flask, request, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

app = Flask(__name__)

def test_basic_connectivity():
    """Test basic network connectivity"""
    results = {}
    
    # Test DNS resolution
    try:
        socket.gethostbyname('smtp.gmail.com')
        results['dns_gmail'] = 'SUCCESS'
    except Exception as e:
        results['dns_gmail'] = f'FAILED: {e}'
    
    # Test socket connections
    for host, port in [('smtp.gmail.com', 465), ('smtp.gmail.com', 587), ('google.com', 80)]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            results[f'{host}:{port}'] = 'OPEN' if result == 0 else f'CLOSED ({result})'
        except Exception as e:
            results[f'{host}:{port}'] = f'ERROR: {e}'
    
    return results

def test_smtp_connection(method='ssl'):
    """Test SMTP connection with detailed logging"""
    sender_email = os.getenv('SENDER_EMAIL', 'dylan@thefreewebsitewizards.com')
    sender_password = os.getenv('SENDER_PASSWORD', '')
    
    if not sender_password:
        return {'error': 'SENDER_PASSWORD not found'}
    
    try:
        if method == 'ssl':
            # SSL method (port 465)
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        else:
            # STARTTLS method (port 587)
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
            server.starttls()
        
        server.login(sender_email, sender_password)
        
        # Try to send a test email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email  # Send to self
        msg['Subject'] = f'Flask Network Test - {method.upper()} - {time.strftime("%Y-%m-%d %H:%M:%S")}'
        
        body = f"""
        This is a test email sent from Flask request context using {method.upper()} method.
        
        Thread ID: {threading.get_ident()}
        Process ID: {os.getpid()}
        Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server.send_message(msg)
        server.quit()
        
        return {'success': True, 'method': method, 'thread_id': threading.get_ident()}
        
    except Exception as e:
        return {'error': str(e), 'method': method, 'thread_id': threading.get_ident()}

@app.route('/debug-network', methods=['GET', 'POST'])
def debug_network():
    """Debug network connectivity within Flask request context"""
    
    results = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'thread_id': threading.get_ident(),
        'process_id': os.getpid(),
        'request_method': request.method,
        'basic_connectivity': {},
        'smtp_tests': {}
    }
    
    # Test basic connectivity
    print(f"[DEBUG] Testing basic connectivity in thread {threading.get_ident()}")
    results['basic_connectivity'] = test_basic_connectivity()
    
    # Test SMTP connections
    print(f"[DEBUG] Testing SMTP SSL connection in thread {threading.get_ident()}")
    results['smtp_tests']['ssl'] = test_smtp_connection('ssl')
    
    print(f"[DEBUG] Testing SMTP STARTTLS connection in thread {threading.get_ident()}")
    results['smtp_tests']['starttls'] = test_smtp_connection('starttls')
    
    # Test environment variables
    results['environment'] = {
        'SENDER_EMAIL': os.getenv('SENDER_EMAIL', 'NOT_SET'),
        'SENDER_PASSWORD_LENGTH': len(os.getenv('SENDER_PASSWORD', '')),
        'FLASK_ENV': os.getenv('FLASK_ENV', 'NOT_SET')
    }
    
    print(f"[DEBUG] Network debug results: {results}")
    
    return jsonify(results)

@app.route('/test-simple-socket')
def test_simple_socket():
    """Test simple socket connection within Flask context"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('smtp.gmail.com', 465))
        sock.close()
        
        return jsonify({
            'success': result == 0,
            'result_code': result,
            'thread_id': threading.get_ident(),
            'message': 'Connection successful' if result == 0 else f'Connection failed with code {result}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'thread_id': threading.get_ident()
        })

if __name__ == '__main__':
    print("Starting Flask Network Debug Server...")
    print("Test endpoints:")
    print("  GET/POST /debug-network - Comprehensive network debugging")
    print("  GET /test-simple-socket - Simple socket connection test")
    
    app.run(host='0.0.0.0', port=10001, debug=True)