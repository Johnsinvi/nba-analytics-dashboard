"""
upload_to_onedrive.py
Uploads NBA data CSVs to OneDrive using the Microsoft Graph API.
Runs inside GitHub Actions — reads credentials from environment variables.

Required environment variables (set as GitHub Secrets):
  TENANT_ID           - Azure AD tenant ID (from App Registration)
  CLIENT_ID           - Azure AD app client ID
  CLIENT_SECRET       - Azure AD app client secret
  ONEDRIVE_FOLDER     - OneDrive folder path, e.g. "NBA Dashboard/data"
"""

import os
import sys
import glob
import requests

# ── Config ────────────────────────────────────────────────────────────────────

TENANT_ID      = os.environ["TENANT_ID"]
CLIENT_ID      = os.environ["CLIENT_ID"]
CLIENT_SECRET  = os.environ["CLIENT_SECRET"]
FOLDER_PATH    = os.environ.get("ONEDRIVE_FOLDER", "NBA Dashboard/data")

CSV_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
CSV_FILES = ["player_stats.csv", "team_standings.csv", "game_log.csv", "advanced_stats.csv"]

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


# ── Step 1: Get access token (client credentials flow) ───────────────────────

def get_access_token() -> str:
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    resp = requests.post(url, data={
        "grant_type":    "client_credentials",
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope":         "https://graph.microsoft.com/.default",
    }, timeout=30)
    resp.raise_for_status()
    token = resp.json()["access_token"]
    print("✓ Access token acquired")
    return token


# ── Step 2: Get the signed-in user's OneDrive drive ID ───────────────────────

def get_drive_id(token: str) -> str:
    # Application-level access: use /users/{upn}/drive
    # We store the UPN (email) as ONEDRIVE_USER in secrets
    upn = os.environ.get("ONEDRIVE_USER", "")
    if not upn:
        raise ValueError("Set ONEDRIVE_USER secret to your Microsoft 365 email address")

    url = f"{GRAPH_BASE}/users/{upn}/drive"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    resp.raise_for_status()
    drive_id = resp.json()["id"]
    print(f"✓ Drive ID: {drive_id}")
    return drive_id, upn


# ── Step 3: Upload a single file ─────────────────────────────────────────────

def upload_file(token: str, drive_id: str, upn: str, local_path: str, filename: str):
    remote_path = f"{FOLDER_PATH}/{filename}".lstrip("/")
    url = f"{GRAPH_BASE}/users/{upn}/drives/{drive_id}/root:/{remote_path}:/content"

    with open(local_path, "rb") as f:
        data = f.read()

    resp = requests.put(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type":  "text/csv",
        },
        data=data,
        timeout=60,
    )
    resp.raise_for_status()
    item = resp.json()
    print(f"  ✓ Uploaded {filename} → {item.get('webUrl', remote_path)}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=== NBA Data → OneDrive Upload ===")

    token = get_access_token()
    drive_id, upn = get_drive_id(token)

    success = 0
    for filename in CSV_FILES:
        local_path = os.path.join(CSV_DIR, filename)
        if not os.path.exists(local_path):
            print(f"  ⚠ Skipping {filename} — not found at {local_path}")
            continue
        try:
            upload_file(token, drive_id, upn, local_path, filename)
            success += 1
        except requests.HTTPError as e:
            print(f"  ✗ Failed to upload {filename}: {e}")
            print(f"    Response: {e.response.text[:300]}")
            sys.exit(1)

    print(f"\n=== Done: {success}/{len(CSV_FILES)} files uploaded to OneDrive ===")


if __name__ == "__main__":
    main()
