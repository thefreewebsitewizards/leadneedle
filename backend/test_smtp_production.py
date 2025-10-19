#!/usr/bin/env python3
"""
Test SMTP functionality in production environment
This script will help identify if emails are actually being sent or just marked as sent
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_smtp_connection():
    """Test SMTP connection and email sending"""
    
    # Get credentials from environment
    sender_email = os.getenv('SENDER_EMAIL', 'dylan@thefreewebsitewizards.com')
    sender_password = os.getenv('SENDER_PASSWORD', '')
    
    if not sender_password:
        logger.error("❌ SENDER_PASSWORD environment variable not set")
        return False
    
    logger.info(f"🧪 Testing SMTP with sender: {sender_email}")
    
    server = None
    try:
        # Connect to Gmail SMTP
        logger.info("🔗 Connecting to smtp.gmail.com:465...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
        
        # Enable debug output
        server.set_debuglevel(1)
        
        # Authenticate
        logger.info("🔐 Authenticating...")
        server.login(sender_email, sender_password)
        logger.info("✅ Authentication successful")
        
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email  # Send to self for testing
        msg['Subject'] = f"🧪 SMTP Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        msg['Message-ID'] = f"<{datetime.now().timestamp()}@leadneedle.com>"
        
        # Add body
        body = f"""
        <html>
        <body>
            <h2>SMTP Test Email</h2>
            <p>This is a test email sent at {datetime.now().isoformat()}</p>
            <p>If you receive this, SMTP is working correctly.</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        logger.info("📤 Sending test email...")
        logger.info(f"📧 Message size: {len(str(msg))} bytes")
        
        # Send email
        send_result = server.send_message(msg)
        logger.info(f"📬 SMTP send_message result: {send_result}")
        
        if send_result:
            logger.warning(f"⚠️ Some recipients were refused: {send_result}")
            return False
        else:
            logger.info("✅ All recipients accepted - email should be delivered")
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"🔐 Authentication failed: {e}")
        return False
        
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"📧 Recipients refused: {e}")
        return False
        
    except smtplib.SMTPException as e:
        logger.error(f"📧 SMTP error: {e}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False
        
    finally:
        if server:
            try:
                server.quit()
                logger.info("🔌 SMTP connection closed")
            except:
                pass

if __name__ == '__main__':
    logger.info("🚀 Starting SMTP production test...")
    success = test_smtp_connection()
    
    if success:
        logger.info("✅ SMTP test completed successfully")
        print("SUCCESS: SMTP is working correctly")
    else:
        logger.error("❌ SMTP test failed")
        print("FAILURE: SMTP is not working correctly")