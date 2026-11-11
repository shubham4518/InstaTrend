"""Unified collector pipeline: Ingests, filters, classifies, and enriches top trending stories."""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Tuple

from trendbharat.collector.enricher import EntityEnricher
from trendbharat.collector.feed_reader import FeedReader

logger = logging.getLogger(__name__)


class TrendsPipeline:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.feed_reader = FeedReader()
        self.enricher = EntityEnricher()
        self.categories = self._load_json(config_dir / "categories.json")
        self.blocklist = self._load_json(config_dir / "blocklist.json").get("blocked_terms", [])

    def _load_json(self, path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def is_blocked(self, text: str) -> Tuple[bool, str]:
        normalized = text.lower()
        for term in self.blocklist:
            if re.search(r"\b" + re.escape(term) + r"\b", normalized):
                return True, term
        return False, ""

    def categorize(self, query: str, context: str) -> Tuple[str, str, str]:
        content = f"{query} {context}".lower()
        for cat_name, data in self.categories.items():
            if cat_name == "General":
                continue
            for kw in data["keywords"]:
                if kw in content:
                    return cat_name, data["badge"], data["hashtag"]
        general = self.categories["General"]
        return "General", general["badge"], general["hashtag"]

    def get_top_story(self) -> Dict:
        """Pulls live trends, filters unsafe items, and enriches the #1 top story."""
        raw_xml = self.feed_reader.fetch_raw_feed()
        items = self.feed_reader.parse_feed(raw_xml)

        valid_items = []
        for it in items:
            blocked, reason = self.is_blocked(f"{it['query']} {it['news_title']}")
            if not blocked:
                cat_name, badge, hashtags = self.categorize(it["query"], it["news_title"])
                it["category"] = cat_name
                it["badge"] = badge
                it["hashtags"] = hashtags
                valid_items.append(it)
            else:
                logger.warning("Filtered unsafe topic '%s': %s", it["query"], reason)

        if not valid_items:
            raise RuntimeError("No valid trending stories found after safety filtering.")

        # Pick the top story and enrich it with HD image & context
        top_item = valid_items[0]
        enriched = self.enricher.enrich_trend(top_item)
        logger.info("Successfully selected & enriched top story: %s", enriched["query"])
        return enriched
