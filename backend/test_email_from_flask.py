import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_function():
    """Test the exact same email function as used in the Flask app"""
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.environ.get('SENDER_EMAIL', 'your-email@gmail.com')
        sender_password = os.environ.get('SENDER_PASSWORD', 'your-app-password')
        recipient = "dylan@thefreewebsitewizards.com"

        print(f"Testing email function with sender: {sender_email}")
        print(f"Password length: {len(sender_password) if sender_password else 0}")

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = "Test Email from Flask Context"

        body = "This is a test email sent using the exact same function as the Flask app."
        msg.attach(MIMEText(body, 'plain'))

        # Use the exact same connection method as Flask app
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, msg.as_string())
        server.quit()

        print("✅ Email sent successfully using Flask method!")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

if __name__ == "__main__":
    test_email_function()