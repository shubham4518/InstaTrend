"""Main Orchestrator CLI for TrendBharat.
Collects top daily trend, generates viral RVCJ-style post, and delivers directly to Telegram.
"""

import argparse
import datetime
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from trendbharat.alerts.telegram_notifier import TelegramDeliveryBot
from trendbharat.collector.pipeline import TrendsPipeline
from trendbharat.db.manager import DatabaseManager
from trendbharat.render.caption_builder import build_instagram_caption
from trendbharat.render.post_builder import RVCJPostBuilder

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("trendbharat.runner")


def main():
    parser = argparse.ArgumentParser(description="TrendBharat Daily Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Render post locally without sending to Telegram")
    parser.add_argument("--post-now", action="store_true", help="Deliver today's post and caption to Telegram")
    parser.add_argument("--force-date", type=str, help="Override date in YYYY-MM-DD format")
    args = parser.parse_args()

    load_dotenv()
    today_str = args.force_date or datetime.date.today().isoformat()
    logger.info("Executing TrendBharat daily pipeline for %s...", today_str)

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    db_path = os.getenv("DATABASE_PATH", "trendbharat.db")

    if not args.dry_run:
        if not bot_token or not chat_id:
            logger.error(
                "\n=======================================================\n"
                "CRITICAL ERROR: Telegram credentials are not configured!\n"
                "- TELEGRAM_BOT_TOKEN: %s\n"
                "- TELEGRAM_CHAT_ID: %s\n\n"
                "If running on GitHub Actions:\n"
                "1. Go to repository Settings -> Secrets and variables -> Actions\n"
                "2. Click 'New repository secret'\n"
                "3. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID\n"
                "=======================================================",
                "Configured" if bot_token else "MISSING",
                "Configured" if chat_id else "MISSING",
            )
            sys.exit(1)

    db = DatabaseManager(db_path)
    notifier = TelegramDeliveryBot(bot_token, chat_id)

    # 1. Idempotency Check
    if db.check_already_run_today(today_str) and not args.dry_run:
        logger.info("Today's run for %s already completed! Exiting.", today_str)
        sys.exit(0)

    try:
        # 2. Ingest & Enrich Top Trending Story
        logger.info("[1/4] Collecting & enriching top trending story from Google...")
        config_dir = Path("trendbharat/config")
        collector = TrendsPipeline(config_dir)
        story = collector.get_top_story()

        logger.info("Top Story: %s (%s)", story["query"], story["category"])
        logger.info("Headline: %s", story["headline"])
        logger.info("Statement: %s", story["statement"])

        # 3. Render RVCJ Style Post (1080x1350 4:5 portrait)
        logger.info("[2/4] Rendering viral RVCJ-style white theme feed post...")
        out_dir = Path("temp/daily_posts")
        out_dir.mkdir(parents=True, exist_ok=True)
        image_path = str(out_dir / f"post_{today_str}.jpg")

        builder = RVCJPostBuilder()
        builder.render(
            badge_text=story["badge"],
            headline=story["headline"],
            red_statement=story["statement"],
            context=story["context"],
            image_url=story.get("hd_image_url"),
            output_path=image_path,
            handle="@InstaTrend",
        )
        logger.info("Image successfully generated: %s", image_path)

        # 4. Generate Instagram Caption
        logger.info("[3/4] Generating viral Instagram caption...")
        caption = build_instagram_caption(story, handle="@InstaTrend")

        # 5. Delivery & State Tracking
        if args.dry_run:
            logger.info("[DRY RUN COMPLETE] Post saved at %s", image_path)
            print(f"\n--- GENERATED CAPTION ---\n{caption}\n")
            sys.exit(0)

        logger.info("[4/4] Delivering post package to Telegram...")
        success = notifier.send_post_package(image_path, caption, story["query"].title())
        if success:
            db.record_run(today_str, story, status="completed")
            logger.info("Pipeline completed successfully for %s!", today_str)
        else:
            raise RuntimeError("Failed to deliver post package to Telegram.")

    except Exception as e:
        logger.exception("Pipeline crashed: %s", e)
        notifier.send_failure_alert("Daily Pipeline", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
