"""Module to enrich trending topics with high-definition portraits and context."""

import logging
import re
from typing import Dict, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary"
USER_AGENT = "TrendBharatBot/2.0 (High-Resolution News Pipeline; contact: bot@trendbharat.internal)"


class EntityEnricher:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def fetch_wikipedia_portrait(self, entity_name: str) -> Tuple[Optional[str], Optional[str]]:
        """Query Wikipedia REST API for official high-res portrait and summary extract."""
        clean_name = entity_name.strip().replace(" ", "_")
        url = f"{WIKIPEDIA_API_URL}/{clean_name}"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                img_url = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
                extract = data.get("extract", "")
                return img_url, extract
        except requests.RequestException as e:
            logger.warning("Could not fetch Wikipedia data for '%s': %s", entity_name, e)
        return None, None

    def enrich_trend(self, trend_item: Dict) -> Dict:
        """
        Enriches a raw trend with:
        1. High-definition subject image
        2. Cleaned headline & viral red statement
        3. Clear context story
        """
        query = trend_item["query"]
        news_title = trend_item.get("news_title", "")
        news_snippet = trend_item.get("news_snippet", "")
        fallback_pic = trend_item.get("picture_url", "")

        # Try Wikipedia lookup for prominent names in query
        hd_image = None
        wiki_extract = None

        # Clean query for entity lookup (e.g. "jailer movie rajinikanth" -> "Rajinikanth")
        tokens = re.findall(r"[A-Za-z]+", query)
        for token_len in (3, 2, 1):
            if len(tokens) >= token_len:
                candidate = " ".join(tokens[:token_len])
                img, extract = self.fetch_wikipedia_portrait(candidate)
                if img:
                    hd_image = img
                    wiki_extract = extract
                    break

        final_image = hd_image or fallback_pic

        # Build punchy headline & statement
        if news_title:
            headline = news_title
        else:
            headline = f"Massive Search Spike in India for {query.title()}"

        # Extract statement if quotes exist, else formulate strong hook
        quotes = re.findall(r"['\"‘“](.*?)['\"’”]", news_title)
        if quotes:
            statement = f"“{quotes[0]}”"
        else:
            statement = f"“High volume surge: Millions of Indian netizens search for updates on {query.title()}”"

        context = (
            news_snippet
            or wiki_extract
            or f"Trending searches across India reflect massive public curiosity on {query}."
        )

        return {
            **trend_item,
            "hd_image_url": final_image,
            "headline": headline,
            "statement": statement,
            "context": context,
        }
