"""Builds high-reach Instagram captions with viral hooks and trending hashtags."""

from typing import Dict


def build_instagram_caption(story: Dict, handle: str = "@InstaTrend") -> str:
    statement = story.get("statement", "").strip("“”\"'")
    context = story.get("context", "")
    hashtags = story.get("hashtags", "#trending #india #viral #news")
    query = story.get("query", "").title()

    caption = f"""🚨 {statement}

{context}

What are your thoughts on this? Tell us in the comments! 👇

Follow {handle} for daily trending stories and viral updates from across India.

#InstaTrend #IndiaTrending #{query.replace(" ", "")} {hashtags}
"""
    return caption.strip()
