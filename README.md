# TrendBharat

**Automated Daily Instagram Reels Pipeline for India Search Trends**

TrendBharat finds what India is searching for today on Google Trends, turns the top 9 trends into a ready-made 9:16 vertical video countdown Reel, and publishes it automatically through the official Meta Instagram Graph API every day at 7:00 PM IST.

## Architecture & Features
* **Zero Cost ($0/month):** Uses free public Google Trends RSS feed, Pillow, FFmpeg, SQLite, Telegram Bot, and GitHub Actions.
* **Content Safety:** Automated blocklist filtering against violent, adult, defamatory, and tragic topics.
* **Multi-Lingual Typography:** Auto-resolves Indic fonts (Hindi Devanagari, Tamil, etc.) with safe-zone margin formatting.
* **Resumable Meta API Publishing:** Official Meta Graph API integration with 60-day token automated refresh.
* **Idempotent Runs:** State persistence in SQLite committed to a dedicated `data` Git branch.

