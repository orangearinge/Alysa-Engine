import firebase_admin
from firebase_admin import credentials
import os
import json
import base64

def initialize_firebase():
    try:
        # Check if already initialized to avoid error
        if not firebase_admin._apps:
            # You can load credentials from environment variable or a file
            # Ideally, use an environment variable containing the path to the service account JSON
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            
            # Fallback: Check if serviceAccountKey.json exists in root
            if not cred_path and os.path.exists('serviceAccountKey.json'):
                cred_path = 'serviceAccountKey.json'
                print(f"Found {cred_path} in current directory. Using it.")

            if cred_path:
                 if not os.path.exists(cred_path):
                     raise FileNotFoundError(f"Firebase credentials file not found at: {cred_path}")
                     
                 cred = credentials.Certificate(cred_path)
                 firebase_admin.initialize_app(cred)
                 print(f"Firebase Admin SDK initialized with credentials from: {cred_path}")
            else:
                # Alternatively, use default Application Default Credentials (ADC)
                print("Warning: FIREBASE_CREDENTIALS_PATH not found and no serviceAccountKey.json found.")
                print("Attempting to use default credentials (ADC). This requires GOOGLE_APPLICATION_CREDENTIALS or running on GCP.")
                try:
                    firebase_admin.initialize_app()
                    print("Firebase Admin SDK initialized with ADC.")
                except Exception as adc_err:
                     print(f"Failed to initialize with ADC: {adc_err}")
                     raise adc_err
                
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize Firebase Admin SDK: {e}")
        # We re-raise the exception so the app fails to start if Firebase is critical
        raise e
