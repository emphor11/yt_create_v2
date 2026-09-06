"""One-time YouTube OAuth 2.0 authorization helper script.

Instructions:
1. Go to Google Cloud Console (https://console.cloud.google.com/).
2. Select or create a project and enable the "YouTube Data API v3".
3. Configure the OAuth Consent Screen (External or Internal).
4. Go to Credentials -> Create Credentials -> OAuth client ID.
5. Application type: "Desktop app".
6. Download the JSON file and save it as:
   backend/credentials/client_secrets.json
7. Run this script:
   python backend/scripts/authenticate_youtube.py
8. Complete the login flow in your browser.
9. A token file will be saved to:
   backend/credentials/youtube_token.json
"""
import sys
from pathlib import Path

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Error: google-auth-oauthlib is not installed.")
    print("Run: pip install google-auth-oauthlib google-api-python-client")
    sys.exit(1)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    credentials_dir = backend_root / "credentials"
    credentials_dir.mkdir(parents=True, exist_ok=True)

    client_secrets = credentials_dir / "client_secrets.json"
    token_file = credentials_dir / "youtube_token.json"

    if not client_secrets.exists():
        print("=" * 70)
        print("MISSING: backend/credentials/client_secrets.json")
        print("=" * 70)
        print("To get client_secrets.json:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Enable 'YouTube Data API v3'.")
        print("3. Create an OAuth 2.0 Client ID with type 'Desktop app'.")
        print(f"4. Download the JSON file and save it to: {client_secrets}")
        print("5. Then run this script again.")
        print("=" * 70)
        sys.exit(1)

    print(f"Loading client secrets from: {client_secrets}")
    flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets), scopes=SCOPES)
    creds = flow.run_local_server(port=0)

    token_file.write_text(creds.to_json(), encoding="utf-8")
    print("=" * 70)
    print("SUCCESS: YouTube authorization complete!")
    print(f"Token saved to: {token_file}")
    print("You can now run Stage 12 (youtube_upload) from the UI.")
    print("=" * 70)


if __name__ == "__main__":
    main()
