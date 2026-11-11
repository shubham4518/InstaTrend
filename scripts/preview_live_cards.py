"""Live Trends Ingestion & Visual Card Generator Preview.

Fetches live Google Trends India RSS, sanitizes and categorizes queries,
and renders pixel-perfect 1080x1920 vertical cards for Instagram Reels.
"""

import html
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import requests
from PIL import Image, ImageDraw, ImageFont

CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1920

# Safe zones for Instagram Reels UI chrome
MARGIN_LEFT = 80
MARGIN_RIGHT = 80
MARGIN_TOP = 240
MARGIN_BOTTOM = 400

FONT_DIR = Path("trendbharat/assets/fonts")
OUTPUT_DIR = Path("temp/cards")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Category Taxonomies & Color Palettes
CATEGORY_THEMES = {
    "Sports": {
        "border": (16, 185, 129),  # Emerald
        "bg": (6, 78, 59),
        "text": (110, 231, 183),
        "label": "CRICKET & SPORTS",
        "keywords": [
            "cricket",
            "ipl",
            "bcci",
            "match",
            "score",
            "vs",
            "cup",
            "tournament",
            "football",
            "messi",
            "ronaldo",
            "badminton",
            "kohli",
            "rohit",
            "dhoni",
            "श्रीलंका",
            "पाकिस्तान",
            "बनाम",
        ],
    },
    "Entertainment": {
        "border": (139, 92, 246),  # Purple / Violet
        "bg": (76, 29, 149),
        "text": (221, 214, 254),
        "label": "CINEMA & OTT",
        "keywords": [
            "movie",
            "trailer",
            "actor",
            "actress",
            "release date",
            "review",
            "song",
            "teaser",
            "ott",
            "netflix",
            "box office",
            "cinema",
            "jailer",
            "rajinikanth",
            "kantara",
            "pushpa",
            "bollywood",
        ],
    },
    "Technology": {
        "border": (6, 182, 212),  # Cyan
        "bg": (22, 78, 99),
        "text": (165, 243, 252),
        "label": "TECH & AI",
        "keywords": [
            "ai",
            "chatgpt",
            "gemini",
            "deepseek",
            "google",
            "apple",
            "iphone",
            "cloud",
            "update",
            "launch",
            "app",
            "feature",
            "nvidia",
            "meta",
            "software",
        ],
    },
    "Business": {
        "border": (245, 158, 11),  # Gold / Amber
        "bg": (120, 53, 15),
        "text": (253, 230, 138),
        "label": "BUSINESS & MARKETS",
        "keywords": [
            "share price",
            "stock",
            "sensex",
            "nifty",
            "gold rate",
            "silver",
            "ipo",
            "crypto",
            "bitcoin",
            "market",
            "rbi",
            "budget",
            "gdp",
            "yusuff ali",
            "bank",
        ],
    },
    "Education": {
        "border": (59, 130, 246),  # Electric Blue
        "bg": (30, 58, 138),
        "text": (191, 219, 254),
        "label": "JOBS & EXAMS",
        "keywords": [
            "upsc",
            "ssc",
            "admit card",
            "result",
            "exam",
            "answer key",
            "syllabus",
            "kseab",
            "neet",
            "jee",
            "cbse",
            "government",
        ],
    },
    "General": {
        "border": (100, 116, 139),  # Slate
        "bg": (30, 41, 59),
        "text": (203, 213, 225),
        "label": "INDIA TRENDING",
        "keywords": [],
    },
}


class LiveCardRenderer:
    def __init__(self):
        self.font_latin_bold = str(FONT_DIR / "NotoSans-Bold.ttf")
        self.font_latin_reg = str(FONT_DIR / "NotoSans-Regular.ttf")
        self.font_devanagari = str(FONT_DIR / "NotoSansDevanagari-Bold.ttf")
        self.font_telugu = str(FONT_DIR / "NotoSansTelugu-Bold.ttf")
        self.font_tamil = str(FONT_DIR / "NotoSansTamil-Bold.ttf")

    def _resolve_font(self, text: str, size: int) -> ImageFont.FreeTypeFont:
        """Select font family matching script Unicode blocks."""
        # Devanagari (Hindi, Marathi)
        if any("\u0900" <= c <= "\u097f" for c in text):
            if os.path.exists(self.font_devanagari):
                return ImageFont.truetype(self.font_devanagari, size)
        # Telugu
        if any("\u0c00" <= c <= "\u0c7f" for c in text):
            if os.path.exists(self.font_telugu):
                return ImageFont.truetype(self.font_telugu, size)
        # Tamil
        if any("\u0b80" <= c <= "\u0bff" for c in text):
            if os.path.exists(self.font_tamil):
                return ImageFont.truetype(self.font_tamil, size)

        # Fallback to Latin
        return ImageFont.truetype(self.font_latin_bold, size)

    def _create_background(self) -> Image.Image:
        """Generate high-end luxury dark gradient with ambient glow."""
        base = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), (10, 14, 23, 255))
        draw = ImageDraw.Draw(base)

        # Vertical subtle gradient
        for y in range(CANVAS_HEIGHT):
            ratio = y / CANVAS_HEIGHT
            r = int(10 + ratio * 8)  # 10 -> 18
            g = int(14 + ratio * 10)  # 14 -> 24
            b = int(23 + ratio * 16)  # 23 -> 39
            draw.line([(0, y), (CANVAS_WIDTH, y)], fill=(r, g, b, 255))

        # Ambient radial glow behind card center
        glow = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        center_x = CANVAS_WIDTH // 2
        center_y = CANVAS_HEIGHT // 2 - 100
        max_radius = 550

        for radius in range(max_radius, 0, -25):
            alpha = int((1.0 - (radius / max_radius)) * 26)  # Subtle 10% opacity glow
            glow_draw.ellipse(
                [(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)],
                fill=(30, 58, 138, alpha),
            )

        return Image.alpha_composite(base, glow).convert("RGB")

    def render_cover(self, date_str: str, top_trends: List[str], output_path: str):
        """Render high-impact cover card."""
        img = self._create_background()
        draw = ImageDraw.Draw(img)

        # Card container plate
        plate_box = [(MARGIN_LEFT, MARGIN_TOP), (CANVAS_WIDTH - MARGIN_RIGHT, CANVAS_HEIGHT - MARGIN_BOTTOM)]
        draw.rounded_rectangle(plate_box, radius=40, fill=(15, 23, 42), outline=(36, 51, 77), width=3)

        # Subtle Header Pill
        f_pill = ImageFont.truetype(self.font_latin_bold, 28)
        draw.rounded_rectangle(
            [(MARGIN_LEFT + 60, MARGIN_TOP + 60), (MARGIN_LEFT + 380, MARGIN_TOP + 120)],
            radius=20,
            fill=(30, 41, 59),
            outline=(51, 65, 85),
            width=2,
        )
        draw.text((MARGIN_LEFT + 85, MARGIN_TOP + 74), "🔴 INDIA DAILY PULSE", font=f_pill, fill=(244, 63, 94))

        # Main Big Hook
        f_hero = ImageFont.truetype(self.font_latin_bold, 84)
        draw.text(
            (MARGIN_LEFT + 60, MARGIN_TOP + 170),
            "WHAT INDIA\nSEARCHED\nTODAY",
            font=f_hero,
            fill=(255, 255, 255),
            spacing=18,
        )

        # Amber Accent Line
        draw.rounded_rectangle(
            [(MARGIN_LEFT + 60, MARGIN_TOP + 490), (MARGIN_LEFT + 220, MARGIN_TOP + 500)], radius=5, fill=(245, 158, 11)
        )

        # Date Badge
        f_date = ImageFont.truetype(self.font_latin_reg, 38)
        draw.text((MARGIN_LEFT + 60, MARGIN_TOP + 530), f"📅 {date_str}", font=f_date, fill=(148, 163, 184))

        # Teaser Checklist of top 3
        f_teaser_hdr = ImageFont.truetype(self.font_latin_bold, 34)
        draw.text(
            (MARGIN_LEFT + 60, MARGIN_TOP + 620), "TODAY'S TOP COUNTDOWN:", font=f_teaser_hdr, fill=(203, 213, 225)
        )

        start_y = MARGIN_TOP + 680
        for i, t in enumerate(top_trends[:3], 1):
            query_preview = (t[:32] + "...") if len(t) > 35 else t
            draw.text(
                (MARGIN_LEFT + 70, start_y + (i - 1) * 60),
                f"#{i:02d}  {query_preview}",
                font=self._resolve_font(query_preview, 32),
                fill=(241, 245, 249),
            )

        # Bottom Call to Action inside card
        f_cta = ImageFont.truetype(self.font_latin_bold, 32)
        draw.text(
            (MARGIN_LEFT + 60, CANVAS_HEIGHT - MARGIN_BOTTOM - 100),
            "Countdown from #09 to #01  👉",
            font=f_cta,
            fill=(245, 158, 11),
        )

        # Footer
        self._render_footer(draw)
        img.save(output_path, "PNG", quality=95)
        print(f"[+] Rendered Cover Card: {output_path}")

    def render_trend(self, rank: int, query: str, category: str, volume: str, date_str: str, output_path: str):
        """Render individual trend countdown card."""
        img = self._create_background()
        draw = ImageDraw.Draw(img)

        # Card container plate
        plate_box = [(MARGIN_LEFT, MARGIN_TOP), (CANVAS_WIDTH - MARGIN_RIGHT, CANVAS_HEIGHT - MARGIN_BOTTOM)]
        draw.rounded_rectangle(plate_box, radius=40, fill=(15, 23, 42), outline=(36, 51, 77), width=3)

        # Top Bar inside plate: Giant Rank + Category Pill
        # Rank Counter (e.g. #01)
        f_rank = ImageFont.truetype(self.font_latin_bold, 120)
        draw.text((MARGIN_LEFT + 60, MARGIN_TOP + 50), f"#{rank:02d}", font=f_rank, fill=(245, 158, 11))

        # Category Theme Pill
        theme = CATEGORY_THEMES.get(category, CATEGORY_THEMES["General"])
        f_cat = ImageFont.truetype(self.font_latin_bold, 28)
        cat_label = theme["label"]

        # Measure text width for pill
        cat_bbox = f_cat.getbbox(cat_label)
        cat_w = cat_bbox[2] - cat_bbox[0]
        pill_x1 = CANVAS_WIDTH - MARGIN_RIGHT - 60 - (cat_w + 40)
        pill_y1 = MARGIN_TOP + 80
        pill_x2 = CANVAS_WIDTH - MARGIN_RIGHT - 60
        pill_y2 = pill_y1 + 54

        draw.rounded_rectangle(
            [(pill_x1, pill_y1), (pill_x2, pill_y2)], radius=18, fill=theme["bg"], outline=theme["border"], width=2
        )
        draw.text((pill_x1 + 20, pill_y1 + 12), cat_label, font=f_cat, fill=theme["text"])

        # Thin divider rule inside card
        draw.line(
            [(MARGIN_LEFT + 60, MARGIN_TOP + 200), (CANVAS_WIDTH - MARGIN_RIGHT - 60, MARGIN_TOP + 200)],
            fill=(36, 51, 77),
            width=2,
        )

        # Search Query (Dynamic Auto-Fitting)
        # Choose font based on language
        font_size = 64 if len(query) < 26 else (50 if len(query) < 45 else 40)
        f_query = self._resolve_font(query, font_size)

        # Wrap text nicely if needed
        wrapped_lines = self._wrap_text(query, f_query, max_width=(CANVAS_WIDTH - MARGIN_LEFT - MARGIN_RIGHT - 140))
        query_y = MARGIN_TOP + 260
        line_height = int(font_size * 1.35)

        for line in wrapped_lines[:3]:  # max 3 lines
            draw.text((MARGIN_LEFT + 60, query_y), line, font=f_query, fill=(255, 255, 255))
            query_y += line_height

        # Search Volume Badge Pill
        vol_text = volume if volume and volume != "0" else "1,000+"
        f_vol = ImageFont.truetype(self.font_latin_bold, 34)
        vol_label = f"🔥  {vol_text} searches today"
        vol_y = query_y + 40

        draw.rounded_rectangle(
            [(MARGIN_LEFT + 60, vol_y), (MARGIN_LEFT + 60 + 520, vol_y + 64)],
            radius=20,
            fill=(30, 41, 59),
            outline=(51, 65, 85),
            width=2,
        )
        draw.text((MARGIN_LEFT + 90, vol_y + 14), vol_label, font=f_vol, fill=(251, 191, 36))

        # Bottom inside card: Date & Status
        f_meta = ImageFont.truetype(self.font_latin_reg, 30)
        draw.text(
            (MARGIN_LEFT + 60, CANVAS_HEIGHT - MARGIN_BOTTOM - 90),
            f"India Search Pulse · {date_str}",
            font=f_meta,
            fill=(148, 163, 184),
        )

        # Footer
        self._render_footer(draw)
        img.save(output_path, "PNG", quality=95)
        print(f"[+] Rendered Trend #{rank:02d} Card: {output_path}")

    def _render_footer(self, draw: ImageDraw.Draw):
        """Draw persistent branding footer in safe zone."""
        f_foot = ImageFont.truetype(self.font_latin_reg, 28)
        foot_y = CANVAS_HEIGHT - 210
        draw.line([(MARGIN_LEFT, foot_y - 25), (CANVAS_WIDTH - MARGIN_RIGHT, foot_y - 25)], fill=(36, 51, 77), width=2)
        draw.text(
            (MARGIN_LEFT, foot_y),
            "@TrendBharat",
            font=ImageFont.truetype(self.font_latin_bold, 30),
            fill=(245, 158, 11),
        )
        draw.text(
            (CANVAS_WIDTH - MARGIN_RIGHT - 360, foot_y),
            "Source: Google Trends India",
            font=f_foot,
            fill=(148, 163, 184),
        )

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        words = text.split()
        if not words:
            return [text]
        lines = []
        current = words[0]
        for w in words[1:]:
            test = current + " " + w
            bbox = font.getbbox(test)
            if (bbox[2] - bbox[0]) <= max_width:
                current = test
            else:
                lines.append(current)
                current = w
        lines.append(current)
        return lines


def categorize_query(query: str, desc: str) -> str:
    content = f"{query} {desc}".lower()
    for cat, theme in CATEGORY_THEMES.items():
        if cat == "General":
            continue
        for kw in theme["keywords"]:
            if kw in content:
                return cat
    return "General"


def fetch_live_trends() -> List[Dict]:
    url = "https://trends.google.com/trending/rss?geo=IN"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()

    root = ET.fromstring(r.text)
    channel = root.find("channel")
    ns = {"ht": "https://trends.google.com/trending/rss"}

    items = []
    for item in channel.findall("item"):
        title = html.unescape(item.findtext("title", default="").strip())
        desc = html.unescape(item.findtext("description", default="").strip())
        traffic = item.findtext("ht:approx_traffic", default="1000+", namespaces=ns).strip()
        category = categorize_query(title, desc)
        items.append({"query": title, "description": desc, "volume": traffic, "category": category})
    return items


def main():
    print("Fetching live India Google Trends...")
    trends = fetch_live_trends()
    print(f"Retrieved {len(trends)} trending searches.\n")

    renderer = LiveCardRenderer()
    date_str = datetime.now().strftime("%B %d, %Y")

    # Render Cover Card
    cover_path = str(OUTPUT_DIR / "preview_00_cover.png")
    top_3_queries = [t["query"] for t in trends[:3]]
    renderer.render_cover(date_str, top_3_queries, cover_path)

    # Render Top 3 Trend Countdown Cards
    # In countdown format: Rank 3, Rank 2, Rank 1
    selected_samples = trends[:3]
    for rank, t in enumerate(selected_samples, 1):
        out_file = str(OUTPUT_DIR / f"preview_0{rank}_trend.png")
        renderer.render_trend(
            rank=rank,
            query=t["query"],
            category=t["category"],
            volume=t["volume"],
            date_str=date_str,
            output_path=out_file,
        )

    print("\nPreview cards generated successfully in:", OUTPUT_DIR.resolve())


if __name__ == "__main__":
    main()
