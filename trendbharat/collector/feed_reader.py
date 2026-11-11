"""Module to fetch and parse India trending searches from Google Trends RSS."""

import html
import logging
import time
import xml.etree.ElementTree as ET
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)

FEED_URL = "https://trends.google.com/trending/rss?geo=IN"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class FeedReader:
    def __init__(self, feed_url: str = FEED_URL, timeout: int = 15):
        self.feed_url = feed_url
        self.timeout = timeout

    def fetch_raw_feed(self, max_retries: int = 3, backoff_factor: float = 2.0) -> str:
        headers = {"User-Agent": USER_AGENT}
        for attempt in range(1, max_retries + 1):
            try:
                logger.info("Fetching Google Trends RSS feed (Attempt %d/%d)...", attempt, max_retries)
                response = requests.get(self.feed_url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except (requests.RequestException, requests.Timeout) as e:
                logger.warning("Attempt %d failed: %s", attempt, str(e))
                if attempt == max_retries:
                    raise RuntimeError(f"Failed to fetch Google Trends after {max_retries} attempts") from e
                time.sleep(backoff_factor * attempt)
        return ""

    def parse_feed(self, xml_content: str) -> List[Dict]:
        root = ET.fromstring(xml_content)
        channel = root.find("channel")
        if channel is None:
            return []

        ns = {"ht": "https://trends.google.com/trending/rss"}
        items = []

        for rank, item in enumerate(channel.findall("item"), start=1):
            title = html.unescape(item.findtext("title", default="").strip())
            traffic_node = item.find("ht:approx_traffic", ns)
            traffic_str = traffic_node.text.strip() if traffic_node is not None and traffic_node.text else "1,000+"
            clean_traffic = int(traffic_str.replace("+", "").replace(",", "") or 1000)

            pub_date = item.findtext("pubDate", default="").strip()
            picture_url = item.findtext("ht:picture", default="", namespaces=ns).strip()

            # Parse primary news item if available
            news_title = ""
            news_snippet = ""
            news_el = item.find("ht:news_item", ns)
            if news_el is not None:
                news_title = html.unescape(news_el.findtext("ht:news_item_title", default="", namespaces=ns).strip())
                news_snippet = html.unescape(
                    news_el.findtext("ht:news_item_snippet", default="", namespaces=ns).strip()
                )
                if not picture_url:
                    picture_url = news_el.findtext("ht:news_item_picture", default="", namespaces=ns).strip()

            items.append(
                {
                    "feed_rank": rank,
                    "query": title,
                    "approx_volume": clean_traffic,
                    "volume_display": traffic_str,
                    "news_title": news_title,
                    "news_snippet": news_snippet,
                    "picture_url": picture_url,
                    "pub_date": pub_date,
                }
            )

        logger.info("Extracted %d items from RSS feed", len(items))
        return items
