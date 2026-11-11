# InstaTrend / TrendBharat

**Automated Daily Instagram News Card Pipeline for India Trends**

InstaTrend finds what India is searching for right now on Google Trends, fetches authentic high-definition subject photography and verified factual reporting, and renders modern, viral Instagram news feed posts (`1080 × 1350 px`, 4:5 portrait) in the high-contrast aesthetic popularized by major digital publishers (*RVCJ, Inshorts, Brut India*).

Every day, the completed package (high-resolution image + formatted viral caption with hashtags) is automatically delivered directly to your private Telegram bot for instant 1-click posting.

---

## 🎨 Three-Tier Visual Card Architecture

* **Top Section (Above Photo):**
  * Soft-tint category badge (`CRICKET & SPORTS`, `POLITICS & GOVERNANCE`, `CINEMA & ENTERTAINMENT`, `TECH & INNOVATION`, etc.)
  * Clean brand watermark (`@InstaTrend`)
  * Heavy, high-contrast bold black headline
* **Middle Section (Center Stage Photo):**
  * High-definition subject photography sourced from Wikipedia / Wikimedia REST APIs
  * Smart face-framing algorithm (preserves facial features, foreheads, and eyes in vertical portraits)
  * Clean divider borders
* **Bottom Section (Below Photo):**
  * Key takeaway statement highlighted in **Vibrant Crimson Red (`#DC2626`)** with a vertical accent bar
  * Full original factual story context (*who, what, where, why*) in dark charcoal slate (`#334155`)
  * Interaction footer with swipe prompt and verified brand handle

---

## ⚡ Key Highlights

* **100% Free ($0 / month):** Zero API costs. Uses free public feeds, open-source typography (Google Noto Sans), and free Telegram delivery.
* **Smart Content Safety:** Filters out tragedy, violence, and adult keywords using `trendbharat/config/blocklist.json`.
* **Zero Host Cost (GitHub Actions):** Scheduled via GitHub Actions cron to run automatically every morning at 8:00 AM IST (02:30 UTC), consuming under 20 free minutes per month (out of 2,000 free minutes).
* **Multi-Lingual Script Support:** Auto-resolves Devanagari (Hindi), Tamil, and Telugu scripts with bundled Noto Sans font families.
* **Idempotent SQLite Engine:** Ensures runs never duplicate on the same date.

---

## 🚀 Setup & Local Execution

### 1. Clone & Install
```powershell
git clone https://github.com/shubham4518/InstaTrend.git
cd InstaTrend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Create a `.env` file in the root directory:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_telegram_chat_id
DATABASE_PATH=trendbharat.db
```

### 3. Run Pipeline
```powershell
# Run a dry-run test without sending to Telegram:
python -m trendbharat.scheduler.daily_runner --dry-run

# Run and deliver live post to Telegram:
python -m trendbharat.scheduler.daily_runner --post-now
```

---

## ⚙️ Automated GitHub Actions Scheduling

The repository includes a ready-to-run GitHub Actions workflow at [`.github/workflows/daily_post.yml`](.github/workflows/daily_post.yml).

To enable cloud automation:
1. Go to your GitHub repository: **Settings → Secrets and variables → Actions**
2. Click **New repository secret** and add:
   * `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   * `TELEGRAM_CHAT_ID`: Your numerical Telegram user/chat ID
3. The workflow will automatically fire every morning at **8:00 AM IST** and can also be triggered manually with 1 click under the **Actions** tab.
