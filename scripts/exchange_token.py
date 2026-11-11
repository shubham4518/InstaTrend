"""Utility script to exchange a short-lived Meta user token for a 60-day long-lived token.

Usage:
    python scripts/exchange_token.py
    python scripts/exchange_token.py --token <SHORT_LIVED_TOKEN> --secret <APP_SECRET>
"""
import argparse
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

GRAPH_API_VERSION = "v21.0"

def exchange_token(short_lived_token: str, client_secret: str, update_env: bool = True) -> dict:
    """Exchange short-lived Instagram user token for a 60-day long-lived token."""
    print("\n[1/3] Exchanging short-lived token with Meta Graph API...")
    url = "https://graph.instagram.com/access_token"
    params = {
        "grant_type": "ig_exchange_token",
        "client_secret": client_secret,
        "access_token": short_lived_token,
    }

    try:
        resp = requests.get(url, params=params, timeout=20)
        data = resp.json()
    except requests.RequestException as e:
        print(f"[-] Network error connecting to Meta: {e}")
        sys.exit(1)

    if "access_token" not in data:
        error_msg = data.get("error", {}).get("message", str(data))
        print(f"[-] Token exchange failed: {error_msg}")
        print("    Tip: Ensure your short-lived token has not expired and your App Secret is correct.")
        sys.exit(1)

    long_lived_token = data["access_token"]
    expires_in_seconds = data.get("expires_in", 5184000)
    expires_in_days = expires_in_seconds // 86400

    print(f"[+] Successfully obtained 60-day token! Valid for ~{expires_in_days} days.")

    # Fetch User Details
    print("\n[2/3] Querying Instagram profile details...")
    me_url = f"https://graph.instagram.com/{GRAPH_API_VERSION}/me"
    me_params = {
        "fields": "id,username,account_type",
        "access_token": long_lived_token,
    }

    try:
        me_resp = requests.get(me_url, params=me_params, timeout=20)
        user_data = me_resp.json()
    except requests.RequestException as e:
        print(f"[-] Failed to fetch profile details: {e}")
        user_data = {}

    user_id = user_data.get("id", "UNKNOWN")
    username = user_data.get("username", "UNKNOWN")
    account_type = user_data.get("account_type", "UNKNOWN")

    print(f"    • Instagram Handle: @{username}")
    print(f"    • User ID:          {user_id}")
    print(f"    • Account Type:     {account_type}")

    if account_type.upper() not in ("BUSINESS", "CREATOR"):
        print("\n[!] WARNING: Account type is not BUSINESS or CREATOR.")
        print("    Instagram API requires a Professional (Creator or Business) account to publish Reels.")
        print("    Please switch your account type in the Instagram mobile app settings.")

    # Write / Update .env
    if update_env:
        print("\n[3/3] Updating local .env file...")
        env_path = Path(".env")
        existing_lines = []
        if env_path.exists():
            existing_lines = env_path.read_text(encoding="utf-8").splitlines()

        keys_to_set = {
            "INSTAGRAM_USER_ID": user_id,
            "INSTAGRAM_ACCESS_TOKEN": long_lived_token,
        }

        updated_keys = set()
        new_lines = []
        for line in existing_lines:
            matched = False
            for k, v in keys_to_set.items():
                if line.startswith(f"{k}="):
                    new_lines.append(f"{k}={v}")
                    updated_keys.add(k)
                    matched = True
                    break
            if not matched:
                new_lines.append(line)

        for k, v in keys_to_set.items():
            if k not in updated_keys:
                new_lines.append(f"{k}={v}")

        env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print("[+] .env file updated successfully with INSTAGRAM_USER_ID and INSTAGRAM_ACCESS_TOKEN!")

    return {
        "user_id": user_id,
        "username": username,
        "long_lived_token": long_lived_token,
        "expires_in_days": expires_in_days,
    }

def main():
    parser = argparse.ArgumentParser(description="Exchange short-lived Meta token for a 60-day long-lived token")
    parser.add_argument("--token", help="Short-lived Meta user token")
    parser.add_argument("--secret", help="Meta App Secret")
    parser.add_argument("--no-env", action="store_true", help="Do not write to .env file")
    args = parser.parse_args()

    token = args.token or os.getenv("META_SHORT_LIVED_TOKEN")
    secret = args.secret or os.getenv("META_APP_SECRET")

    if not token:
        token = input("Enter Short-Lived User Access Token from Meta Graph Explorer: ").strip()
    if not secret:
        secret = input("Enter Meta App Secret (from App Dashboard -> App settings -> Basic): ").strip()

    if not token or not secret:
        print("[-] Both token and secret are required. Exiting.")
        sys.exit(1)

    exchange_token(token, secret, update_env=not args.no_env)

if __name__ == "__main__":
    main()
