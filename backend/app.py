import os
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
import gspread
# Note: oauth2client.service_account is generally used for service accounts,
# but your current get_google_sheet uses pickle/Credentials for user authentication.
# Keeping the import as it's in your original file.
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv
load_dotenv()

# Import the website blueprint from the parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from website import website_bp

# Import background email queue system
from backend.email_queue import queue_notification_email, queue_confirmation_email, email_queue 

# Assuming these are in backend subfolder relative to app.py
# If they are in the same folder as app.py, adjust the import path
try:
    from backend.sms import send_sms
    from backend.database import insert_lead
    from backend.scheduler import book_appointment
    from backend.agent import AI_Sales_Agent
except ImportError as e:
    print(f"Warning: Could not import backend modules. Ensure paths are correct: {e}")
    # Define dummy functions/classes if you want the app to run without them for now
    def send_sms(*args, **kwargs): print("Dummy send_sms called")
    def insert_lead(*args, **kwargs): print("Dummy insert_lead called")
    def book_appointment(*args, **kwargs): print("Dummy book_appointment called")
    class AI_Sales_Agent:
        def process_sms(self, *args, **kwargs): return {"status": "dummy"}


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

app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Register blueprint if it exists and was imported successfully
app.register_blueprint(website_bp)
# if 'website_bp' in locals():
#     app.register_blueprint(website_bp)

def get_google_sheet(sheet_name="Submissions"):
    """
    Try to connect to Google Sheets using OAuth credentials from environment variable first,
    then fall back to local token.pickle file.
    """
    import pickle
    import json
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    # First, try OAuth credentials from environment variable (for production)
    oauth_creds_json = os.environ.get('GOOGLE_OAUTH_CREDENTIALS')
    if oauth_creds_json:
        try:
            print("🔑 Using OAuth credentials from environment variable")
            oauth_info = json.loads(oauth_creds_json)
            creds = Credentials(
                token=oauth_info.get('token'),
                refresh_token=oauth_info.get('refresh_token'),
                token_uri=oauth_info.get('token_uri'),
                client_id=oauth_info.get('client_id'),
                client_secret=oauth_info.get('client_secret'),
                scopes=SCOPES
            )
            
            # Refresh token if needed
            if not creds.valid and creds.refresh_token:
                creds.refresh(Request())
                print("🔄 OAuth token refreshed successfully")
            
            client = gspread.authorize(creds)
            return client.open_by_key("1batVITcT526zxkc8Qdf0_AKbORnrLRB7-wHdDKhcm9M").worksheet(sheet_name)
        except Exception as e:
            print(f"❌ OAuth credentials from environment failed: {e}")
    
    # Try service account authentication (legacy support)
    service_account_path = os.environ.get('GOOGLE_SERVICE_ACCOUNT_PATH')
    service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    
    if service_account_json:
        try:
            print("🔑 Trying service account from environment variable")
            service_account_info = json.loads(service_account_json)
            creds = service_account.Credentials.from_service_account_info(
                service_account_info, scopes=SCOPES)
            client = gspread.authorize(creds)
            return client.open_by_key("1batVITcT526zxkc8Qdf0_AKbORnrLRB7-wHdDKhcm9M").worksheet(sheet_name)
        except Exception as e:
            print(f"❌ Service account auth failed: {e}")
    
    if service_account_path and os.path.exists(service_account_path):
        try:
            print("🔑 Trying service account from file path")
            creds = service_account.Credentials.from_service_account_file(
                service_account_path, scopes=SCOPES)
            client = gspread.authorize(creds)
            return client.open_by_key("1batVITcT526zxkc8Qdf0_AKbORnrLRB7-wHdDKhcm9M").worksheet(sheet_name)
        except Exception as e:
            print(f"❌ Service account file auth failed: {e}")
    
    # Fall back to local token.pickle (for local development)
    print("🔑 Trying local token.pickle file")
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), 'token.pickle')
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
            print("🔄 Local token refreshed successfully")
        else:
            # For production deployment, we'll skip Google Sheets if no auth is available
            raise Exception("No valid Google Sheets authentication found. "
                          "Set GOOGLE_OAUTH_CREDENTIALS environment variable "
                          "or run manual_auth.py locally to generate token.pickle.")

    client = gspread.authorize(creds)
    return client.open_by_key("1batVITcT526zxkc8Qdf0_AKbORnrLRB7-wHdDKhcm9M").worksheet(sheet_name)

def send_notification_email(form_data, recipient="dylan@leadneedle.com"):
    """Queue notification email using background processing to avoid Flask request context issues"""
    try:
        print("📧 Queuing notification email...")
        queue_notification_email(form_data)
        print("✅ Notification email queued successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to queue notification email: {e}")
        return False

def send_confirmation_email(form_data):
    """Queue confirmation email using background processing to avoid Flask request context issues"""
    try:
        recipient_email = form_data.get('email')
        if not recipient_email:
            print("Warning: No recipient email provided for confirmation email.")
            return False
        
        print("📧 Queuing confirmation email...")
        queue_confirmation_email(recipient_email, form_data)
        print("✅ Confirmation email queued successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to queue confirmation email: {e}")
        return False

def handle_form_submission(sheet_name, recipient_email):
    try:
        print(f"🔍 Starting form submission for sheet: {sheet_name}")
        
        # Handle both JSON and form data
        data = None
        if request.is_json:
            print("📋 Processing JSON data")
            data = request.get_json()
        else:
            print("📋 Processing form data")
            data = request.form.to_dict()
        
        if not data:
            print("❌ No data received in request body")
            raise ValueError("No data received in the request body.")
        
        print(f"📝 Received form data: {list(data.keys())}")

        form_data = {
            'firstName': data.get('firstName'),
            'lastName': data.get('lastName'), # Added for completeness if frontend sends it
            'email': data.get('email'),
            'phoneNumber': data.get('phoneNumber') or data.get('phone'), # Handle both field names
            'websiteName': data.get('websiteName'),
            'websiteDescription': data.get('websiteDescription'),
            'hasWebsite': data.get('hasWebsite'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'service': data.get('service', 'Free Website Wizard'), # Allow frontend to specify, default if not
            'message': data.get('message', data.get('websiteDescription', '')) # Use message if present, fallback to description
        }

        print("🔗 Attempting to connect to Google Sheets...")
        try:
            sheet = get_google_sheet(sheet_name)
            print(f"✅ Successfully connected to Google Sheet: {sheet_name}")
        except Exception as sheet_error:
            print(f"❌ Google Sheets connection failed: {sheet_error}")
            # Continue without Google Sheets for now
            sheet = None

        if sheet:
            try:
                row = [
                    form_data['timestamp'],
                    form_data.get('firstName', ''),
                    form_data.get('email', ''),
                    form_data.get('phoneNumber', ''),
                    form_data.get('hasWebsite', ''),
                    form_data.get('websiteName', ''),
                    form_data.get('websiteDescription', '')
                ]
                # Ensure all values are strings before appending to Google Sheet
                row = [str(x) for x in row]
                sheet.append_row(row)
                print(f"✅ Data appended to Google Sheet '{sheet_name}'")
            except Exception as append_error:
                print(f"❌ Failed to append to Google Sheet: {append_error}")

        # Send notification and confirmation emails (with 10-second timeout)
        print("📧 Sending notification email...")
        try:
            if send_notification_email(form_data, "dylan@thefreewebsitewizards.com"):
                print("✅ Notification email sent successfully")
            else:
                print("❌ Failed to send notification email")
        except Exception as email_error:
            print(f"❌ Notification email error: {email_error}")
        
        print("📧 Sending confirmation email...")
        try:
            if send_confirmation_email(form_data):
                print("✅ Confirmation email sent successfully")
            else:
                print("❌ Failed to send confirmation email")
        except Exception as email_error:
            print(f"❌ Confirmation email error: {email_error}")
        
        print("✅ Form submission completed successfully")
        return {"status": "success", "message": "Form submitted successfully!"}
    except Exception as e:
        print(f"❌ Form submission error for '{sheet_name}': {e}")
        import traceback
        print(f"📋 Full traceback: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

@app.route('/submit-wizard', methods=['POST', 'OPTIONS'])
def submit_wizard_form():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    try:
        print("🚀 Submit wizard endpoint called")
        result = handle_form_submission("Website Submissions", "dylan@thefreewebsitewizards.com")
        return jsonify(result)
    except Exception as e:
        print(f"❌ Error in submit_wizard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/submit', methods=['POST', 'OPTIONS'])
def submit_contact_form():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    try:
        print("🚀 Submit contact form endpoint called")
        # Note: If this route is also expecting JSON, it will use request.get_json() as well.
        # If it's a different form sending application/x-www-form-urlencoded,
        # you might need a separate handler or more robust content-type checking.
        result = handle_form_submission("Submissions", "dylan@leadneedle.com")
        return jsonify(result)
    except Exception as e:
        print(f"❌ Error in submit_contact_form: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/privacy')
def redirect_privacy():
    return redirect('/privacy-policy', code=301)

@app.route('/submit-kim', methods=['POST'])
def submit_kim_contact_form():
    return handle_form_submission("Kims Fresh Start Leads", "FreshStartCleaningAug@gmail.com")

@app.route('/sms', methods=['POST'])
def receive_sms():
    # This route correctly uses request.get_json() already
    data = request.get_json()
    sms_text = data.get('sms_text')
    phone = data.get('phone')

    if not sms_text or not phone:
        return jsonify({"error": "Missing phone or sms_text"}), 400

    sales_agent = AI_Sales_Agent()
    responses = sales_agent.process_sms(phone, sms_text)

    start_time = datetime.utcnow() + timedelta(hours=1)

    insert_lead(
        name="Unknown",
        phone=phone,
        responses=str(responses),
        appointment_time=start_time.strftime("%Y-%m-%d %I:%M %p")
    )

    book_appointment(
        summary="Lead Needle Appointment",
        description=f"Auto-booked lead from {phone}",
        start_time=start_time
    )

    # Make sure send_sms is imported correctly from backend.sms
    # If it's not, this line will fail silently or loudly depending on where it's defined.
    send_sms(phone, "✅ Thanks! We've saved your info and booked your appointment.")
    return jsonify({"status": "success", "responses": responses})

# Add shutdown handler for proper cleanup of email worker thread
import atexit
from backend.email_queue import _email_queue_instance

def cleanup_email_worker():
    """Cleanup function to stop email worker thread on app shutdown"""
    try:
        if _email_queue_instance:
            _email_queue_instance.stop_worker()
            print("🧹 Email worker thread stopped during cleanup")
    except Exception as e:
        print(f"⚠️ Error during email worker cleanup: {e}")

# Register cleanup function
atexit.register(cleanup_email_worker)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)