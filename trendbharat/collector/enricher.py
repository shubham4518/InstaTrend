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

        # Clean source attribution from headline (e.g. " - NDTV News" or " | India Today")
        if news_title:
            clean_headline = re.sub(r"\s+[-|]\s+[^-|]+$", "", news_title).strip()
        else:
            clean_headline = f"Massive Search Spike in India for {query.title()}"

        # Extract meaningful statement (at least 3 words) or craft an impactful takeaway
        statement = ""
        quotes = re.findall(r"['\"‘“](.*?)['\"’”]", news_title)
        for q in quotes:
            if len(q.split()) >= 3:
                statement = f"“{q.strip()}”"
                break

        if not statement and news_snippet:
            snip_quotes = re.findall(r"['\"‘“](.*?)['\"’”]", news_snippet)
            for q in snip_quotes:
                if len(q.split()) >= 3:
                    statement = f"“{q.strip()}”"
                    break

        is_hindi = any("\u0900" <= c <= "\u097f" for c in f"{query} {clean_headline}")

        if not statement:
            if is_hindi:
                statement = f"“{clean_headline}”"
            else:
                statement = f"“Key Update: Massive surge across India with millions following {query.title()}”"

        # Provide complete factual background (who, what, why)
        if news_snippet and len(news_snippet.split()) > 6:
            context = news_snippet
        elif wiki_extract:
            sentences = wiki_extract.split(". ")
            context = ". ".join(sentences[:2]).strip()
            if not context.endswith("."):
                context += "."
        elif is_hindi:
            context = f"ताज़ा रिपोर्ट्स के अनुसार {query} को लेकर देश भर में भारी चर्चा देखी जा रही है।"
        else:
            context = f"Reports confirm significant national interest and discussions around {query} today."

        return {
            **trend_item,
            "hd_image_url": final_image,
            "headline": clean_headline,
            "statement": statement,
            "context": context,
        }
