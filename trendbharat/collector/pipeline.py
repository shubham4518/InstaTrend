"""Unified collector pipeline: Ingests, filters, classifies, and enriches top trending stories."""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple

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

    def get_top_stories(self, limit: int = 3) -> List[Dict]:
        """Pulls live trends, filters unsafe items, and enriches top distinct stories."""
        raw_xml = self.feed_reader.fetch_raw_feed()
        items = self.feed_reader.parse_feed(raw_xml)

        valid_items = []
        seen_queries = set()

        for it in items:
            q_norm = it["query"].strip().lower()
            if q_norm in seen_queries:
                continue

            blocked, reason = self.is_blocked(f"{it['query']} {it['news_title']}")
            if not blocked:
                cat_name, badge, hashtags = self.categorize(it["query"], it["news_title"])
                it["category"] = cat_name
                it["badge"] = badge
                it["hashtags"] = hashtags
                valid_items.append(it)
                seen_queries.add(q_norm)
            else:
                logger.warning("Filtered unsafe topic '%s': %s", it["query"], reason)

        if not valid_items:
            raise RuntimeError("No valid trending stories found after safety filtering.")

        # Pick the top distinct stories up to the limit
        selected = valid_items[:limit]
        enriched_stories = []

        for idx, item in enumerate(selected, start=1):
            enriched = self.enricher.enrich_trend(item)
            enriched["post_index"] = idx
            logger.info("Enriched story #%d: %s (%s)", idx, enriched["query"], enriched["category"])
            enriched_stories.append(enriched)

        return enriched_stories

    def get_top_story(self) -> Dict:
        """Backward compatibility: returns top 1 story."""
        return self.get_top_stories(limit=1)[0]
