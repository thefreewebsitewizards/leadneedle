#!/usr/bin/env python3
"""
Test that exactly replicates the Flask email queue scenario
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

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment like Flask does
from dotenv import load_dotenv
load_dotenv()

class TestEmailQueue:
    def __init__(self):
        self.email_queue = queue.Queue()
        self.worker_thread = None
        self.running = False
    
    def start_worker(self):
        """Start the background email worker thread - EXACTLY like Flask app"""
        if self.worker_thread and self.worker_thread.is_alive():
            print("Email worker already running")
            return
        
        self.running = True
        # This is EXACTLY how Flask starts the daemon thread
        self.worker_thread = threading.Thread(target=self._email_worker, daemon=True)
        self.worker_thread.start()
        print("✅ Email worker thread started")
    
    def _email_worker(self):
        """Email worker - EXACTLY like Flask implementation"""
        print(f"🔄 Email worker started processing queue")
        print(f"🔄 Worker thread ID: {threading.current_thread().ident}")
        print(f"🔄 Is daemon: {threading.current_thread().daemon}")
        
        while self.running:
            try:
                # Get email from queue with timeout
                email_data = self.email_queue.get(timeout=1)
                print(f"📨 Worker got email from queue: {email_data['type']} to {email_data['to']}")
                
                success = self._send_email(email_data)
                
                if success:
                    print(f"✅ Successfully sent {email_data['type']} email to {email_data['to']}")
                else:
                    print(f"❌ Failed to send {email_data['type']} email to {email_data['to']}")
                
                # Mark task as done
                self.email_queue.task_done()
                
            except queue.Empty:
                # No emails in queue, continue loop
                continue
            except Exception as e:
                print(f"❌ Email worker error: {e}")
                continue
        
        print("🔄 Email worker stopped")
    
    def _send_email(self, email_data):
        """Send a single email - EXACTLY like Flask implementation"""
        print(f"[{email_data['type']}] 🎯 _send_email method called")
        
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        
        try:
            print(f"[{email_data['type']}] 🔗 Connecting to smtp.gmail.com:465...")
            
            # Test raw socket first
            print(f"[{email_data['type']}] 🔍 Testing raw socket...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex(('smtp.gmail.com', 465))
            sock.close()
            
            if result != 0:
                print(f"[{email_data['type']}] ❌ Raw socket failed: {result}")
                return False
            else:
                print(f"[{email_data['type']}] ✅ Raw socket successful")
            
            # Now try SMTP SSL - EXACTLY like Flask
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
            print(f"[{email_data['type']}] ✅ SMTP SSL connection established")
            
            server.login(sender_email, sender_password)
            print(f"[{email_data['type']}] ✅ Authentication successful")
            
            server.quit()
            print(f"[{email_data['type']}] ✅ Email sending simulation successful")
            return True
            
        except socket.gaierror as e:
            print(f"[{email_data['type']}] ❌ DNS resolution failed: {e}")
        except socket.timeout as e:
            print(f"[{email_data['type']}] ❌ Connection timeout: {e}")
        except ConnectionRefusedError as e:
            print(f"[{email_data['type']}] ❌ Connection refused: {e}")
        except OSError as e:
            print(f"[{email_data['type']}] ❌ Network error: {e}")
            if e.errno == 101:
                print(f"[{email_data['type']}] 💀 'Network is unreachable' - REPRODUCED THE BUG!")
        except Exception as e:
            print(f"[{email_data['type']}] ❌ Unexpected error: {e}")
        
        return False
    
    def queue_email(self, email_type, to_email, subject, body):
        """Queue an email - EXACTLY like Flask"""
        email_data = {
            'type': email_type,
            'to': to_email,
            'subject': subject,
            'body': body
        }
        
        self.email_queue.put(email_data)
        print(f"📧 Queued {email_type} email to {to_email}")

def main():
    print("🔍 Testing EXACT Flask email queue scenario...")
    
    # Create email queue EXACTLY like Flask
    test_queue = TestEmailQueue()
    
    # Start worker EXACTLY like Flask
    test_queue.start_worker()
    
    # Wait a moment for worker to initialize
    time.sleep(0.5)
    
    # Queue an email EXACTLY like Flask does
    test_queue.queue_email(
        email_type='notification',
        to_email='dylan@thefreewebsitewizards.com',
        subject='🚀 Test Email',
        body='Test email body'
    )
    
    # Wait for processing
    print("⏳ Waiting for email processing...")
    time.sleep(15)  # Give it time to process
    
    # Stop worker
    test_queue.running = False
    
    print("🏁 Test completed!")

if __name__ == "__main__":
    main()