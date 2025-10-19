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

# Also create a console handler to ensure logs appear
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

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
        self.worker_thread = threading.Thread(target=self._email_worker, daemon=True)
        self.worker_thread.start()
        logger.info("✅ Email worker thread started")
    
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
        
        self.email_queue.put(email_data)
        self.stats['queued'] += 1
        
        logger.info(f"📧 Queued {email_type} email to {to_email} (Queue size: {self.email_queue.qsize()})")
        
        # Start worker if not running
        if not self.running:
            self.start_worker()
    
    def _email_worker(self):
        """Background worker that processes emails from the queue"""
        logger.info("🔄 Email worker started processing queue")
        
        while self.running:
            try:
                # Get email from queue with timeout
                email_data = self.email_queue.get(timeout=1)
                
                success = self._send_email(email_data)
                
                if success:
                    self.stats['sent'] += 1
                    logger.info(f"✅ Successfully sent {email_data['type']} email to {email_data['to']}")
                else:
                    self.stats['failed'] += 1
                    logger.error(f"❌ Failed to send {email_data['type']} email to {email_data['to']}")
                
                # Mark task as done
                self.email_queue.task_done()
                
            except queue.Empty:
                # No emails in queue, continue loop
                continue
            except Exception as e:
                logger.error(f"❌ Email worker error: {e}")
                continue
        
        logger.info("🔄 Email worker stopped")
    
    def _send_email(self, email_data):
        """Send a single email with retry logic"""
        max_attempts = email_data['max_attempts']
        
        for attempt in range(1, max_attempts + 1):
            server = None
            try:
                logger.info(f"[{email_data['type']}] 🚀 Attempt {attempt}/{max_attempts} to {email_data['to']}")
                logger.info(f"[{email_data['type']}] 📧 From: {email_data['sender_email']}")
                logger.info(f"[{email_data['type']}] 📧 Subject: {email_data['subject']}")
                
                # Use SSL method (port 465) - this works outside Flask request context
                logger.info(f"[{email_data['type']}] 🔗 Connecting to smtp.gmail.com:465...")
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
                
                # Enable debug output for SMTP - but capture it in our logs
                # Note: SMTP debug goes to stderr, so we need to capture it
                logger.info(f"[{email_data['type']}] 🔧 Enabling SMTP debug output...")
                server.set_debuglevel(0)  # Disable built-in debug to avoid stderr spam
                
                # Manual SMTP command logging
                logger.info(f"[{email_data['type']}] 🔐 Sending EHLO command...")
                ehlo_response = server.ehlo()
                logger.info(f"[{email_data['type']}] 📋 EHLO response: {ehlo_response}")
                
                logger.info(f"[{email_data['type']}] 🔐 Authenticating with Gmail...")
                server.login(email_data['sender_email'], email_data['sender_password'])
                logger.info(f"[{email_data['type']}] ✅ Authentication successful")
                
                # Create message
                msg = MIMEMultipart()
                msg['From'] = email_data['sender_email']
                msg['To'] = email_data['to']
                msg['Subject'] = email_data['subject']
                msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
                msg['Message-ID'] = f"<{datetime.now().timestamp()}@leadneedle.com>"
                
                # Add body
                msg.attach(MIMEText(email_data['body'], 'html'))
                
                logger.info(f"[{email_data['type']}] 📤 Sending email...")
                logger.info(f"[{email_data['type']}] 📧 Message size: {len(str(msg))} bytes")
                
                # Send email and capture response
                send_result = server.send_message(msg)
                logger.info(f"[{email_data['type']}] 📬 SMTP send_message result: {send_result}")
                
                # Check if there were any refused recipients
                if send_result:
                    logger.warning(f"[{email_data['type']}] ⚠️ Some recipients were refused: {send_result}")
                else:
                    logger.info(f"[{email_data['type']}] ✅ All recipients accepted")
                
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
                
            except Exception as e:
                logger.error(f"[{email_data['type']}] ❌ Unexpected error: {e}")
                if server:
                    try:
                        server.quit()
                    except:
                        pass
                
                if attempt < max_attempts:
                    # Wait before retry (exponential backoff)
                    wait_time = 2 ** attempt
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

# Global email queue instance
email_queue = EmailQueue()

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