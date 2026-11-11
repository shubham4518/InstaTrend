# TrendBharat: Step-by-Step Implementation Guide
**Complete Hands-On Engineering Guide: From Zero to Automated Daily Instagram Reels**
*Document Version: 1.0.0 · Target Stack: Python 3.12, Pillow, FFmpeg, SQLite, Meta Graph API, GitHub Actions*

---

## Guide Overview

This guide walks you through building **TrendBharat** step-by-step from scratch. Each step includes:
1. **Goal & Prerequisites**
2. **Terminal commands** to set up directories and files
3. **Complete, copy-pasteable code implementations**
4. **Verification commands** to test that step before moving on

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                IMPLEMENTATION WORKFLOW                                 │
└────────────────────────────────────────────────────────────────────────────────────────┘
 [Step 1: Scaffolding] ──> [Step 2: Credentials] ──> [Step 3: Collector & Filter]
                                                              │
                                                              ▼
 [Step 6: Meta Publisher] <── [Step 5: Visual & Video] <── [Step 4: Database Layer]
            │
            ▼
 [Step 7: Orchestrator CLI & Alerts] ──> [Step 8: CI/CD Automation] ──> [Step 9: Live Launch]
```

---

## Step 1: Project Scaffolding & Virtual Environment

### 1.1 Create the Directory Tree
Open PowerShell in `D:\Workspace\Instaposts` and execute:

```powershell
# Create core module directories
New-Item -ItemType Directory -Force -Path `
  "trendbharat/collector", `
  "trendbharat/render", `
  "trendbharat/publisher", `
  "trendbharat/scheduler", `
  "trendbharat/db", `
  "trendbharat/config", `
  "trendbharat/assets/fonts", `
  "trendbharat/assets/audio", `
  "trendbharat/alerts", `
  "scripts", `
  "tests", `
  ".github/workflows", `
  "temp/cards", `
  "temp/output"

# Create Python package init files
New-Item -ItemType File -Force -Path `
  "trendbharat/__init__.py", `
  "trendbharat/collector/__init__.py", `
  "trendbharat/render/__init__.py", `
  "trendbharat/publisher/__init__.py", `
  "trendbharat/scheduler/__init__.py", `
  "trendbharat/db/__init__.py", `
  "trendbharat/alerts/__init__.py", `
  "tests/__init__.py"
```

### 1.2 Setup Dependencies & Tooling
Create `requirements.txt`:

```text
requests>=2.31.0
feedparser>=6.0.10
Pillow>=10.3.0
python-dotenv>=1.0.0
pydantic>=2.7.0
```

Create `requirements-dev.txt`:

```text
-r requirements.txt
pytest>=8.0.0
pytest-mock>=3.14.0
ruff>=0.4.0
mypy>=1.9.0
```

Create `.gitignore`:

```gitignore
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
*.db
*.sqlite3
.env
temp/
output/
*.mp4
*.png
.pytest_cache/
.ruff_cache/
.mypy_cache/
```

### 1.3 Initialize & Activate Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 1.4 Verification
```powershell
python -c "import requests, feedparser, PIL; print('All core libraries loaded successfully!')"
```

---

## Step 2: External Credentials Setup (Meta & Telegram)

### 2.1 Meta Developer App & Instagram Professional Account
1. Open Instagram on mobile -> Go to **Settings** -> **Account Type** -> Switch to **Professional (Creator or Business)**.
2. Go to [developers.facebook.com](https://developers.facebook.com) -> **Create App** -> Select **Business** type -> Name it `TrendBharat`.
3. Add the **Instagram API with Instagram Login** product.
4. Navigate to **Instagram API -> User Token Generator** -> Add your Instagram account as an **Instagram Tester**.
5. On mobile Instagram: Accept the tester invite under **Settings -> Developer -> Tester Invitations**.
6. Generate a short-lived user token with permissions:
   * `instagram_business_basic`
   * `instagram_business_content_publish`

### 2.2 Token Exchange Script
Create `scripts/exchange_token.py` to exchange the short-lived token for a **60-day long-lived token**:

```python
"""Script to exchange a short-lived Meta user token for a 60-day long-lived token."""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

def exchange_token(short_lived_token: str, client_secret: str) -> None:
    print("Exchanging short-lived token for long-lived token...")
    url = "https://graph.instagram.com/access_token"
    params = {
        "grant_type": "ig_exchange_token",
        "client_secret": client_secret,
        "access_token": short_lived_token
    }
    resp = requests.get(url, params=params, timeout=15)
    data = resp.json()

    if "access_token" not in data:
        print(f"Error exchanging token: {data}")
        sys.exit(1)

    long_lived_token = data["access_token"]
    expires_in_days = data.get("expires_in", 0) // 86400

    # Get User ID
    me_resp = requests.get(
        "https://graph.instagram.com/v21.0/me",
        params={"fields": "id,username,account_type", "access_token": long_lived_token},
        timeout=15
    )
    user_data = me_resp.json()

    print("\nSUCCESS!")
    print(f"Instagram Handle: @{user_data.get('username')}")
    print(f"User ID:          {user_data.get('id')}")
    print(f"Account Type:     {user_data.get('account_type')}")
    print(f"Token Lifespan:   ~{expires_in_days} days")
    print(f"\nAdd these to your .env file:")
    print(f"INSTAGRAM_USER_ID={user_data.get('id')}")
    print(f"INSTAGRAM_ACCESS_TOKEN={long_lived_token}")

if __name__ == "__main__":
    token = input("Enter Short-Lived User Token: ").strip()
    secret = input("Enter Meta App Secret: ").strip()
    exchange_token(token, secret)
```

### 2.3 Setup Telegram Bot
1. Open Telegram -> Message `@BotFather`.
2. Send `/newbot` -> Name it `TrendBharat Alert Bot` -> Username `trendbharat_alerts_bot`.
3. Copy the HTTP API token (`TELEGRAM_BOT_TOKEN`).
4. Send any test message to your new bot.
5. In your browser, open `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`.
6. Locate `"chat":{"id": 123456789}` -> That is your `TELEGRAM_CHAT_ID`.

### 2.4 Create `.env` Configuration File
Create `.env` in `D:\Workspace\Instaposts`:

```env
INSTAGRAM_USER_ID=your_instagram_user_id
INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
DATABASE_PATH=trendbharat.db
LOG_LEVEL=INFO
```

---

## Step 3: Data Ingestion, Sanitization & Classification Engine

### 3.1 Category Taxonomy & Safety Blocklist
Create `trendbharat/config/categories.json`:

```json
{
  "Sports": {
    "keywords": ["cricket", "ipl", "bcci", "match", "score", "vs", "cup", "tournament", "football", "messi", "ronaldo", "badminton", "kohli", "rohit", "dhoni", "test", "odi", "t20"],
    "hashtag": "#sports #cricket #indiancricket"
  },
  "Entertainment": {
    "keywords": ["movie", "trailer", "actor", "actress", "release date", "review", "song", "teaser", "ott", "netflix", "box office", "cinema", "kantara", "saiyaara", "pushpa", "bollywood"],
    "hashtag": "#entertainment #cinema #bollywood #movies"
  },
  "Technology": {
    "keywords": ["ai", "chatgpt", "gemini", "deepseek", "google", "apple", "iphone", "update", "launch", "app", "feature", "nvidia", "meta", "robotics", "software"],
    "hashtag": "#tech #ai #innovation #technews"
  },
  "Business & Finance": {
    "keywords": ["share price", "stock", "sensex", "nifty", "gold rate", "silver", "ipo", "crypto", "bitcoin", "market", "rbi", "budget", "gdp"],
    "hashtag": "#business #markets #stocks #finance"
  },
  "Jobs & Education": {
    "keywords": ["upsc", "ssc", "admit card", "result", "exam", "answer key", "syllabus", "recruitment", "vacancy", "neet", "jee", "cbse"],
    "hashtag": "#education #jobs #exams #upsc"
  },
  "General": {
    "keywords": [],
    "hashtag": "#trending #india #trendbharat"
  }
}
```

Create `trendbharat/config/blocklist.json`:

```json
{
  "blocked_terms": [
    "murder", "killed", "dead", "death", "suicide", "rape", "assault", 
    "accident", "crash", "corpse", "slur", "porn", "sex", "nude", 
    "scandal", "arrested", "custody", "convicted", "terrorist", "blast"
  ]
}
```

### 3.2 RSS Feed Reader
Create `trendbharat/collector/feed_reader.py`:

```python
"""Module to fetch India trending searches from Google Trends RSS feed."""
import logging
import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

FEED_URL = "https://trends.google.com/trending/rss?geo=IN"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

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
                    raise RuntimeError(f"Failed to fetch trends after {max_retries} attempts") from e
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
            title = item.findtext("title", default="").strip()
            traffic_node = item.find("ht:approx_traffic", ns)
            traffic_str = traffic_node.text.strip() if traffic_node is not None and traffic_node.text else "0"
            
            # Normalize traffic e.g. "100,000+" -> 100000
            clean_traffic = int(traffic_str.replace("+", "").replace(",", "") or 0)
            description = item.findtext("description", default="").strip()
            pub_date = item.findtext("pubDate", default="").strip()

            items.append({
                "feed_rank": rank,
                "query": title,
                "approx_volume": clean_traffic,
                "volume_display": traffic_str,
                "description": description,
                "pub_date": pub_date
            })

        logger.info("Extracted %d items from RSS feed", len(items))
        return items
```

### 3.3 Sanitizer, Classifier & Safety Filter
Create `trendbharat/collector/pipeline.py`:

```python
"""Data ingestion, normalization, classification and filtering pipeline."""
import html
import json
import logging
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple
from trendbharat.collector.feed_reader import FeedReader

logger = logging.getLogger(__name__)

class TrendsPipeline:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.feed_reader = FeedReader()
        self.categories = self._load_json(config_dir / "categories.json")
        self.blocklist = self._load_json(config_dir / "blocklist.json").get("blocked_terms", [])

    def _load_json(self, path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def sanitize(self, text: str) -> str:
        """Strip HTML tags, unescape HTML entities, normalize unicode."""
        text = html.unescape(text)
        text = re.sub(r"<[^>]+>", "", text)
        text = unicodedata.normalize("NFC", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def is_blocked(self, text: str) -> Tuple[bool, str]:
        """Check if any query contains terms from the blocklist."""
        normalized = text.lower()
        for term in self.blocklist:
            if re.search(r"\b" + re.escape(term) + r"\b", normalized):
                return True, term
        return False, ""

    def categorize(self, query: str, description: str) -> Tuple[str, str]:
        """Classify topic based on query and snippet keywords."""
        content = f"{query} {description}".lower()
        for cat_name, data in self.categories.items():
            if cat_name == "General":
                continue
            for kw in data["keywords"]:
                if kw in content:
                    return cat_name, data["hashtag"]
        return "General", self.categories["General"]["hashtag"]

    def run(self) -> List[Dict]:
        """Execute full ingestion pipeline, keeping top 9 clean trends."""
        raw_xml = self.feed_reader.fetch_raw_feed()
        raw_items = self.feed_reader.parse_feed(raw_xml)

        valid_trends = []
        for item in raw_items:
            clean_query = self.sanitize(item["query"])
            blocked, reason = self.is_blocked(clean_query)
            
            category, hashtags = self.categorize(clean_query, item["description"])
            trend_record = {
                **item,
                "query": clean_query,
                "category": category,
                "hashtags": hashtags,
                "blocked": blocked,
                "block_reason": reason
            }

            if not blocked:
                valid_trends.append(trend_record)
            else:
                logger.warning("Blocked trend '%s': matched term '%s'", clean_query, reason)

        if len(valid_trends) < 5:
            raise RuntimeError(f"Insufficient valid trends ({len(valid_trends)}). Minimum 5 required.")

        # Keep top 9 trends, assign ranks 1 to 9 (top search = rank 1)
        top_9 = valid_trends[:9]
        for rank, trend in enumerate(top_9, start=1):
            trend["rank"] = rank

        logger.info("Successfully selected %d clean trends", len(top_9))
        return top_9
```

### 3.4 Verification
Run the pipeline directly from PowerShell:

```powershell
python -c "from pathlib import Path; from trendbharat.collector.pipeline import TrendsPipeline; p = TrendsPipeline(Path('trendbharat/config')); trends = p.run(); print('\n'.join(f'#{t[\"rank\"]} {t[\"query\"]} [{t[\"category\"]}] - {t[\"volume_display\"]}' for t in trends))"
```

---

## Step 4: Database Layer & State Management

### 4.1 SQL Schema
Create `trendbharat/db/schema.sql`:

```sql
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_date TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL,
  started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  finished_at TIMESTAMP,
  error TEXT
);

CREATE TABLE IF NOT EXISTS trends (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
  rank INTEGER NOT NULL,
  query TEXT NOT NULL,
  category TEXT,
  approx_volume INTEGER,
  blocked BOOLEAN DEFAULT 0,
  selected BOOLEAN DEFAULT 0,
  raw_payload TEXT
);

CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL UNIQUE REFERENCES runs(id) ON DELETE CASCADE,
  caption TEXT,
  status TEXT NOT NULL,
  container_id TEXT,
  ig_media_id TEXT,
  video_bytes INTEGER,
  attempts INTEGER DEFAULT 0,
  published_at TIMESTAMP,
  error TEXT
);
```

### 4.2 Database Manager & Idempotency Controller
Create `trendbharat/db/manager.py`:

```python
"""Database operations and run idempotency controller."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "trendbharat.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        schema_file = Path(__file__).parent / "schema.sql"
        with self._conn() as conn:
            conn.executescript(schema_file.read_text(encoding="utf-8"))

    def get_or_create_run(self, run_date: str) -> Tuple[int, bool]:
        """Returns (run_id, is_already_published)."""
        with self._conn() as conn:
            row = conn.execute("SELECT id, status FROM runs WHERE run_date = ?", (run_date,)).fetchone()
            if row:
                if row["status"] == "published":
                    return row["id"], True
                return row["id"], False
            
            cur = conn.execute(
                "INSERT INTO runs (run_date, status) VALUES (?, 'started')",
                (run_date,)
            )
            return cur.lastrowid, False

    def save_trends(self, run_id: int, trends: List[Dict]):
        with self._conn() as conn:
            for t in trends:
                conn.execute(
                    """INSERT INTO trends (run_id, rank, query, category, approx_volume, blocked, selected, raw_payload)
                       VALUES (?, ?, ?, ?, ?, ?, 1, ?)""",
                    (run_id, t["rank"], t["query"], t["category"], t["approx_volume"], t.get("blocked", False), json.dumps(t))
                )

    def record_post_started(self, run_id: int, caption: str, video_bytes: int) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                """INSERT OR REPLACE INTO posts (run_id, caption, status, video_bytes, attempts)
                   VALUES (?, ?, 'pending', ?, 1)""",
                (run_id, caption, video_bytes)
            )
            return cur.lastrowid

    def mark_post_published(self, run_id: int, container_id: str, ig_media_id: str):
        with self._conn() as conn:
            conn.execute(
                """UPDATE posts SET status = 'published', container_id = ?, ig_media_id = ?, published_at = CURRENT_TIMESTAMP
                   WHERE run_id = ?""",
                (container_id, ig_media_id, run_id)
            )
            conn.execute(
                "UPDATE runs SET status = 'published', finished_at = CURRENT_TIMESTAMP WHERE id = ?",
                (run_id,)
            )

    def record_run_failed(self, run_id: int, error_msg: str):
        with self._conn() as conn:
            conn.execute(
                "UPDATE runs SET status = 'failed', error = ?, finished_at = CURRENT_TIMESTAMP WHERE id = ?",
                (error_msg, run_id)
            )
```

### 4.3 Git `data` Branch Sync Helper
Create `scripts/sync_data_branch.ps1`:

```powershell
# Restore or push sqlite database to git data branch
param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("restore", "commit")]
    [string]$Action
)

$Branch = "data"
$DbFile = "trendbharat.db"

if ($Action -eq "restore") {
    Write-Host "Restoring database from branch $Branch..."
    git fetch origin $Branch
    if ($LASTEXITCODE -eq 0) {
        git checkout "origin/$Branch" -- $DbFile
        Write-Host "Database restored successfully."
    } else {
        Write-Host "Branch $Branch does not exist yet. Fresh database will be created."
    }
} elseif ($Action -eq "commit") {
    Write-Host "Committing database to branch $Branch..."
    git checkout -B $Branch
    git add $DbFile
    git commit -m "chore(data): auto-sync database [skip ci]"
    git push origin $Branch --force
    git checkout main
}
```

---

## Step 5: Visual Card & Video Generation Engine

### 5.1 Download Google Noto Sans Fonts
Create and run `scripts/download_fonts.py` to bundle official Noto Sans Latin and Indic fonts:

```python
"""Download Google Noto Sans fonts for multi-lingual rendering."""
import os
import requests

FONTS = {
    "NotoSans-Bold.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf",
    "NotoSans-Regular.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf",
    "NotoSansDevanagari-Bold.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Bold.ttf",
    "NotoSansTamil-Bold.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansTamil/NotoSansTamil-Bold.ttf"
}

target_dir = os.path.join("trendbharat", "assets", "fonts")
os.makedirs(target_dir, exist_ok=True)

for name, url in FONTS.items():
    dest = os.path.join(target_dir, name)
    if not os.path.exists(dest):
        print(f"Downloading {name}...")
        r = requests.get(url, timeout=30)
        with open(dest, "wb") as f:
            f.write(r.content)
print("All fonts downloaded.")
```

Run it:
```powershell
python scripts/download_fonts.py
```

### 5.2 Pillow Card Generator
Create `trendbharat/render/card_builder.py`:

```python
"""Generate 1080x1920 Instagram Reel vertical cards."""
import os
from pathlib import Path
from typing import Dict, List
from PIL import Image, ImageDraw, ImageFont

CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1920

# Safe zones: clearance from top/bottom Instagram navigation & chrome
MARGIN_LEFT = 90
MARGIN_RIGHT = 140
MARGIN_TOP = 240
MARGIN_BOTTOM = 420

COLOR_BG = (11, 15, 25)          # Deep Navy
COLOR_CARD = (20, 27, 45)        # Card Plate
COLOR_TEXT_WHITE = (255, 255, 255)
COLOR_TEXT_MUTED = (148, 163, 184)
COLOR_AMBER = (245, 158, 11)     # Accent Rank
COLOR_BORDER = (30, 41, 69)

class CardBuilder:
    def __init__(self, font_dir: Path):
        self.font_dir = font_dir
        self.font_bold = str(font_dir / "NotoSans-Bold.ttf")
        self.font_regular = str(font_dir / "NotoSans-Regular.ttf")
        self.font_hindi = str(font_dir / "NotoSansDevanagari-Bold.ttf")

    def _get_font(self, text: str, size: int) -> ImageFont.FreeTypeFont:
        # Detect Devanagari Unicode range
        if any('\u0900' <= char <= '\u097F' for char in text) and os.path.exists(self.font_hindi):
            return ImageFont.truetype(self.font_hindi, size)
        return ImageFont.truetype(self.font_bold, size)

    def render_cover_card(self, date_str: str, output_path: str):
        img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), COLOR_BG)
        draw = ImageDraw.Draw(img)

        # Hook Header
        f_sub = ImageFont.truetype(self.font_bold, 36)
        draw.text((MARGIN_LEFT, MARGIN_TOP), "DAILY SEARCH PULSE", font=f_sub, fill=COLOR_AMBER)

        # Big Title
        f_title = ImageFont.truetype(self.font_bold, 86)
        draw.text((MARGIN_LEFT, MARGIN_TOP + 80), "WHAT INDIA\nSEARCHED\nTODAY", font=f_title, fill=COLOR_TEXT_WHITE)

        # Date & Subtitle
        f_date = ImageFont.truetype(self.font_regular, 44)
        draw.text((MARGIN_LEFT, MARGIN_TOP + 420), f"📅 {date_str}", font=f_date, fill=COLOR_TEXT_MUTED)

        f_desc = ImageFont.truetype(self.font_regular, 38)
        draw.text((MARGIN_LEFT, MARGIN_TOP + 500), "Top 9 Google Search Trends Countdown 🇮🇳", font=f_desc, fill=COLOR_TEXT_WHITE)

        # Footer
        self._draw_footer(draw)
        img.save(output_path, "PNG")

    def render_trend_card(self, rank: int, query: str, category: str, volume: str, date_str: str, output_path: str):
        img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), COLOR_BG)
        draw = ImageDraw.Draw(img)

        # Countdown Rank Badge (e.g. #09 down to #01)
        f_rank = ImageFont.truetype(self.font_bold, 120)
        draw.text((MARGIN_LEFT, MARGIN_TOP), f"#{rank:02d}", font=f_rank, fill=COLOR_AMBER)

        # Category Pill
        f_cat = ImageFont.truetype(self.font_bold, 32)
        cat_text = category.upper()
        draw.rounded_rectangle(
            [(MARGIN_LEFT, MARGIN_TOP + 170), (MARGIN_LEFT + 280, MARGIN_TOP + 230)],
            radius=15, fill=COLOR_CARD, outline=COLOR_BORDER, width=2
        )
        draw.text((MARGIN_LEFT + 20, MARGIN_TOP + 182), cat_text, font=f_cat, fill=COLOR_TEXT_WHITE)

        # Search Query Title (Auto-scaling font)
        font_size = 72 if len(query) < 25 else 52
        f_query = self._get_font(query, font_size)
        draw.text((MARGIN_LEFT, MARGIN_TOP + 300), query, font=f_query, fill=COLOR_TEXT_WHITE)

        # Volume tag
        if volume and volume != "0":
            f_vol = ImageFont.truetype(self.font_regular, 36)
            draw.text((MARGIN_LEFT, MARGIN_TOP + 500), f"🔥 {volume} searches today", font=f_vol, fill=COLOR_TEXT_MUTED)

        # Footer
        self._draw_footer(draw)
        img.save(output_path, "PNG")

    def _draw_footer(self, draw: ImageDraw.Draw):
        f_foot = ImageFont.truetype(self.font_regular, 30)
        y = CANVAS_HEIGHT - 220
        draw.line([(MARGIN_LEFT, y - 20), (CANVAS_WIDTH - MARGIN_RIGHT, y - 20)], fill=COLOR_BORDER, width=2)
        draw.text((MARGIN_LEFT, y), "Follow @TrendBharat · Source: Google Trends", font=f_foot, fill=COLOR_TEXT_MUTED)
```

### 5.3 Caption Generator
Create `trendbharat/render/caption_builder.py`:

```python
"""Generate Instagram caption with hook in first 125 characters."""
from typing import Dict, List

def build_caption(trends: List[Dict], date_str: str) -> str:
    # First line MUST be <= 125 chars to appear before the "...more" fold
    first_line = f"What is India searching today? Top 9 countdown for {date_str}! 🇮🇳👇"
    
    trend_lines = "\n".join(f"{t['rank']}. {t['query']} ({t['category']})" for t in trends)
    all_hashtags = " ".join(set(t.get("hashtags", "") for t in trends))

    caption = f"""{first_line}

Here are India's top trending Google searches today:
{trend_lines}

Follow @TrendBharat for your daily 30-second trend pulse.
Source: Google Trends.

#TrendBharat #IndiaTrends #TrendingNow {all_hashtags}
"""
    return caption.strip()
```

### 5.4 FFmpeg Video Compiler & Validator
Create `trendbharat/render/video_compiler.py`:

```python
"""Compile rendered PNG cards into a 30s 1080x1920 MP4 video using FFmpeg."""
import json
import logging
import subprocess
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

class VideoCompiler:
    def __init__(self, ffmpeg_bin: str = "ffmpeg", ffprobe_bin: str = "ffprobe"):
        self.ffmpeg = ffmpeg_bin
        self.ffprobe = ffprobe_bin

    def compile_countdown_video(self, image_paths: List[str], output_mp4: str) -> str:
        """
        Takes 1 cover card (2.5s) + 9 trend countdown cards (rank 9 down to 1, 3.0s each)
        and joins them with silent stereo AAC audio into a 1080x1920 H.264 MP4.
        """
        concat_txt = Path(output_mp4).parent / "concat.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for i, img in enumerate(image_paths):
                duration = 2.5 if i == 0 else 3.0
                # FFmpeg concat format requires forward slashes
                clean_path = str(Path(img).resolve()).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")
                f.write(f"duration {duration}\n")
            # Repeat last file per FFmpeg concat demuxer specification
            f.write(f"file '{clean_path}'\n")

        cmd = [
            self.ffmpeg, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_txt).replace("\\", "/"),
            "-f", "lavfi",
            "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            "-movflags", "+faststart",
            output_mp4
        ]

        logger.info("Running FFmpeg video compilation...")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            logger.error("FFmpeg compilation failed: %s", res.stderr)
            raise RuntimeError(f"FFmpeg failed with exit code {res.returncode}")

        logger.info("Video successfully compiled to %s", output_mp4)
        return output_mp4

    def validate_mp4(self, mp4_path: str):
        """Validate video file meets Instagram Reels specifications using ffprobe."""
        cmd = [
            self.ffprobe, "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,codec_name,duration",
            "-of", "json",
            mp4_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"ffprobe validation failed: {res.stderr}")

        data = json.loads(res.stdout)
        stream = data["streams"][0]
        width = int(stream["width"])
        height = int(stream["height"])
        codec = stream["codec_name"]

        if (width, height) != (1080, 1920):
            raise ValueError(f"Invalid dimensions: {width}x{height}, expected 1080x1920")
        if codec != "h264":
            raise ValueError(f"Invalid codec: {codec}, expected h264")
        logger.info("Video verified: %dx%d (%s)", width, height, codec)
```

---

## Step 6: Meta Instagram Graph API Publishing Client

### 6.1 Resumable Reels Uploader
Create `trendbharat/publisher/instagram_client.py`:

```python
"""Meta Instagram Graph API client for Reels publishing."""
import logging
import os
import time
from typing import Dict
import requests

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.instagram.com/v21.0"

class InstagramPublisher:
    def __init__(self, user_id: str, access_token: str):
        self.user_id = user_id
        self.token = access_token

    def check_quota(self) -> int:
        """Check content publishing quota for today."""
        url = f"{GRAPH_API_BASE}/{self.user_id}/content_publishing_limit"
        res = requests.get(url, params={"access_token": self.token}, timeout=15)
        res.raise_for_status()
        data = res.json().get("data", [{}])[0]
        quota_used = data.get("quota_usage", 0)
        logger.info("Current Instagram quota usage: %d / 100", quota_used)
        return quota_used

    def publish_reel(self, mp4_path: str, caption: str) -> str:
        """Complete 4-step Reels publication: Create Container -> Resumable Upload -> Poll -> Publish."""
        file_size = os.path.getsize(mp4_path)

        # 1. Create Media Container
        logger.info("Step 1: Creating Instagram Reels container...")
        init_url = f"{GRAPH_API_BASE}/{self.user_id}/media"
        params = {
            "media_type": "REELS",
            "upload_type": "resumable",
            "caption": caption,
            "access_token": self.token
        }
        res = requests.post(init_url, data=params, timeout=30)
        res.raise_for_status()
        init_data = res.json()
        container_id = init_data["id"]
        upload_url = init_data["uri"]

        # 2. Upload Video Binary Stream
        logger.info("Step 2: Uploading %d bytes of video binary...", file_size)
        headers = {
            "Authorization": f"OAuth {self.token}",
            "Offset": "0",
            "Content-Length": str(file_size),
            "Content-Type": "application/octet-stream"
        }
        with open(mp4_path, "rb") as f:
            upload_res = requests.post(upload_url, headers=headers, data=f, timeout=120)
            upload_res.raise_for_status()

        # 3. Poll Container Status until FINISHED
        logger.info("Step 3: Waiting for Instagram to process video...")
        status_url = f"{GRAPH_API_BASE}/{container_id}"
        max_polls = 15
        for poll in range(1, max_polls + 1):
            time.sleep(15)
            s_res = requests.get(status_url, params={"fields": "status_code", "access_token": self.token}, timeout=15)
            status_code = s_res.json().get("status_code")
            logger.info("Poll %d/%d: status = %s", poll, max_polls, status_code)

            if status_code == "FINISHED":
                break
            elif status_code in ("ERROR", "EXPIRED"):
                raise RuntimeError(f"Instagram video processing failed with status: {status_code}")
        else:
            raise TimeoutError("Timed out waiting for Instagram to finish processing video")

        # 4. Trigger Publication
        logger.info("Step 4: Publishing Reel container %s...", container_id)
        pub_url = f"{GRAPH_API_BASE}/{self.user_id}/media_publish"
        pub_res = requests.post(pub_url, data={"creation_id": container_id, "access_token": self.token}, timeout=30)
        pub_res.raise_for_status()
        ig_media_id = pub_res.json()["id"]

        logger.info("Reel successfully published! Media ID: %s", ig_media_id)
        return ig_media_id
```

---

## Step 7: Telegram Alerts & Daily Orchestrator CLI

### 7.1 Telegram Alert Dispatcher
Create `trendbharat/alerts/telegram_notifier.py`:

```python
"""Send execution success cards and failure alerts to Telegram."""
import logging
import requests

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def send_success(self, date_str: str, trend_count: int, ig_media_id: str):
        reel_url = f"https://www.instagram.com/reel/{ig_media_id}"
        msg = f"""✅ *TrendBharat Daily Reel Published!*
📅 *Date:* {date_str}
🔥 *Trends Shown:* {trend_count} of 9
🎬 *Watch Reel:* [Click Here]({reel_url})
"""
        self._send(msg)

    def send_failure(self, date_str: str, stage: str, error_msg: str):
        msg = f"""🚨 *TrendBharat Pipeline Failed!*
📅 *Date:* {date_str}
💥 *Stage:* `{stage}`
⚠️ *Error:* `{error_msg[:300]}`
"""
        self._send(msg)

    def _send(self, text: str):
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not configured; skipping notification.")
            return
        try:
            requests.post(
                self.api_url,
                json={"chat_id": self.chat_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": False},
                timeout=10
            )
        except Exception as e:
            logger.error("Failed to send Telegram alert: %s", e)
```

### 7.2 Main Daily Orchestrator CLI
Create `trendbharat/scheduler/daily_runner.py`:

```python
"""Main pipeline entrypoint."""
import argparse
import datetime
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from trendbharat.alerts.telegram_notifier import TelegramNotifier
from trendbharat.collector.pipeline import TrendsPipeline
from trendbharat.db.manager import DatabaseManager
from trendbharat.publisher.instagram_client import InstagramPublisher
from trendbharat.render.caption_builder import build_caption
from trendbharat.render.card_builder import CardBuilder
from trendbharat.render.video_compiler import VideoCompiler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("trendbharat.runner")

def main():
    parser = argparse.ArgumentParser(description="TrendBharat Daily Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Compile video and verify without publishing to Instagram")
    parser.add_argument("--post-now", action="store_true", help="Execute live publishing to Instagram")
    parser.add_argument("--force-date", type=str, help="Override date in YYYY-MM-DD format")
    args = parser.parse_args()

    load_dotenv()
    today_str = args.force_date or datetime.date.today().isoformat()
    formatted_date = datetime.date.fromisoformat(today_str).strftime("%B %d, %Y")

    notifier = TelegramNotifier(os.getenv("TELEGRAM_BOT_TOKEN", ""), os.getenv("TELEGRAM_CHAT_ID", ""))
    db = DatabaseManager(os.getenv("DATABASE_PATH", "trendbharat.db"))

    # 1. Idempotency Check
    run_id, already_published = db.get_or_create_run(today_str)
    if already_published and not args.dry_run:
        logger.info("Run for %s already published. Exiting.", today_str)
        sys.exit(0)

    try:
        # 2. Ingestion & Filtering
        logger.info("--- Stage 1: Collecting Trends ---")
        pipeline = TrendsPipeline(Path("trendbharat/config"))
        trends = pipeline.run()
        db.save_trends(run_id, trends)

        # 3. Card Generation
        logger.info("--- Stage 2: Rendering Cards ---")
        temp_dir = Path("temp/cards")
        temp_dir.mkdir(parents=True, exist_ok=True)
        card_builder = CardBuilder(Path("trendbharat/assets/fonts"))

        cover_path = str(temp_dir / f"cover_{today_str}.png")
        card_builder.render_cover_card(formatted_date, cover_path)

        # Render countdown cards from rank 9 down to 1
        trend_images = [cover_path]
        for t in reversed(trends):
            c_path = str(temp_dir / f"trend_{today_str}_{t['rank']}.png")
            card_builder.render_trend_card(t['rank'], t['query'], t['category'], t['volume_display'], formatted_date, c_path)
            trend_images.append(c_path)

        # 4. Video Compilation & Validation
        logger.info("--- Stage 3: Compiling Video ---")
        output_dir = Path("temp/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        mp4_path = str(output_dir / f"trendbharat_{today_str}.mp4")

        compiler = VideoCompiler()
        compiler.compile_countdown_video(trend_images, mp4_path)
        compiler.validate_mp4(mp4_path)

        caption = build_caption(trends, formatted_date)
        video_bytes = os.path.getsize(mp4_path)
        db.record_post_started(run_id, caption, video_bytes)

        # 5. Instagram Publishing
        if args.dry_run:
            logger.info("DRY-RUN COMPLETE: Video rendered at %s (Skipping publish)", mp4_path)
            print(f"\n[DRY RUN SUCCESS] Generated video: {mp4_path}\nCaption:\n{caption}")
            sys.exit(0)

        logger.info("--- Stage 4: Publishing to Instagram ---")
        user_id = os.environ["INSTAGRAM_USER_ID"]
        token = os.environ["INSTAGRAM_ACCESS_TOKEN"]
        publisher = InstagramPublisher(user_id, token)
        ig_media_id = publisher.publish_reel(mp4_path, caption)

        # 6. Finalize State & Notify
        db.mark_post_published(run_id, "direct_upload", ig_media_id)
        notifier.send_success(formatted_date, len(trends), ig_media_id)
        logger.info("Pipeline completed successfully for %s!", today_str)

    except Exception as e:
        logger.exception("Pipeline crashed: %s", e)
        db.record_run_failed(run_id, str(e))
        notifier.send_failure(today_str, "Pipeline Execution", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 7.3 Test Local Dry Run
```powershell
python -m trendbharat.scheduler.daily_runner --dry-run
```
Inspect the output video in `temp/output/trendbharat_<DATE>.mp4` using VLC media player.

---

## Step 8: CI/CD Automation & Scheduled Execution

### 8.1 GitHub Actions Workflow
Create `.github/workflows/daily_pipeline.yml`:

```yaml
name: TrendBharat Daily Auto-Poster

on:
  workflow_dispatch:
  schedule:
    # Backup trigger: 13:00 UTC = 6:30 PM IST daily
    - cron: '0 13 * * *'

jobs:
  publish_reel:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install System FFmpeg
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg

      - name: Setup Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install Python Dependencies
        run: pip install -r requirements.txt

      - name: Download Noto Sans Fonts
        run: python scripts/download_fonts.py

      - name: Restore SQLite Database from Data Branch
        run: |
          git fetch origin data || true
          git checkout origin/data -- trendbharat.db || echo "No previous database found"

      - name: Run TrendBharat Pipeline
        env:
          INSTAGRAM_USER_ID: ${{ secrets.INSTAGRAM_USER_ID }}
          INSTAGRAM_ACCESS_TOKEN: ${{ secrets.INSTAGRAM_ACCESS_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python -m trendbharat.scheduler.daily_runner --post-now

      - name: Commit Updated Database to Data Branch
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git config user.name "TrendBharat Bot"
          git config user.email "bot@trendbharat.internal"
          git checkout -B data
          git add trendbharat.db
          git commit -m "chore(data): auto-update state for $(date +'%Y-%m-%d') [skip ci]" || echo "No state changes"
          git push origin data --force
```

### 8.2 Setup Free External Cron (Bypassing GitHub Schedule Delays)
1. Go to [cron-job.org](https://cron-job.org) (100% free service).
2. Create new cron job:
   * **Title:** `TrendBharat Daily Trigger`
   * **URL:** `https://api.github.com/repos/<YOUR_GITHUB_USERNAME>/<YOUR_REPO>/actions/workflows/daily_pipeline.yml/dispatches`
   * **Execution Schedule:** Every day at **13:00 UTC** (6:30 PM IST).
   * **HTTP Method:** `POST`
   * **HTTP Headers:**
     - `Authorization`: `Bearer <YOUR_GITHUB_PERSONAL_ACCESS_TOKEN>`
     - `Accept`: `application/vnd.github.v3+json`
     - `User-Agent`: `TrendBharat-Cron`
   * **Request Body:** `{"ref": "main"}`

---

## Step 9: Staging Pilot & Production Go-Live Checklist

Follow this checklist to take TrendBharat live:

- [ ] **Step 9.1 — Unit Test Verification**
  Run all automated tests:
  ```powershell
  pytest tests/ -v
  ```
- [ ] **Step 9.2 — Local Live Publish to Test Account**
  Run live publisher once manually from local machine:
  ```powershell
  python -m trendbharat.scheduler.daily_runner --post-now
  ```
  Open Instagram mobile app -> Verify the Reel appears with crisp visuals, readable Indic text, and AAC audio.
- [ ] **Step 9.3 — Push to GitHub**
  ```powershell
  git add .
  git commit -m "feat: complete TrendBharat MVP automated pipeline"
  git push origin main
  ```
- [ ] **Step 9.4 — Trigger Manual GitHub Actions Run**
  Go to GitHub -> **Actions** -> **TrendBharat Daily Auto-Poster** -> Click **Run workflow**. Verify green checkmark.
- [ ] **Step 9.5 — 7-Day Automated Shadow Run**
  Keep GitHub Actions running daily for 7 days. Verify Telegram sends success card every day at 7:05 PM IST with zero manual intervention.
- [ ] **Step 9.6 — Day 35 Production Sign-Off**
  Confirm 30-day autonomous zero-cost operation.

