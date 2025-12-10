# Firebase Admin SDK Setup for Backend

To fix the "Default Firebase app does not exist" or "Invalid token" errors, you must configure the Firebase Admin SDK.

## CRITICAL: You need the "serviceAccountKey.json" file.

1.  **Go to Firebase Console**: [https://console.firebase.google.com/](https://console.firebase.google.com/)
2.  Select your project ("alysa-speak" or similar).
3.  Click the **Gear Icon** (Project Settings) > **Service accounts**.
4.  Click **Generate new private key**.
5.  This will download a JSON file.

### How to install it:

**Option A (Recommended):**

1.  Rename the downloaded file to **`serviceAccountKey.json`**.
2.  Move it into the **`alysa-engine/`** folder (next to `app.py` and `requirements.txt`).
3.  Restart your backend (`python app.py` or `flask run`). The app will auto-detect it.

**Option B (Environment Variable):**

1.  Save the file anywhere.
2.  In `alysa-engine/.env`, set:
    ```env
    FIREBASE_CREDENTIALS_PATH=/absolute/path/to/your/file.json
    ```
3.  Restart your backend.

---

**Verification:**
When you start the backend, you should see:
`Firebase Admin SDK initialized with credentials from: ...`
If you see "CRITICAL ERROR", read the error message to see what went wrong.
