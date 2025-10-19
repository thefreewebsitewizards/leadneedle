#!/usr/bin/env python3
"""
Helper script to extract OAuth credentials from token.pickle 
and format them for the GOOGLE_OAUTH_CREDENTIALS environment variable.
"""

import pickle
import json
import os

def extract_oauth_credentials():
    """Extract OAuth credentials from token.pickle and format for environment variable."""
    
    token_path = os.path.join(os.path.dirname(__file__), 'token.pickle')
    
    if not os.path.exists(token_path):
        print("❌ token.pickle not found!")
        print("Run 'python manual_auth.py' first to generate the token file.")
        return None
    
    try:
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        # Extract the credentials data
        oauth_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        
        # Convert to JSON string
        oauth_json = json.dumps(oauth_data, indent=2)
        
        print("✅ OAuth credentials extracted successfully!")
        print("\n" + "="*60)
        print("GOOGLE_OAUTH_CREDENTIALS environment variable value:")
        print("="*60)
        print(oauth_json)
        print("="*60)
        print("\nCopy the JSON above and add it as the GOOGLE_OAUTH_CREDENTIALS")
        print("environment variable in your Render dashboard.")
        
        return oauth_data
        
    except Exception as e:
        print(f"❌ Error extracting credentials: {e}")
        return None

if __name__ == "__main__":
    extract_oauth_credentials()