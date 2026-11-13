"""Main Orchestrator CLI for TrendBharat.
Collects top daily trends, generates viral 3-tier news card posts, and delivers directly to Telegram.
"""

import argparse
import datetime
import logging
import os
import sys
import time
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
    parser.add_argument("--dry-run", action="store_true", help="Render posts locally without sending to Telegram")
    parser.add_argument("--post-now", action="store_true", help="Deliver daily posts and captions to Telegram")
    parser.add_argument("--force-date", type=str, help="Override date in YYYY-MM-DD format")
    parser.add_argument("--count", type=int, default=3, help="Number of daily posts to generate and send (default: 3)")
    parser.add_argument("--force", action="store_true", help="Force run even if already completed today")
    args = parser.parse_args()

    load_dotenv()
    today_str = args.force_date or datetime.date.today().isoformat()
    logger.info("Executing TrendBharat daily pipeline for %s (Target: %d posts)...", today_str, args.count)

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

    # 1. Check if all required posts for today are already completed
    if not args.force and db.check_all_completed_today(today_str, required_count=args.count) and not args.dry_run:
        logger.info(
            "All %d posts for %s are already completed! (Use --force to run anyway). Exiting.",
            args.count,
            today_str,
        )
        sys.exit(0)

    try:
        # 2. Ingest & Enrich Top Trending Stories
        logger.info("[1/4] Collecting top %d trending stories from Google Trends...", args.count)
        config_dir = Path("trendbharat/config")
        collector = TrendsPipeline(config_dir)
        stories = collector.get_top_stories(limit=args.count)

        logger.info("Successfully fetched and enriched %d stories.", len(stories))

        out_dir = Path("temp/daily_posts")
        out_dir.mkdir(parents=True, exist_ok=True)
        builder = RVCJPostBuilder()

        # 3. Process Each Story
        delivered_count = 0
        for idx, story in enumerate(stories, start=1):
            logger.info(
                "--- Processing Post #%d of %d: %s (%s) ---",
                idx,
                len(stories),
                story["query"],
                story["category"],
            )
            logger.info("Headline: %s", story["headline"])
            logger.info("Statement: %s", story["statement"])

            image_path = str(out_dir / f"post_{today_str}_{idx}.jpg")
            builder.render(
                badge_text=story["badge"],
                headline=story["headline"],
                red_statement=story["statement"],
                context=story["context"],
                image_url=story.get("hd_image_url"),
                output_path=image_path,
                handle="@InstaTrend",
            )
            logger.info("Image #%d generated: %s", idx, image_path)

            caption = build_instagram_caption(story, handle="@InstaTrend")

            if args.dry_run:
                logger.info("[DRY RUN] Post #%d saved at %s", idx, image_path)
                print(f"\n=================== CAPTION #{idx} ===================\n{caption}\n")
                continue

            # Deliver Post Package to Telegram
            logger.info("Delivering Post #%d to Telegram...", idx)
            success = notifier.send_post_package(
                image_path=image_path,
                caption=caption,
                topic_name=story["query"].title(),
                post_index=idx,
                total_posts=len(stories),
            )
            if success:
                db.record_run(today_str, story, post_index=idx, status="completed")
                delivered_count += 1
                logger.info("Delivered post #%d to Telegram!", idx)
                if idx < len(stories):
                    time.sleep(2)  # Pause between Telegram messages to avoid rate limits
            else:
                logger.error("Failed to deliver post #%d to Telegram.", idx)

        if not args.dry_run:
            logger.info("Daily pipeline completed: %d/%d posts delivered to Telegram!", delivered_count, len(stories))

    except Exception as e:
        logger.exception("Pipeline crashed: %s", e)
        notifier.send_failure_alert("Daily Pipeline", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
