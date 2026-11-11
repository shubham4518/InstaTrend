"""Telegram notification & post delivery client.
Delivers ready-to-post high-definition JPEG images & captions directly to your phone.
"""

import logging

import requests

logger = logging.getLogger(__name__)


class TelegramDeliveryBot:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_post_package(self, image_path: str, caption: str, topic_name: str) -> bool:
        """
        Sends the 1080x1350 feed post image directly to your Telegram chat,
        followed by a 1-tap copyable caption message!
        """
        if not self.bot_token or not self.chat_id:
            logger.error("Telegram bot token or chat ID is missing!")
            return False

        # 1. Send High-Res Photo
        photo_url = f"{self.base_url}/sendPhoto"
        logger.info("Uploading post image to Telegram chat %s...", self.chat_id)

        try:
            with open(image_path, "rb") as f:
                files = {"photo": f}
                data = {
                    "chat_id": self.chat_id,
                    "caption": f"🚀 *Today's Top Trend:* `{topic_name}`\n📸 High-res 4:5 feed image ready to share!",
                    "parse_mode": "Markdown",
                }
                resp = requests.post(photo_url, data=data, files=files, timeout=30)
                resp.raise_for_status()

            # 2. Send 1-Tap Copyable Caption in Next Message
            msg_url = f"{self.base_url}/sendMessage"
            cap_data = {
                "chat_id": self.chat_id,
                "text": f"📋 *Instagram Caption (Tap & hold to copy):*\n\n{caption}",
                "disable_web_page_preview": True,
            }
            c_resp = requests.post(msg_url, json=cap_data, timeout=15)
            c_resp.raise_for_status()

            logger.info("Successfully delivered post package to Telegram!")
            return True
        except requests.RequestException as e:
            logger.error("Failed to deliver post package to Telegram: %s", e)
            return False

    def send_failure_alert(self, stage: str, error_msg: str):
        msg_url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": f"🚨 *TrendBharat Pipeline Alert!*\n\n💥 *Failed Stage:* `{stage}`\n⚠️ *Error:* `{error_msg[:300]}`",
            "parse_mode": "Markdown",
        }
        try:
            requests.post(msg_url, json=data, timeout=10)
        except Exception:
            pass
