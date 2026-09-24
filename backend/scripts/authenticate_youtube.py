"""One-time YouTube OAuth 2.0 authorization helper script supporting dual accounts.

Usage:
  # Authenticate testing account:
  python backend/scripts/authenticate_youtube.py --account test

  # Authenticate production/real account:
  python backend/scripts/authenticate_youtube.py --account prod
"""
import argparse
import sys
from pathlib import Path

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("Error: Required Google client libraries are not installed.")
    print("Run: pip install google-auth-oauthlib google-api-python-client")
    sys.exit(1)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def authenticate(account_type: str) -> None:
    backend_root = Path(__file__).resolve().parents[1]
    credentials_dir = backend_root / "credentials"
    credentials_dir.mkdir(parents=True, exist_ok=True)

    is_prod = account_type.lower() in ("prod", "production", "real")
    account_label = "PRODUCTION (REAL)" if is_prod else "TESTING"

    # Check for dedicated client_secrets or shared client_secrets
    client_secrets = (
        credentials_dir / "client_secrets_prod.json"
        if is_prod and (credentials_dir / "client_secrets_prod.json").exists()
        else credentials_dir / "client_secrets.json"
    )

    token_file = (
        credentials_dir / "youtube_token_prod.json"
        if is_prod
        else credentials_dir / "youtube_token_test.json"
    )

    if not client_secrets.exists():
        print("=" * 70)
        print("MISSING CLIENT SECRETS FILE")
        print(f"Looked for: {client_secrets}")
        print("=" * 70)
        print("To get client_secrets.json:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Select your project and enable 'YouTube Data API v3'.")
        print("3. Under Credentials -> Create Credentials -> OAuth client ID (Desktop app).")
        print(f"4. Download the JSON and save as: {credentials_dir / 'client_secrets.json'}")
        print("=" * 70)
        sys.exit(1)

    print("=" * 70)
    print(f"AUTHENTICATING YOUTUBE ACCOUNT: [{account_label}]")
    print(f"Using Client Secrets: {client_secrets.name}")
    print(f"Target Token File:    {token_file.name}")
    print("=" * 70)
    print("A browser window will now open. Please log into the Google Account")
    print(f"associated with your {account_label} YouTube channel and click 'Allow'.\n")

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets), scopes=SCOPES)
    creds = flow.run_local_server(port=0)

    # Save credentials
    token_json = creds.to_json()
    token_file.write_text(token_json, encoding="utf-8")

    # If this is the test account, also sync legacy youtube_token.json for backwards compatibility
    if not is_prod:
        legacy_token = credentials_dir / "youtube_token.json"
        legacy_token.write_text(token_json, encoding="utf-8")

    # Fetch and verify the channel name to prevent any mixups
    channel_title = "Unknown Channel"
    channel_id = "Unknown ID"
    try:
        youtube = build("youtube", "v3", credentials=creds)
        response = youtube.channels().list(mine=True, part="snippet").execute()
        items = response.get("items", [])
        if items:
            channel_title = items[0]["snippet"].get("title", "Unknown Channel")
            channel_id = items[0].get("id", "Unknown ID")
    except Exception as exc:
        print(f"Warning: Could not fetch channel metadata: {exc}")

    print("\n" + "=" * 70)
    print(f"✅ SUCCESS: {account_label} YouTube Authorization Complete!")
    print(f"Channel Name:  \"{channel_title}\"")
    print(f"Channel ID:    {channel_id}")
    print(f"Token Saved:   {token_file}")
    print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(description="Authorize YouTube Account (Test or Production)")
    parser.add_argument(
        "--account",
        choices=["test", "prod", "production"],
        default=None,
        help="Specify which account to authenticate ('test' or 'prod')",
    )
    args = parser.parse_args()

    account = args.account
    if not account:
        print("\nWhich YouTube account do you want to authenticate?")
        print("  1) Testing Account  (saves to youtube_token_test.json)")
        print("  2) Production Account (saves to youtube_token_prod.json)")
        choice = input("Enter choice [1 or 2]: ").strip()
        account = "prod" if choice == "2" else "test"

    authenticate(account)


if __name__ == "__main__":
    main()
