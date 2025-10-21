#!/usr/bin/env python3
"""
Background Email Queue System
Processes emails in a separate thread to bypass Flask request context network issues
"""

import os
import time
import threading
import queue
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

# Configure logging with more explicit settings for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True  # Override any existing logging configuration
)
logger = logging.getLogger(__name__)

class EmailQueue:
    def __init__(self):
        self.email_queue = queue.Queue()
        self.worker_thread = None
        self.running = False
        self.stats = {
            'sent': 0,
            'failed': 0,
            'queued': 0
        }
    
    def start_worker(self):
        """Start the background email worker thread"""
        if self.worker_thread and self.worker_thread.is_alive():
            logger.info("Email worker already running")
            return
        
        self.running = True
        # Use regular thread instead of daemon to avoid network connectivity issues
        self.worker_thread = threading.Thread(target=self._email_worker, daemon=False)
        self.worker_thread.start()
        logger.info("✅ Email worker thread started (non-daemon)")
    
    def stop_worker(self):
        """Stop the background email worker thread"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("🛑 Email worker thread stopped")
    
    def queue_email(self, email_type, to_email, subject, body, sender_email=None, sender_password=None):
        """Queue an email for background processing"""
        email_data = {
            'type': email_type,
            'to': to_email,
            'subject': subject,
            'body': body,
            'sender_email': sender_email or os.getenv('SENDER_EMAIL', 'dylan@thefreewebsitewizards.com'),
            'sender_password': sender_password or os.getenv('SENDER_PASSWORD', ''),
            'timestamp': datetime.now().isoformat(),
            'attempts': 0,
            'max_attempts': 3
        }
        
        logger.info(f"📥 Adding email to queue: {email_type} to {to_email}")
        logger.info(f"📥 Queue instance ID: {id(self.email_queue)}")
        logger.info(f"📥 Queue size before put: {self.email_queue.qsize()}")
        
        self.email_queue.put(email_data)
        self.stats['queued'] += 1
        
        logger.info(f"📥 Queue size after put: {self.email_queue.qsize()}")
        logger.info(f"📧 Queued {email_type} email to {to_email} (Queue size: {self.email_queue.qsize()})")
        
        # Check if worker thread is actually alive
        thread_alive = self.worker_thread.is_alive() if self.worker_thread else False
        logger.info(f"🔄 Worker status - running: {self.running}, Thread alive: {thread_alive}")
        
        # Start worker if not running OR if thread is dead
        if not self.running or not thread_alive:
            if not self.running:
                logger.info("🚀 Starting worker thread - not running")
            else:
                logger.warning("💀 Worker thread is dead but running=True, restarting...")
                self.running = False  # Reset the flag
            self.start_worker()
        else:
            logger.info(f"✅ Worker thread is healthy and running")
    
    def _email_worker(self):
        """Background worker that processes emails from the queue"""
        logger.info("🔄 Email worker started processing queue")
        logger.info(f"🔄 Worker thread ID: {threading.current_thread().ident}")
        logger.info(f"🔄 Queue instance ID in worker: {id(self.email_queue)}")
        
        while self.running:
            try:
                # Get email from queue with timeout
                logger.debug("🔍 Worker checking for emails in queue...")
                logger.debug(f"🔍 Current queue size: {self.email_queue.qsize()}")
                logger.debug(f"🔍 Worker running status: {self.running}")
                
                email_data = self.email_queue.get(timeout=1)
                logger.info(f"📨 Worker got email from queue: {email_data['type']} to {email_data['to']}")
                
                success = self._send_email(email_data)
                
                if success:
                    self.stats['sent'] += 1
                    logger.info(f"✅ Successfully sent {email_data['type']} email to {email_data['to']}")
                else:
                    self.stats['failed'] += 1
                    logger.error(f"❌ Failed to send {email_data['type']} email to {email_data['to']}")
                
                # Mark task as done
                self.email_queue.task_done()
                logger.info(f"✅ Task marked as done for {email_data['type']} email")
                
            except queue.Empty:
                # No emails in queue, continue loop
                logger.debug("📭 No emails in queue, continuing...")
                continue
            except Exception as e:
                logger.error(f"❌ Email worker error: {e}")
                logger.error(f"❌ Exception type: {type(e).__name__}")
                import traceback
                logger.error(f"❌ Full traceback: {traceback.format_exc()}")
                continue
        
        logger.info("🔄 Email worker stopped")
    
    def _send_email(self, email_data):
        """Send a single email with robust retry logic"""
        logger.info(f"[{email_data['type']}] 🎯 _send_email method called")
        
        max_attempts = email_data.get('max_attempts', 3)
        server = None
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"[{email_data['type']}] 🚀 Attempt {attempt}/{max_attempts} to {email_data['to']}")
            logger.info(f"[{email_data['type']}] 📧 From: {email_data['sender_email']}")
            logger.info(f"[{email_data['type']}] 📧 Subject: {email_data['subject']}")
            
            try:
                # Pre-connection network test with longer timeout
                logger.info(f"[{email_data['type']}] 🔍 Testing network connectivity...")
                import socket
                network_test_passed = False
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(15)  # Increased timeout
                    try:
                        result = sock.connect_ex(('smtp.gmail.com', 465))
                        if result == 0:
                            logger.info(f"[{email_data['type']}] ✅ Network connectivity verified")
                            network_test_passed = True
                        elif result == 11:  # WSAEWOULDBLOCK - Resource temporarily unavailable
                            logger.info(f"[{email_data['type']}] ⚠️ Network test returned code 11 (non-blocking), proceeding with SMTP connection...")
                            network_test_passed = True  # Treat as non-fatal, proceed anyway
                        else:
                            logger.warning(f"[{email_data['type']}] ⚠️ Network test failed with code {result}, but proceeding with SMTP connection...")
                            network_test_passed = True  # Still proceed, let SMTP connection be the real test
                    finally:
                        sock.close()
                except Exception as e:
                    logger.warning(f"[{email_data['type']}] ⚠️ Network test exception: {e}, proceeding with SMTP connection...")
                    network_test_passed = True  # Proceed anyway, let SMTP be the real test
                
                if not network_test_passed:
                    raise ConnectionError(f"Network connectivity test failed")
                    
                # If we get here, either the test passed or we're proceeding despite the test
                
                logger.info(f"[{email_data['type']}] 🔗 Connecting to smtp.gmail.com:465...")
                
                # Create SMTP connection with increased timeout and retry logic
                connection_attempts = 3
                for conn_attempt in range(1, connection_attempts + 1):
                    try:
                        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=20)  # Increased timeout
                        logger.info(f"[{email_data['type']}] ✅ SMTP SSL connection established (attempt {conn_attempt})")
                        break
                    except Exception as conn_error:
                        logger.error(f"[{email_data['type']}] ❌ SMTP connection attempt {conn_attempt} failed: {conn_error}")
                        if conn_attempt < connection_attempts:
                            logger.info(f"[{email_data['type']}] ⏳ Waiting 3s before connection retry...")
                            time.sleep(3)
                        else:
                            raise
                
                # Enable debug output for SMTP - but capture it in our logs
                # Note: SMTP debug goes to stderr, so we need to capture it
                logger.info(f"[{email_data['type']}] 🔧 Enabling SMTP debug output...")
                server.set_debuglevel(0)  # Disable built-in debug to avoid stderr spam
                
                # Manual SMTP command logging with retry
                logger.info(f"[{email_data['type']}] 🔐 Sending EHLO command...")
                try:
                    ehlo_response = server.ehlo()
                    logger.info(f"[{email_data['type']}] 📋 EHLO response: {ehlo_response}")
                except Exception as ehlo_error:
                    logger.error(f"[{email_data['type']}] ❌ EHLO failed: {ehlo_error}")
                    raise
                
                logger.info(f"[{email_data['type']}] 🔐 Authenticating with Gmail...")
                try:
                    server.login(email_data['sender_email'], email_data['sender_password'])
                    logger.info(f"[{email_data['type']}] ✅ Authentication successful")
                except Exception as auth_error:
                    logger.error(f"[{email_data['type']}] ❌ Authentication failed: {auth_error}")
                    raise
                
                # Create message
                logger.info(f"[{email_data['type']}] 📝 Creating email message...")
                msg = MIMEMultipart()
                msg['From'] = email_data['sender_email']
                msg['To'] = email_data['to']
                msg['Subject'] = email_data['subject']
                msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
                msg['Message-ID'] = f"<{datetime.now().timestamp()}@leadneedle.com>"
                
                # Add body
                msg.attach(MIMEText(email_data['body'], 'html'))
                logger.info(f"[{email_data['type']}] ✅ Email message created")
                
                logger.info(f"[{email_data['type']}] 📤 Sending email...")
                logger.info(f"[{email_data['type']}] 📧 Message size: {len(str(msg))} bytes")
                
                # Send email and capture response
                send_result = server.send_message(msg)
                logger.info(f"[{email_data['type']}] 📬 SMTP send_message result: {send_result}")
                
                # Additional verification - try to get server response
                try:
                    # Get the last server response
                    last_response = server.noop()  # No-op command to get server status
                    logger.info(f"[{email_data['type']}] 🔍 Server status after send: {last_response}")
                except Exception as noop_error:
                    logger.warning(f"[{email_data['type']}] ⚠️ Could not get server status: {noop_error}")
                
                # Check if there were any refused recipients
                if send_result:
                    logger.warning(f"[{email_data['type']}] ⚠️ Some recipients were refused: {send_result}")
                    return False  # If recipients were refused, consider it a failure
                else:
                    logger.info(f"[{email_data['type']}] ✅ All recipients accepted by SMTP server")
                
                # Log detailed message info for debugging
                logger.info(f"[{email_data['type']}] 📋 Email details - From: {email_data['sender_email']}, To: {email_data['to']}, Subject: {email_data['subject'][:50]}...")
                
                # Verify sender email format
                if '@' not in email_data['sender_email'] or '.' not in email_data['sender_email']:
                    logger.error(f"[{email_data['type']}] ❌ Invalid sender email format: {email_data['sender_email']}")
                    return False
                
                server.quit()
                logger.info(f"[{email_data['type']}] 🔌 SMTP connection closed")
                
                logger.info(f"[{email_data['type']}] ✅ Attempt {attempt} completed successfully")
                return True
                
            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"[{email_data['type']}] 🔐 Authentication failed: {e}")
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                return False  # Don't retry auth failures
                
            except smtplib.SMTPRecipientsRefused as e:
                logger.error(f"[{email_data['type']}] 📧 Recipients refused: {e}")
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                return False  # Don't retry recipient failures
                
            except smtplib.SMTPException as e:
                logger.error(f"[{email_data['type']}] 📧 SMTP error: {e}")
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                
            except (ConnectionError, OSError, socket.error) as e:
                logger.error(f"[{email_data['type']}] 🌐 Network/Connection error: {e}")
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                
                # Special handling for "Network is unreachable" errors
                if hasattr(e, 'errno') and e.errno == 101:
                    logger.error(f"[{email_data['type']}] 💀 Network is unreachable - system-level network issue")
                
            except Exception as e:
                logger.error(f"[{email_data['type']}] ❌ Unexpected error: {e}")
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                
            # Retry logic with exponential backoff
            if attempt < max_attempts:
                # Increased wait time with jitter to avoid thundering herd
                base_wait = 2 ** attempt
                jitter = random.uniform(0.5, 1.5)  # Add randomness
                wait_time = int(base_wait * jitter)
                logger.info(f"[{email_data['type']}] ⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                logger.error(f"[{email_data['type']}] ❌ Failed after all {max_attempts} attempts")
                return False
        
        return False
    
    def get_stats(self):
        """Get email queue statistics"""
        return {
            **self.stats,
            'queue_size': self.email_queue.qsize(),
            'worker_running': self.running and self.worker_thread and self.worker_thread.is_alive()
        }
    
    def wait_for_completion(self, timeout=30):
        """Wait for all queued emails to be processed"""
        logger.info("⏳ Waiting for email queue to complete...")
        
        start_time = time.time()
        while not self.email_queue.empty() and (time.time() - start_time) < timeout:
            time.sleep(0.5)
        
        if self.email_queue.empty():
            logger.info("✅ All emails processed")
            return True
        else:
            logger.warning(f"⚠️ Timeout after {timeout}s, {self.email_queue.qsize()} emails still queued")
            return False

# Global email queue instance (singleton pattern)
_email_queue_instance = None

def get_email_queue():
    """Get the singleton email queue instance"""
    global _email_queue_instance
    if _email_queue_instance is None:
        _email_queue_instance = EmailQueue()
    return _email_queue_instance

# For backward compatibility
email_queue = get_email_queue()

def queue_notification_email(form_data):
    """Queue a notification email for the admin"""
    subject = f"🚀 New Website Submission - {form_data.get('firstName', 'Unknown')}"
    
    body = f"""
    <html>
    <body>
        <h2>New Website Submission Received</h2>
        <p><strong>Name:</strong> {form_data.get('firstName', 'N/A')}</p>
        <p><strong>Email:</strong> {form_data.get('email', 'N/A')}</p>
        <p><strong>Phone:</strong> {form_data.get('phoneNumber', 'N/A')}</p>
        <p><strong>Country:</strong> {form_data.get('countryName', 'N/A')}</p>
        <p><strong>Has Web Hosting:</strong> {form_data.get('hasWebHosting', 'N/A')}</p>
        <p><strong>Website Description:</strong></p>
        <p>{form_data.get('websiteDescription', 'N/A')}</p>
        <p><strong>Source:</strong> {form_data.get('source', 'N/A')}</p>
        <p><strong>Timestamp:</strong> {form_data.get('timestamp', 'N/A')}</p>
        
        <hr>
        <p><em>This email was sent via background queue to avoid Flask request context issues.</em></p>
    </body>
    </html>
    """
    
    admin_email = os.getenv('SENDER_EMAIL', 'dylan@thefreewebsitewizards.com')
    
    email_queue.queue_email(
        email_type='notification',
        to_email=admin_email,
        subject=subject,
        body=body
    )

def queue_confirmation_email(user_email, form_data):
    """Queue a confirmation email for the user"""
    subject = "✅ Thank you for your website submission!"
    
    body = f"""
    <html>
    <body>
        <h2>Thank you for your submission!</h2>
        <p>Hi {form_data.get('firstName', 'there')},</p>
        
        <p>We've received your website submission and will be in touch soon!</p>
        
        <h3>Your Submission Details:</h3>
        <p><strong>Name:</strong> {form_data.get('firstName', 'N/A')}</p>
        <p><strong>Email:</strong> {form_data.get('email', 'N/A')}</p>
        <p><strong>Phone:</strong> {form_data.get('phoneNumber', 'N/A')}</p>
        <p><strong>Has Web Hosting:</strong> {form_data.get('hasWebHosting', 'N/A')}</p>
        
        <p>We'll review your requirements and get back to you within 24 hours.</p>
        
        <p>Best regards,<br>
        The Free Website Wizards Team</p>
        
        <hr>
        <p><em>This email was sent via background queue for improved reliability.</em></p>
    </body>
    </html>
    """
    
    email_queue.queue_email(
        email_type='confirmation',
        to_email=user_email,
        subject=subject,
        body=body
    )

# Auto-start the email worker when module is imported
email_queue.start_worker()

if __name__ == '__main__':
    # Test the email queue
    print("🧪 Testing Email Queue System")
    
    test_form_data = {
        'firstName': 'Test User',
        'email': 'test@example.com',
        'phoneNumber': '+1234567890',
        'countryName': 'Test Country',
        'hasWebHosting': 'Yes',
        'websiteDescription': 'Test website description',
        'source': 'Test',
        'timestamp': datetime.now().isoformat()
    }
    
    # Queue test emails
    queue_notification_email(test_form_data)
    queue_confirmation_email('test@example.com', test_form_data)
    
    # Wait for completion
    email_queue.wait_for_completion()
    
    # Print stats
    stats = email_queue.get_stats()
    print(f"📊 Email Queue Stats: {stats}")
    
    # Stop worker
    email_queue.stop_worker()