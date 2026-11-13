"""Telegram notification & post delivery client.
Delivers ready-to-post high-definition JPEG images & captions directly to your phone.
"""

import html
import logging

import requests

logger = logging.getLogger(__name__)


class TelegramDeliveryBot:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token.strip() if bot_token else ""
        self.chat_id = str(chat_id).strip() if chat_id else ""
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_post_package(
        self,
        image_path: str,
        caption: str,
        topic_name: str,
        post_index: int = 1,
        total_posts: int = 1,
    ) -> bool:
        """
        Sends the 1080x1350 feed post image directly to your Telegram chat,
        followed by a 1-tap copyable caption message.
        """
        if not self.bot_token or not self.chat_id:
            logger.error(
                "Telegram bot token or chat ID is missing! "
                "(Check TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env or GitHub Secrets)"
            )
            return False

        # 1. Send High-Res Photo
        photo_url = f"{self.base_url}/sendPhoto"
        logger.info("Uploading post #%d/%d to Telegram chat %s...", post_index, total_posts, self.chat_id)

        try:
            safe_topic = html.escape(topic_name)
            count_label = (
                f"Post #{post_index} of {total_posts}" if total_posts > 1 else "Today's Top Trend"
            )
            with open(image_path, "rb") as f:
                files = {"photo": f}
                cap_text = (
                    f"🚀 <b>{count_label}:</b> <code>{safe_topic}</code>\n"
                    "📸 High-res 4:5 feed image ready to share!"
                )
                data = {
                    "chat_id": self.chat_id,
                    "caption": cap_text,
                    "parse_mode": "HTML",
                }
                resp = requests.post(photo_url, data=data, files=files, timeout=30)
                if resp.status_code != 200:
                    logger.error("Telegram photo upload failed (status %d): %s", resp.status_code, resp.text)
                resp.raise_for_status()

            # 2. Send 1-Tap Copyable Caption in Next Message
            msg_url = f"{self.base_url}/sendMessage"
            safe_caption = html.escape(caption)
            cap_header = (
                f"📋 <b>Instagram Caption #{post_index} (Tap & hold to copy):</b>"
                if total_posts > 1
                else "📋 <b>Instagram Caption (Tap & hold to copy):</b>"
            )
            cap_data = {
                "chat_id": self.chat_id,
                "text": f"{cap_header}\n\n{safe_caption}",
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            }
            c_resp = requests.post(msg_url, json=cap_data, timeout=15)
            if c_resp.status_code != 200:
                logger.error("Telegram caption send failed (status %d): %s", c_resp.status_code, c_resp.text)
            c_resp.raise_for_status()

            logger.info("Successfully delivered post #%d/%d package to Telegram!", post_index, total_posts)
            return True
        except requests.RequestException as e:
            logger.error("Failed to deliver post package to Telegram: %s", e)
            return False

    def send_failure_alert(self, stage: str, error_msg: str):
        if not self.bot_token or not self.chat_id:
            return
        msg_url = f"{self.base_url}/sendMessage"
        safe_stage = html.escape(stage)
        safe_err = html.escape(error_msg[:300])
        msg_text = (
            f"🚨 <b>TrendBharat Pipeline Alert!</b>\n\n"
            f"💥 <b>Failed Stage:</b> <code>{safe_stage}</code>\n"
            f"⚠️ <b>Error:</b> <code>{safe_err}</code>"
        )
        data = {
            "chat_id": self.chat_id,
            "text": msg_text,
            "parse_mode": "HTML",
        }
        try:
            requests.post(msg_url, json=data, timeout=10)
        except Exception:
            pass
