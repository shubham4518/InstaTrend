"""Utility script to verify Telegram bot credentials and send a test alert.

Usage:
    python scripts/test_telegram.py
    python scripts/test_telegram.py --token <BOT_TOKEN> --chat-id <CHAT_ID>
"""
import argparse
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

def test_telegram(bot_token: str, chat_id: str, update_env: bool = True) -> bool:
    """Verify Telegram bot token and dispatch a test markdown message."""
    print("\n[1/2] Verifying Telegram Bot token...")
    me_url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        resp = requests.get(me_url, timeout=15)
        me_data = resp.json()
    except requests.RequestException as e:
        print(f"[-] Network error connecting to Telegram: {e}")
        return False

    if not me_data.get("ok"):
        print(f"[-] Invalid bot token: {me_data.get('description', 'Unknown error')}")
        print("    Tip: Double-check the token copied from @BotFather.")
        return False

    bot_info = me_data["result"]
    print(f"[+] Bot Verified: @{bot_info.get('username')} ({bot_info.get('first_name')})")

    # Send test message
    print("\n[2/2] Sending test alert to Telegram Chat ID...")
    msg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": (
            "🔔 *TrendBharat Notification Test*\n\n"
            "Your Telegram alert channel is successfully connected!\n"
            "You will receive daily execution summaries and failure alerts here.\n\n"
            "🚀 *Status:* Online & Operational"
        ),
        "parse_mode": "Markdown",
    }

    try:
        send_resp = requests.post(msg_url, json=payload, timeout=15)
        send_data = send_resp.json()
    except requests.RequestException as e:
        print(f"[-] Network error sending message: {e}")
        return False

    if not send_data.get("ok"):
        print(f"[-] Failed to deliver message: {send_data.get('description', 'Unknown error')}")
        print("    Tips:")
        print("    1. Ensure you have sent at least one message (or clicked 'Start') to your bot on Telegram.")
        print("    2. Verify that your Chat ID is correct (numeric ID, e.g. 123456789).")
        return False

    print("[+] Test alert delivered successfully to your Telegram client!")

    # Write / Update .env
    if update_env:
        env_path = Path(".env")
        existing_lines = []
        if env_path.exists():
            existing_lines = env_path.read_text(encoding="utf-8").splitlines()

        keys_to_set = {
            "TELEGRAM_BOT_TOKEN": bot_token,
            "TELEGRAM_CHAT_ID": chat_id,
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
        print("[+] .env file updated successfully with TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID!")

    return True

def main():
    parser = argparse.ArgumentParser(description="Test Telegram alert bot credentials")
    parser.add_argument("--token", help="Telegram Bot Token from @BotFather")
    parser.add_argument("--chat-id", help="Telegram Chat ID")
    parser.add_argument("--no-env", action="store_true", help="Do not write to .env file")
    args = parser.parse_args()

    token = args.token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = args.chat_id or os.getenv("TELEGRAM_CHAT_ID")

    if not token:
        token = input("Enter Telegram Bot Token from @BotFather: ").strip()
    if not chat_id:
        chat_id = input("Enter your Telegram Chat ID: ").strip()

    if not token or not chat_id:
        print("[-] Both token and chat_id are required. Exiting.")
        sys.exit(1)

    success = test_telegram(token, chat_id, update_env=not args.no_env)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
