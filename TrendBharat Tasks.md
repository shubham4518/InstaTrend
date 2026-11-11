# TrendBharat: Engineering Task Backlog & Execution Checklist
**Granular Implementation Tasks for Automated Daily Instagram Reels Pipeline**
*Derived from: TrendBharat Implementation Roadmap (v1.0.0)*

---

## Quick Reference Summary

| Phase | Milestone | Task Count | Est. Hours | Target Days | Status |
|---|---|:---:|:---:|:---:|:---:|
| **Phase 0** | Project Setup, Accounts & Credentials | 6 tasks | 6h | Days 1–3 | Ready |
| **Phase 1** | Ingestion, Sanitization & Classification | 5 tasks | 8h | Days 4–7 | Blocked by Phase 0 |
| **Gate 1**  | Ingestion & Safety Gate Check | 1 gate | 1h | Day 7 | Blocked by Phase 1 |
| **Phase 2** | Database Layer & State Management | 4 tasks | 6h | Days 8–10 | Blocked by Gate 1 |
| **Phase 3** | Typography, Pillow Cards & FFmpeg Video | 6 tasks | 16h | Days 11–18 | Blocked by Phase 2 |
| **Phase 4** | Instagram Graph API & Resumable Media | 6 tasks | 14h | Days 19–25 | Blocked by Phase 3 |
| **Gate 2**  | End-to-End Publishing Gate Check | 1 gate | 2h | Day 25 | Blocked by Phase 4 |
| **Phase 5** | CI/CD Orchestration, Telemetry & Reliability | 5 tasks | 6h | Days 26–28 | Blocked by Gate 2 |
| **Phase 6** | 7-Day Shadow Run & Production Go-Live | 5 tasks | 10h | Days 29–35 | Blocked by Phase 5 |
| **Gate 3**  | Production Go-Live Gate Check | 1 gate | 1h | Day 35 | Blocked by Phase 6 |
| **Total**   | **Complete MVP Launch** | **40 items** | **70h** | **35 Days** | |

---

## Phase 0: Project Setup, Accounts & Credentials Provisioning
**Target Window: Days 1–3 · Total Est: 6 Hours · Status: Ready**

- [x] ### `TB-001` Initialize Project Repository Scaffold
  - **Module / Files:**
    - `trendbharat/`
    - `trendbharat/collector/__init__.py`
    - `trendbharat/render/__init__.py`
    - `trendbharat/publisher/__init__.py`
    - `trendbharat/scheduler/__init__.py`
    - `trendbharat/db/__init__.py`
    - `trendbharat/config/`
    - `trendbharat/assets/fonts/`
    - `trendbharat/tests/`
    - `.gitignore`
    - `README.md`
  - **Prerequisites:** None
  - **Est. Effort:** 1 hour
  - **Acceptance Criteria:**
    - Clean Python package structure initialized with `__init__.py` files in each subpackage.
    - Comprehensive `.gitignore` covering Python cache (`__pycache__`, `.pytest_cache`), virtualenvs (`.venv`), local SQLite databases (`*.db`, `*.sqlite3`), generated MP4/PNG assets, and environment variables (`.env`).
  - **Verification:** `python -c "import trendbharat; print('Package initialized')"` succeeds without error.

---

- [x] ### `TB-002` Configure Python 3.12 Virtualenv & Development Tooling
  - **Module / Files:**
    - `requirements.txt`
    - `requirements-dev.txt`
    - `pyproject.toml`
  - **Prerequisites:** `TB-001`
  - **Est. Effort:** 1 hour
  - **Acceptance Criteria:**
    - Python 3.12 virtual environment established.
    - Production dependencies pinned in `requirements.txt`:
      `requests>=2.31.0`, `feedparser>=6.0.10`, `Pillow>=10.3.0`, `python-dotenv>=1.0.0`.
    - Dev tooling configured in `pyproject.toml`:
      `pytest>=8.0.0`, `ruff>=0.4.0`, `mypy>=1.9.0`.
    - Ruff and Mypy configurations enforce strict linting and type checking rules.
  - **Verification:** Run `ruff check .` and `mypy --install-types` with exit code 0.

---

- [ ] ### `TB-003` Provision Meta Developer App & Instagram Creator Account
  - **Module / Files:**
    - `docs/meta_setup_guide.md`
  - **Prerequisites:** None (can run in parallel)
  - **Est. Effort:** 1.5 hours
  - **Acceptance Criteria:**
    - Instagram target account switched to **Professional (Creator or Business)** in mobile app settings.
    - Meta Developer App created under [developers.facebook.com](https://developers.facebook.com) of type **Business**.
    - **Instagram API with Instagram Login** added to app products.
    - App permissions enabled: `instagram_business_basic`, `instagram_business_content_publish`.
    - Instagram user account registered as an authorized App Tester / Developer.
  - **Verification:** Instagram account displays as linked under Meta App Dashboard -> App Roles.

---

- [ ] ### `TB-004` Build Token Exchange & Validation Script
  - **Module / Files:**
    - `scripts/exchange_token.py`
  - **Prerequisites:** `TB-003`
  - **Est. Effort:** 1 hour
  - **Acceptance Criteria:**
    - Script accepts short-lived User Access Token from Meta Graph API Explorer.
    - Calls `GET https://graph.instagram.com/access_token` to exchange for a **60-day long-lived token**.
    - Queries `GET https://graph.instagram.com/v21.0/me?fields=id,username,account_type` to retrieve target `ig_user_id`.
    - Displays token expiration timestamp and validates account type is `BUSINESS` or `CREATOR`.
  - **Verification:** Script outputs `Valid 60-day token obtained for @<handle> (Expires: <date>)`.

---

- [x] ### `TB-005` Provision Telegram Alert Bot
  - **Module / Files:**
    - `scripts/test_telegram.py`
  - **Prerequisites:** None
  - **Est. Effort:** 0.5 hours
  - **Acceptance Criteria:**
    - New bot created via `@BotFather` on Telegram (e.g. `@TrendBharatAlertBot`).
    - Telegram Bot API token secured.
    - Recipient Telegram Chat ID obtained by sending initial message and querying `GET /getUpdates`.
    - Test script sends formatted Markdown test notification (`"🔔 TrendBharat Alert System Online"`).
  - **Verification:** Test alert received on mobile Telegram client.

---

- [ ] ### `TB-006` Setup Local Environment & GitHub Repository Secrets
  - **Module / Files:**
    - `.env.example`
    - `.env`
  - **Prerequisites:** `TB-004`, `TB-005`
  - **Est. Effort:** 1 hour
  - **Acceptance Criteria:**
    - `.env.example` committed with placeholder environment variables:
      ```env
      INSTAGRAM_USER_ID=your_instagram_user_id
      INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token
      TELEGRAM_BOT_TOKEN=your_telegram_bot_token
      TELEGRAM_CHAT_ID=your_telegram_chat_id
      DATABASE_PATH=trendbharat.db
      LOG_LEVEL=INFO
      ```
    - Local `.env` created and added to `.gitignore`.
    - Matching GitHub Actions Secrets added to repository settings:
      `INSTAGRAM_USER_ID`, `INSTAGRAM_ACCESS_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `GH_PAT_DATA_BRANCH`.
  - **Verification:** Python config loader reads all required keys from `.env` without `KeyError`.

---

## Phase 1: Ingestion, Sanitization & Classification Engine
**Target Window: Days 4–7 · Total Est: 8 Hours · Status: Blocked by Phase 0**

- [ ] ### `TB-101` Implement RSS Feed Ingestion Module
  - **Module / Files:**
    - `trendbharat/collector/feed_reader.py`
  - **Prerequisites:** `TB-001`, `TB-002`
  - **Est. Effort:** 2 hours
  - **Acceptance Criteria:**
    - Connects to Google Trends India RSS feed: `https://trends.google.com/trending/rss?geo=IN`.
    - Sets appropriate HTTP headers (`User-Agent: Mozilla/5.0 ...`, 15-second timeout).
    - Implements retry mechanism: 3 attempts with exponential backoff (`factor=2s`).
    - Uses `feedparser` / `xml.etree` to parse `<item>` elements.
    - Extracts `title`, `ht:approx_traffic` (normalized as integer volume), `pubDate`, and `description`.
    - Supports `fixture_path` parameter to load recorded XML files in offline/test environments.
  - **Verification:** `python -m trendbharat.collector.feed_reader` prints parsed list of 10 trends.

---

- [ ] ### `TB-102` Implement Data Sanitizer & Normalizer
  - **Module / Files:**
    - `trendbharat/collector/sanitizer.py`
  - **Prerequisites:** `TB-101`
  - **Est. Effort:** 1.5 hours
  - **Acceptance Criteria:**
    - Strips leading/trailing punctuation, quotes, excess whitespace, and unescaped HTML entities (e.g. `&amp;`, `&#39;`).
    - Normalizes Indic and Latin Unicode characters into NFC form.
    - Preserves vital casing (e.g. acronyms like "IPL", "BCCI", "AI", "UPSC").
    - Truncates oversized query strings to a maximum of 60 characters with clean word boundaries.
  - **Verification:** Unit tests confirm clean outputs for inputs containing HTML tags and broken Unicode.

---

- [ ] ### `TB-103` Build Rules-Based Category Classifier
  - **Module / Files:**
    - `trendbharat/config/categories.json`
    - `trendbharat/collector/categorizer.py`
  - **Prerequisites:** `TB-102`
  - **Est. Effort:** 2 hours
  - **Acceptance Criteria:**
    - `categories.json` defines category mappings and hashtags:
      - `Sports` (`#cricket #ipl #sports #indvsaus`)
      - `Entertainment` (`#bollywood #cinema #ott #netflix`)
      - `Technology` (`#tech #ai #innovation #gemini`)
      - `Business` (`#stocks #sensex #economy #gold`)
      - `Jobs & Education` (`#upsc #results #education`)
      - `General` (`#india #trendingnow`)
    - Classifier scans trend query and news snippet; returns matched category name, normalized score, and relevant hashtags.
    - Falls back safely to `General` if no high-confidence keyword matches.
  - **Verification:** Test runner asserts correct categorization across 30 sample Indian news trends.

---

- [ ] ### `TB-104` Implement Content Safety Blocklist Filter
  - **Module / Files:**
    - `trendbharat/config/blocklist.json`
    - `trendbharat/collector/safety_filter.py`
  - **Prerequisites:** `TB-102`
  - **Est. Effort:** 1.5 hours
  - **Acceptance Criteria:**
    - `blocklist.json` compiles sensitive and prohibited regex patterns:
      - Adult / sexually explicit queries.
      - Homicide, violent assault, rape, suicide, and gruesome accidents.
      - Communal provocation, hate speech, and religious defamation.
      - Ongoing sub-judice criminal litigation / defaming individual names.
    - Filter scans query and news snippet; marks violating trends with `blocked=True` and records exclusion reason.
    - Selects the next clean candidate from feed to guarantee top 9 trends.
    - Throws `InsufficientTrendsException` if fewer than 5 clean trends remain in the feed.
  - **Verification:** Test suite verifies that simulated unsafe queries are caught and discarded.

---

- [ ] ### `TB-105` Collector Pipeline Integration & Test Suite
  - **Module / Files:**
    - `trendbharat/collector/pipeline.py`
    - `tests/test_collector.py`
  - **Prerequisites:** `TB-101`, `TB-102`, `TB-103`, `TB-104`
  - **Est. Effort:** 1 hour
  - **Acceptance Criteria:**
    - `collect_daily_trends()` brings together reader, sanitizer, filter, and categorizer.
    - Returns structured `List[TrendItem]` containing exactly 9 selected trends (ranks 1–9) plus reserve backups.
    - Pytest suite tests offline mock XML, broken XML, network timeouts, and blocklist triggers.
  - **Verification:** `pytest tests/test_collector.py -v` passes with 100% assertions.

---

### GATE 1: Ingestion & Safety Quality Gate Check
- [ ] **Gate Evaluation Tasks:**
  1. Ingest 7 live daily feed samples from `https://trends.google.com/trending/rss?geo=IN` without exceptions.
  2. Run synthetic suite of 50 sensitive/toxic search queries through safety filter; confirm 0% leakage.
  3. Verify keyword classifier accuracy exceeds 85% on verified samples.
  - **Gate Decision:** Formal sign-off to proceed to Phase 2.

---

## Phase 2: Database Layer & State Management
**Target Window: Days 8–10 · Total Est: 6 Hours · Status: Blocked by Gate 1**

- [ ] ### `TB-201` Implement SQLite Schema & Models
  - **Module / Files:**
    - `trendbharat/db/schema.sql`
    - `trendbharat/db/models.py`
  - **Prerequisites:** Gate 1 Pass
  - **Est. Effort:** 1.5 hours
  - **Acceptance Criteria:**
    - Defines `schema.sql` according to Technical Specification:
      - `runs` (id, run_date UNIQUE, status, started_at, finished_at, error)
      - `trends` (id, run_id, rank, query, category, approx_volume, blocked, selected, raw_payload)
      - `posts` (id, run_id UNIQUE, caption, status, container_id, ig_media_id, video_bytes, attempts, published_at, error)
      - `slides` (id, post_id, position, trend_id, image_path)
    - Pydantic/dataclass models in `models.py` representing each entity with type safety.
  - **Verification:** Script initializes fresh SQLite database and validates table creation.

---

- [ ] ### `TB-202` Implement Database Manager & Idempotency Controller
  - **Module / Files:**
    - `trendbharat/db/manager.py`
  - **Prerequisites:** `TB-201`
  - **Est. Effort:** 2 hours
  - **Acceptance Criteria:**
    - Context-managed SQLite connection handler with `PRAGMA foreign_keys = ON;` and `PRAGMA journal_mode = WAL;`.
    - `get_or_create_run(run_date)`:
      - If run already has `status == 'published'`, returns run with flag `already_published=True`.
      - If run exists with `status == 'failed'`, permits resuming/retrying.
      - If no run exists, creates new record with `status == 'started'`.
    - Transactional write methods: `save_trends()`, `save_post_container()`, `mark_post_published()`.
  - **Verification:** Concurrent/duplicate insertion test verifies unique constraint enforcement on `run_date`.

---

- [ ] ### `TB-203` Implement Git `data` Branch Synchronization
  - **Module / Files:**
    - `scripts/sync_data_branch.py`
  - **Prerequisites:** `TB-202`
  - **Est. Effort:** 1.5 hours
  - **Acceptance Criteria:**
    - Script handles state restoration and persistence across stateless GitHub Actions runner runs:
      - `restore_db()`: Checks out or downloads `trendbharat.db` from `data` branch. Runs schema migrations if new.
      - `commit_db()`: Adds `trendbharat.db`, commits with message `chore(data): sync db for YYYY-MM-DD [skip ci]`, and pushes to `data` branch using `GH_PAT_DATA_BRANCH`.
    - Handles merge conflicts using `--ours` strategy (the latest run is authoritative).
  - **Verification:** Dry-run script performs commit and push simulation in a local test branch.

---

- [ ] ### `TB-204` Database Layer Integration & Crash Recovery Tests
  - **Module / Files:**
    - `tests/test_db.py`
  - **Prerequisites:** `TB-202`, `TB-203`
  - **Est. Effort:** 1 hour
  - **Acceptance Criteria:**
    - Pytest test cases covering:
      - Complete lifecycle: `started` -> `collected` -> `rendered` -> `published`.
      - Recovery from crash at `rendered` state without re-collecting trends.
      - Enforcement of cascading deletes (`ON DELETE CASCADE`).
  - **Verification:** `pytest tests/test_db.py -v` passes with 100% assertions.

---

## Phase 3: Visual Typography & Video Rendering Engine
**Target Window: Days 11–18 · Total Est: 16 Hours · Status: Blocked by Phase 2**

- [ ] ### `TB-301` Typography Asset Setup & Indic Script Font Resolver
  - **Module / Files:**
    - `trendbharat/assets/fonts/`
    - `trendbharat/render/font_resolver.py`
  - **Prerequisites:** `TB-001`
  - **Est. Effort:** 2 hours
  - **Acceptance Criteria:**
    - Bundle open-source Google Noto Sans fonts under `assets/fonts/`:
      - `NotoSans-Bold.ttf`, `NotoSans-Regular.ttf`
      - `NotoSansDevanagari-Bold.ttf` (Hindi, Marathi)
      - `NotoSansTamil-Bold.ttf`, `NotoSansBengali-Bold.ttf`, `NotoSansTelugu-Bold.ttf`
    - `font_resolver.py` inspects character Unicode blocks in input string and selects the matching font.
    - Falls back cleanly to English Noto Sans for standard Latin text.
  - **Verification:** Renders sample text containing Hindi, Tamil, and English characters without empty box (`□`) glyphs.

---

- [ ] ### `TB-302` Implement Pillow Card Generator & Safe Zone Mask
  - **Module / Files:**
    - `trendbharat/render/card_builder.py`
    - `trendbharat/render/templates.py`
  - **Prerequisites:** `TB-301`
  - **Est. Effort:** 4 hours
  - **Acceptance Criteria:**
    - Canvas dimensions: Exactly 1080 × 1920 pixels (9:16 vertical).
    - Instagram Safe Zone margins strictly enforced:
      - Top margin: 240px.
      - Bottom margin: 420px.
      - Right margin: 140px.
      - Left margin: 80px.
    - Card Type A — Cover Slide:
      - Main Hook: "WHAT INDIA SEARCHED TODAY".
      - Calendar Date (e.g. "OCTOBER 30, 2026").
      - Subheading: "Top 9 Trending Searches · Countdown".
      - Footer: Handle `@TrendBharat` + "Source: Google Trends".
    - Card Type B — Trend Countdown Slide:
      - Giant Rank Counter: `#09` down to `#01` in electric amber (`#F59E0B`).
      - Category Badge: Pill box showing `CRICKET`, `TECH`, `CINEMA`.
      - Trend Title: Auto-shrinking text (starts 68pt, scales down to 42pt, wraps to max 2 lines, truncates with `...` if needed).
      - Volume Badge: e.g. `🔥 200K+ searches`.
      - Consistent footer on every slide.
  - **Verification:** Script outputs 10 PNG images (1 cover + 9 trends) in `temp/cards/`; visually confirmed against Instagram UI mask.

---

- [ ] ### `TB-303` Implement Caption & Hashtag Builder
  - **Module / Files:**
    - `trendbharat/render/caption_builder.py`
  - **Prerequisites:** `TB-103`
  - **Est. Effort:** 1.5 hours
  - **Acceptance Criteria:**
    - Generates Instagram caption adhering strictly to the PRD template:
      ```text
      What is India searching today? Watch the top 9 countdown! ({date_str}) 🇮🇳

      Today's top trending searches across India:
      1. {trend_1}
      2. {trend_2}
      ...
      9. {trend_9}

      Follow @{handle} for your daily 30-second trend pulse.
      Source: Google Trends.

      #trendbharat #indiatrends #googletrends #{category_hashtags}
      ```
    - Critical Rule: The first line must be under 125 characters so the hook displays before the fold ("...more").
  - **Verification:** Unit test asserts `len(caption.split('\n')[0]) <= 125` across all dates.

---

- [ ] ### `TB-304` Implement FFmpeg Video Assembler
  - **Module / Files:**
    - `trendbharat/render/video_compiler.py`
  - **Prerequisites:** `TB-302`
  - **Est. Effort:** 4 hours
  - **Acceptance Criteria:**
    - Sequences 10 cards: Cover slide (2.5s) + 9 Countdown slides (3.0s each, from rank 9 down to 1).
    - Total video duration: ~29.5 seconds.
    - Adds smooth 0.3s crossfade transitions between slides using FFmpeg `xfade` filter.
    - Video Encoding Parameters:
      - Codec: `libx264`
      - Profile: `high`
      - Pixel Format: `yuv420p`
      - Framerate: `30 fps`
      - Resolution: `1080x1920`
    - Audio Integration:
      - Silent AAC audio stream generated via `anullsrc=channel_layout=stereo:sample_rate=44100` or royalty-free audio loop from `assets/audio/lofi_beat.mp3`.
      - Audio codec: `aac`, bitrate: `192k`.
  - **Verification:** Running compiler produces valid MP4 file (`output.mp4`) in under 60 seconds on a standard CPU.

---

- [ ] ### `TB-305` Implement Pre-Flight Probe Validator
  - **Module / Files:**
    - `trendbharat/render/validator.py`
  - **Prerequisites:** `TB-304`
  - **Est. Effort:** 2 hours
  - **Acceptance Criteria:**
    - Uses `ffprobe` to inspect output MP4 and returns structured validation report:
      - Validates video codec is `h264`.
      - Validates dimensions are exactly `1080` width and `1920` height.
      - Validates aspect ratio evaluates to `9:16`.
      - Validates framerate is `30.0`.
      - Validates audio stream is present and encoded with `aac`.
      - Validates total duration is between 25.0 and 35.0 seconds.
      - Validates file size is under 50 MB (safe headroom below Meta's 100MB limit).
    - Throws `InvalidMediaFormatException` with detailed diagnostic breakdown if any assertion fails.
  - **Verification:** Unit test passes against valid MP4; fails when fed invalid/corrupt video test files.

---

- [ ] ### `TB-306` Video Rendering Integration & Performance Test
  - **Module / Files:**
    - `trendbharat/render/pipeline.py`
    - `tests/test_render.py`
  - **Prerequisites:** `TB-301`, `TB-302`, `TB-303`, `TB-304`, `TB-305`
  - **Est. Effort:** 2.5 hours
  - **Acceptance Criteria:**
    - `render_daily_reel(trends, run_date)` handles card rendering, compilation, validation, and returns `VideoArtifact(mp4_path, caption, cover_path)`.
    - Cleans up temporary PNG cards after compilation to avoid runner disk bloat.
    - Full render pipeline completes within 90 seconds on Ubuntu/Windows environments.
  - **Verification:** `pytest tests/test_render.py -v` executes complete render pipeline and validates output file.

---

## Phase 4: Instagram Graph API & Resumable Media Publishing
**Target Window: Days 19–25 · Total Est: 14 Hours · Status: Blocked by Phase 3**

- [ ] ### `TB-401` Implement Instagram Graph API Core Client
  - **Module / Files:**
    - `trendbharat/publisher/instagram_client.py`
  - **Prerequisites:** `TB-004`, `TB-006`
  - **Est. Effort:** 2 hours
  - **Acceptance Criteria:**
    - Wraps Meta Graph API endpoints (`v21.0`) with typed error handling:
      - Handles `OAuthException` (code 190: token expired/invalid).
      - Handles rate limit errors (code 32, 4).
      - Implements exponential retry on HTTP 5xx errors.
    - Method `get_content_publishing_limit()` queries `GET /{ig_user_id}/content_publishing_limit`:
      - Asserts quota usage is below daily limit (100 posts/day).
      - Aborts and alerts if quota is exhausted.
  - **Verification:** `python -m trendbharat.publisher.instagram_client` logs valid quota usage from live Meta account.

---

- [ ] ### `TB-402` Implement Reel Container Creation & Resumable Uploader
  - **Module / Files:**
    - `trendbharat/publisher/reels_uploader.py`
  - **Prerequisites:** `TB-401`
  - **Est. Effort:** 3.5 hours
  - **Acceptance Criteria:**
    - Step 1 — Create Container:
      - Issues `POST /{ig_user_id}/media`:
        - `media_type=REELS`
        - `upload_type=resumable`
        - `caption={caption_text}`
        - `cover_url` (optional / cover frame)
      - Extracts returned container `id` and `upload_url`.
    - Step 2 — Resumable Binary Transfer:
      - Sends raw MP4 binary stream to `upload_url` via HTTP `POST`.
      - Required headers:
        - `Authorization: OAuth {access_token}`
        - `Offset: 0`
        - `Content-Length: {file_size}`
        - `Content-Type: application/octet-stream`
      - Handles chunked upload if file size exceeds 8MB.
  - **Verification:** Test upload against Meta Graph API returns HTTP 200 with container ready for processing.

---

- [ ] ### `TB-403` Implement Container Processing Status Polling Loop
  - **Module / Files:**
    - `trendbharat/publisher/status_poller.py`
  - **Prerequisites:** `TB-402`
  - **Est. Effort:** 2 hours
  - **Acceptance Criteria:**
    - Polls `GET /{container_id}?fields=status_code` periodically.
    - Polling interval: Every 20 seconds, maximum 15 iterations (5 minutes timeout).
    - Status handling:
      - `FINISHED`: Container encoded and ready for publish. Returns `True`.
      - `IN_PROGRESS`: Log progress and continue sleep loop.
      - `ERROR`: Raises `MediaProcessingFailedException` with server error details.
      - `EXPIRED`: Container timed out; signals clean retry.
  - **Verification:** Unit test with mocked responses verifies polling behavior across all status codes.

---

- [ ] ### `TB-404` Implement Media Publish Trigger & DB Record
  - **Module / Files:**
    - `trendbharat/publisher/publisher.py`
  - **Prerequisites:** `TB-403`, `TB-202`
  - **Est. Effort:** 2 hours
  - **Acceptance Criteria:**
    - Invokes `POST /{ig_user_id}/media_publish?creation_id={container_id}`.
    - Extracts returned `id` (permanent Instagram Media ID).
    - Updates SQLite `posts` table:
      - Sets `status='published'`.
      - Sets `ig_media_id={id}`.
      - Sets `published_at=CURRENT_TIMESTAMP`.
    - Builds public Reel URL: `https://www.instagram.com/reel/{media_id}`.
  - **Verification:** Publishing call succeeds and updates local DB record.

---

- [ ] ### `TB-405` Implement Automated Token Refresher
  - **Module / Files:**
    - `trendbharat/publisher/token_manager.py`
  - **Prerequisites:** `TB-401`
  - **Est. Effort:** 2 hours
  - **Acceptance Criteria:**
    - Tracks token age in SQLite or secret metadata.
    - If token age $\ge 30$ days (well ahead of 60-day expiry), calls:
      `GET https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token={token}`.
    - Stores refreshed token.
    - If running on GitHub Actions, triggers Telegram warning if token age $\ge 50$ days to prevent dead token lockouts.
  - **Verification:** Test refresh call against live long-lived token returns refreshed token with new 60-day lifespan.

---

- [ ] ### `TB-406` Publisher Integration & Staging Test
  - **Module / Files:**
    - `tests/test_publisher.py`
  - **Prerequisites:** `TB-401`, `TB-402`, `TB-403`, `TB-404`, `TB-405`
  - **Est. Effort:** 2.5 hours
  - **Acceptance Criteria:**
    - Complete mock integration test of the publisher module.
    - Verifies handling of:
      - Network timeout during upload.
      - Processing status failure.
      - Quota limit rejection.
  - **Verification:** `pytest tests/test_publisher.py -v` passes with all mocked platform scenarios.

---

### GATE 2: End-to-End Media Publishing Gate Check
- [ ] **Gate Evaluation Tasks:**
  1. Trigger full pipeline publish against private staging / test Instagram Creator account.
  2. Verify Reel appears in Instagram app feed within 3 minutes of upload.
  3. Verify video displays crisp 1080x1920 visuals, smooth 30fps transitions, readable Indic fonts, and correct audio playback.
  4. Verify caption contains full 9 trends and hook is visible before the fold.
  - **Gate Decision:** Formal sign-off to proceed to Phase 5 CI/CD integration.

---

## Phase 5: CI/CD Orchestration, Telemetry & Reliability
**Target Window: Days 26–28 · Total Est: 6 Hours · Status: Blocked by Gate 2**

- [ ] ### `TB-501` Build Unified Orchestrator CLI
  - **Module / Files:**
    - `trendbharat/scheduler/daily_runner.py`
  - **Prerequisites:** Gate 2 Pass
  - **Est. Effort:** 2 hours
  - **Acceptance Criteria:**
    - CLI entrypoint supporting standard arguments:
      - `--dry-run`: Ingests trends, writes DB, generates cards & MP4, runs validator, skips Instagram upload.
      - `--post-now`: Executes live production publish pipeline.
      - `--force-date YYYY-MM-DD`: Allows manual backfill/testing for specific calendar date.
    - Orchestration flow:
      1. Check idempotency for date.
      2. Ingest & clean trends.
      3. Render cards & compile video.
      4. Validate MP4 with `ffprobe`.
      5. Upload & publish to Instagram.
      6. Dispatch Telegram notification.
      7. Sync database to `data` branch.
    - Structured logging with Run ID, step timestamps, and clean exit codes (`0` = success, `1` = transient error, `2` = unrecoverable error).
  - **Verification:** `python -m trendbharat.scheduler.daily_runner --dry-run` executes all local stages in sequence.

---

- [ ] ### `TB-502` Implement Telegram Telemetry & Alert Dispatcher
  - **Module / Files:**
    - `trendbharat/alerts/telegram_notifier.py`
  - **Prerequisites:** `TB-005`
  - **Est. Effort:** 1.5 hours
  - **Acceptance Criteria:**
    - Success Card:
      - Sends Markdown formatted message with run duration, trends summary, top 3 trend queries, category breakdown, and direct link to the published Reel.
    - Failure Alert:
      - Sends alert with high-visibility emojis (`🚨`), failed module name (`collector`, `render`, `publisher`), error string, and truncated stack trace.
    - Implements timeout and fallback so telemetry failure never crashes the main pipeline.
  - **Verification:** Test triggers send formatted success and error cards to target Telegram chat.

---

- [ ] ### `TB-503` Configure GitHub Actions Daily Workflow
  - **Module / Files:**
    - `.github/workflows/daily_pipeline.yml`
  - **Prerequisites:** `TB-501`, `TB-502`, `TB-203`
  - **Est. Effort:** 1.5 hours
  - **Acceptance Criteria:**
    - Runner: `ubuntu-latest`.
    - Triggers: `workflow_dispatch` (primary) and `schedule: - cron: '0 13 * * *'` (backup).
    - Workflow Steps:
      1. Checkout code (`actions/checkout@v4`, `fetch-depth: 0`).
      2. Install FFmpeg: `sudo apt-get update && sudo apt-get install -y ffmpeg`.
      3. Setup Python 3.12 with pip cache.
      4. Install dependencies: `pip install -r requirements.txt`.
      5. Sync database from `data` branch.
      6. Run pipeline: `python -m trendbharat.scheduler.daily_runner --post-now`.
      7. Push updated `trendbharat.db` back to `data` branch.
      8. Ping Healthchecks.io heartbeat endpoint on success.
    - On failure: Uploads `run.log` and generated artifacts as GitHub workflow run artifacts for debugging.
  - **Verification:** Manual dispatch on GitHub Actions completes successfully in under 5 minutes.

---

- [ ] ### `TB-504` Setup Precision External Trigger & Heartbeat Monitor
  - **Module / Files:**
    - `docs/cron_heartbeat_setup.md`
  - **Prerequisites:** `TB-503`
  - **Est. Effort:** 1 hour
  - **Acceptance Criteria:**
    - Create free scheduled job on [cron-job.org](https://cron-job.org):
      - Schedule: Every day at **13:00 UTC (6:30 PM IST)**.
      - Target: `POST https://api.github.com/repos/{owner}/{repo}/actions/workflows/daily_pipeline.yml/dispatches`.
      - Headers: `Authorization: Bearer {GH_PAT}`, `Accept: application/vnd.github.v3+json`.
      - Payload: `{"ref": "main"}`.
    - Create free heartbeat monitor on [Healthchecks.io](https://healthchecks.io):
      - Expected schedule: Daily at 7:15 PM IST (grace period: 30 minutes).
      - Alert channels: Telegram / Email.
  - **Verification:** External cron triggers test workflow dispatch; Healthchecks.io registers heartbeat ping.

---

## Phase 6: Staging Simulation, 7-Day Shadow Run & Production Launch
**Target Window: Days 29–35 · Total Est: 10 Hours · Status: Blocked by Phase 5**

- [ ] ### `TB-601` Execute 7-Day Automated Shadow Run
  - **Module / Files:**
    - `.github/workflows/daily_pipeline.yml` (configured in `--dry-run` mode)
  - **Prerequisites:** Phase 5 Complete
  - **Est. Effort:** 3.5 hours (over 7 days)
  - **Acceptance Criteria:**
    - Pipeline runs autonomously every day at 6:30 PM IST for 7 consecutive days in `--dry-run` mode.
    - Output MP4 videos saved as GitHub workflow artifacts each day.
    - Inspect each day's video artifact:
      - Confirm all 9 trends are topical and clean.
      - Confirm zero font rendering artifacts across Indic scripts.
      - Confirm aspect ratio, audio stream, and duration.
    - Confirm zero manual interventions required.
  - **Verification:** 7/7 successful GitHub Actions runs logged on consecutive days.

---

- [ ] ### `TB-602` Conduct Failure Injection & Recovery Testing
  - **Module / Files:**
    - `tests/test_resilience.py`
  - **Prerequisites:** `TB-601`
  - **Est. Effort:** 2 hours
  - **Acceptance Criteria:**
    - Test Case 1: Ingest server timeout simulation -> pipeline retries 3x and sends Telegram alert.
    - Test Case 2: Corrupted video file simulation -> `validator.py` intercepts before upload.
    - Test Case 3: Re-running pipeline on same date -> detected as already posted and exits cleanly without duplicate.
    - Test Case 4: Emergency post delete script tested against test media ID.
  - **Verification:** All 4 failure scenarios handled gracefully with zero unhandled exceptions.

---

- [ ] ### `TB-603` Physical Device Visual Compliance Verification
  - **Module / Files:**
    - `docs/visual_qa_checklist.md`
  - **Prerequisites:** `TB-601`
  - **Est. Effort:** 1.5 hours
  - **Acceptance Criteria:**
    - Transfer rendered MP4 files to iOS (iPhone) and Android (Samsung/Pixel) devices.
    - Open within Instagram Reels preview screen:
      - Header clearance: Cover title visible below Instagram top chrome.
      - Bottom clearance: Trend card text not covered by Instagram caption or audio pill.
      - Right margin clearance: Like, Comment, and Share buttons do not obscure text.
      - High-contrast text legible under direct sunlight.
  - **Verification:** Visual QA checklist signed off with zero margin violations.

---

### GATE 3: Production Go-Live Gate Check
- [ ] **Gate Evaluation Tasks:**
  1. 7/7 consecutive shadow runs completed without errors.
  2. Average workflow execution time under 12 minutes (within 30-min window).
  3. Visual QA verified on physical iOS and Android devices.
  4. Zero-cost infrastructure confirmed ($0.00 spent across all platforms).
  5. Emergency delete runbook validated.
  - **Gate Decision:** Formal GO LIVE approval. Switch workflow argument to `--post-now`.

---

- [ ] ### `TB-604` Production Day 1 Live Post Execution
  - **Module / Files:**
    - Production Instagram Account
  - **Prerequisites:** Gate 3 Pass
  - **Est. Effort:** 1 hour (Day 35)
  - **Acceptance Criteria:**
    - 6:30 PM IST: External cron triggers live production workflow dispatch.
    - 6:42 PM IST: Trends collected, video compiled, container uploaded.
    - 7:00 PM IST: Reel published to live `@TrendBharat` Instagram profile.
    - 7:05 PM IST: Live post inspected on Instagram:
      - Video plays smoothly with audio.
      - Caption formatted with active hashtags and clean formatting.
      - Database records published post ID and execution timestamps.
      - Telegram sends success card.
  - **Verification:** Published Reel active on Instagram profile.

---

- [ ] ### `TB-605` 30-Day Operational Handover & Monitoring Playbook
  - **Module / Files:**
    - `docs/operational_runbook.md`
  - **Prerequisites:** `TB-604`
  - **Est. Effort:** 1 hour
  - **Acceptance Criteria:**
    - Standard operating procedure documented:
      - Daily health check: Review Telegram success card at 7:05 PM IST.
      - Day 30 / Day 50 token refresh checklist.
      - Handling Instagram API version deprecation notices.
      - Blocklist keyword maintenance guide.
  - **Verification:** Runbook saved in repository and ready for day-to-day operations.

