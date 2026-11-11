# TrendBharat: Technical Specification

Oct 30, 2026 · @Shubham Chaudhary

## 1. System architecture

A single scheduled job runs seven steps in order and logs each one. It collects India's top trending searches, builds one vertical Reel of about 30 seconds, and publishes it through Instagram's official API.

&#91;embedded content: pipeline architecture · 7 steps, 1 shared log\]

Steps 1 to 3 gather and clean the data, 4 and 5 make the post, and 6 and 7 publish it. Step 6 waits until Instagram finishes processing the video before it publishes.

## 2. Data sourcing: popular searches in India

Use Google's free public Trending now RSS feed instead of a paid scraper. Google's Trending now page itself offers [RSS and CSV export](https://support.google.com/trends/answer/3076011), and the feed needs no key, no account and no payment. Scraper tools describe it as [Google's public feed](https://apify.com/benthepythondev/google-trends-rss-scraper) that carries only about [10 trends per feed](https://apify.com/zahidthani/google-trends-trending-now.md). Google's official Trends API is still [an invite-only alpha](https://scrapegraphai.com/blog/google-trends-api), so it is not an option yet.

The feed for all of India is `https://trends.google.com/trending/rss?geo=IN`. It carries about 10 trends, which fits a cover slide plus 9 trend slides. Google's [Trending now page also filters by category](https://trends.google.com/trending?category=14&geo=IN), including Sports, Entertainment, Technology, and Business and Finance, but I could not confirm that the RSS feed accepts a category parameter, so test it in week 1. If it does not, tag each trend yourself with a small keyword list (for example team and player names for sports) and keep a category label on every slide.

| Option | Cost | Reliability | Verdict |
| --- | --- | --- | --- |
| Google Trends RSS feed with `geo=IN` | Free | Public feed with about 10 trends | Use for MVP |
| Same feed with a category filter, if supported | Free | Untested; would allow a single-niche page | Test in week 1 |
| Open-source RSS wrappers such as `trendspyg` ([listing](https://tomevault.io/tome/flack0x/trendspyg)) | Free | Wrap the same feed; check that the library is maintained | Optional shortcut |
| Official Google Trends API (alpha) | Not published | Best, but invite-only | Apply now, switch later |
| Unofficial `pytrends` or browser scraping | Free | Often blocked with 429 errors | Avoid |
| Paid scraper APIs | Paid | Good | Out of scope under the zero-cost rule |

**Rules for the data step**

- Fetch the India feed once a day, shortly before posting time.
- Keep the top 9 trends by approximate traffic (feed order if no traffic is given); hold any extras as backups.
- Tag each trend with a category so you can compare categories later.
- Skip a topic if it matches a blocklist (adult, violence, hate, deaths, crime) and use the next one.
- If fewer than 9 usable trends remain, publish a shorter carousel.
- Save the raw feed in the database so every post can be audited later.

## 3. Tech stack

Everything runs on free tiers: Python on GitHub Actions, Google's free RSS feed, free image hosting and a Telegram bot. The trade-off is less certainty, because free services have no support and can change without notice.

| Layer | Recommended (free) | Why | Alternative |
| --- | --- | --- | --- |
| Language | Python 3.12 | Free libraries for data and images (`requests`, `feedparser`, `Pillow`) | Node.js with TypeScript |
| Trend data | Google Trends RSS feed | Free, no key or account | Official Trends API once approved |
| Scheduler and compute | GitHub Actions, started at the exact time by a free external cron service that calls `workflow_dispatch` | GitHub's own `schedule` trigger can run hours late; Actions is free on public repos and gives 2,000 minutes a month on private ones ([source](https://thebiggish.pages.dev/news/github-actions-2-000-free-minutes-can-replace-your-20-month-cron-server)) | A cron job on your own always-on PC or Raspberry Pi |
| Card images | `Pillow` drawing each card as a 1080 x 1920 PNG | Simple, fast, no browser needed | HTML template rendered by Playwright |
| Video | FFmpeg joins the cards into an H.264 MP4 with AAC audio | Free and open source; it [installs on a GitHub runner with apt-get](https://skills.cat/skills/josiahsiegel/claude-plugin-marketplace/ffmpeg-cicd-runners) | MoviePy (a Python wrapper around FFmpeg) |
| Fonts | Noto Sans plus Noto Sans Devanagari, Tamil, Bengali and other Indic scripts | Trends often contain Hindi and regional text; missing fonts show empty boxes | Google Fonts equivalents |
| Audio | No music, or a royalty-free track whose license you checked (for example from the YouTube Audio Library, which one guide describes as free for commercial use) | Unlicensed music can get a Reel muted or flagged | Your own recording |
| Video delivery | Direct resumable upload to Instagram | Meta's API accepts the file itself, so no hosting is needed ([Meta docs](https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media)) | A public video URL on Cloudflare R2's free tier or GitHub Pages |
| Database | SQLite file committed to a `data` branch after each run | GitHub's runners start empty every time, so state must be saved somewhere free | A free-tier hosted Postgres (check its limits) |
| Alerts | Telegram bot | Free and instant | Email from a free mailbox |
| Secrets | GitHub Actions encrypted secrets | Free and kept out of the code | A local `.env` file when running on your own PC |
| Dashboard | None in v1 | Logs and Telegram messages are enough | A static page on GitHub Pages later |

**Project layout (suggested)**

```
trendbharat/
  collector/     fetch and clean trends
  render/        card templates, fonts, video output
  publisher/     Instagram API client, token refresh
  scheduler/     daily job entry point
  db/            models and migrations
  config/        blocklist, categories, schedule time
  tests/
```

## 4. Video and caption generation

The renderer turns the selected trends into one vertical MP4: a cover card plus 9 trend cards, counting down from 9 to 1.

| Slide | Content |
| --- | --- |
| Cover | Title such as "What India is searching today" and the date |
| Trend card | Rank number, the trend in large text, a category label, optional approximate volume; about 3 seconds each |
| Footer on every card | Handle, date, "Source: Google Trends" |

**Rendering rules**

- Output a 1080 x 1920 (9:16) MP4 at 30 frames per second, with H.264 video and AAC audio, about 30 seconds long and under 100 MB.
- Auto-fit the trend text: shrink the font until it fits in two lines, then cut with an ellipsis.
- One colour theme, high contrast, 80 px margins from the edges, and extra room at the bottom for Instagram's caption and buttons.
- Fall back to Indic-script fonts so Hindi, Tamil, Bengali and similar text renders correctly.
- Alt text is not supported on Reels through the API, so also write the trend names in the caption.
- Save each rendered card as a PNG and keep its file path in the `slides` table.
- After the Reel is confirmed live, delete the video and card files from the runner; nothing is stored long term.
- Join the cards with FFmpeg, about 3 seconds per card with short crossfades, and check the file with `ffprobe` (codec, size, 9:16 shape) before uploading.
- Audio: use no music, or a royalty-free track whose license you checked. The [Instagram Audio API](https://developers.facebook.com/documentation/instagram-platform/content-publishing/audio-api) that attaches Instagram's own library works only with Facebook Login, not the Instagram Login used here.

**Caption template**

```
What is India searching today? Watch the top 9 countdown. ({date})

Top searches from Google Trends.

Follow @{handle} for a daily update.

#trending #india #googletrends #{category_hashtag}
```

Put the hook in the first line, because only the first 125 characters show before "more".

## 5. Instagram publishing

Publish through Meta's official Instagram API with Instagram Login, which works with a Business or Creator account and, in this setup, [needs no Facebook Page](https://developers.facebook.com/documentation/instagram-platform/overview). A personal account cannot post through the API.

**One-time setup**

1. Switch your Instagram account to Professional (Business or Creator) in Settings.
2. Create an app at developers.facebook.com (type Business) and add the Instagram API with Instagram Login product.
3. Request two permissions: `instagram_business_basic` and `instagram_business_content_publish`.
4. Add your account to the app, generate an access token, and exchange it for a long-lived token.
5. Store the token as a secret and refresh it automatically: it [lasts 60 days and can be refreshed once it is at least 24 hours old](https://bundle.social/blog/instagram-graph-api); a token left unrefreshed past day 60 is dead and you must log in again.

Because the app only serves your own account, [Standard Access should be enough](https://developers.facebook.com/documentation/instagram-platform/overview) with no app review for Advanced Access. Confirm this in your Meta dashboard.

**Publishing a Reel (what the code does)**

1. Create a Reel container (media type REELS) with the caption and a cover image, and start a resumable upload.
2. Upload the MP4 to that container, or give Instagram a public video URL instead.
3. Poll the container's `status_code` until it says it is ready.
4. Call `media_publish` on the container.
5. Save the returned media ID in the database.

| Limit | Value | Source and note |
| --- | --- | --- |
| Posts per account per 24 hours | 100 API-published posts, a Reel counts as one | [Meta docs](https://developers.facebook.com/documentation/instagram-platform/content-publishing). The same page also mentions 50 in the carousel section, so call `content_publishing_limit` to check your real number |
| Video format | MP4 or MOV; H.264 or HEVC video, AAC audio, 23 to 60 frames per second | [Meta docs](https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media) |
| Shape | 9:16 recommended, up to 1920 pixels wide | Same Meta page; other shapes get cropped or padded |
| Length | 3 seconds to 15 minutes accepted; 5 to 90 seconds in 9:16 for the Reels tab | [Third-party guide](https://postproxy.dev/blog/instagram-reels-api-publishing-guide/); aim for about 30 seconds |
| File size | Meta's reference says up to 300 MB, one guide says 100 MB | Keep the file under 100 MB to be safe |
| Cover | Optional JPEG up to 8 MB, 9:16 recommended | Meta docs |
| Processing time | Meta suggests polling once a minute for up to 5 minutes | Most Reels finish in 30 seconds to 2 minutes, per the third-party guide |
| Caption | First 125 characters show before "more" | Put the hook there ([source](https://docs.zernio.com/platforms/instagram)) |
| Alt text | Added for image posts only; not supported on Reels | [Meta docs](https://developers.facebook.com/documentation/instagram-platform/content-publishing) |

## 6. Scheduler and reliability

Start the work 30 minutes before the posting time, so a slow or failed step still leaves time to retry and publish on schedule.

**Example daily run (7:00 PM IST posting time)**

1. 6:30 PM: the external trigger starts the workflow; collect India's trends and save the raw data.
2. 6:40 PM: clean, rank and keep the top 9 trends.
3. 6:45 PM: render the cards and the 30-second video, and check the file with ffprobe.
4. 7:00 PM: upload the Reel and publish it once Instagram finishes processing.
5. 7:15 PM: verify the post exists, then send a success summary.

Trigger the workflow at 6:30 PM IST (13:00 UTC) with a free external cron service that calls GitHub's `workflow_dispatch` endpoint, using a token limited to this repository. GitHub's own `schedule` trigger is best-effort: [community reports from October 2026](https://github.com/orgs/community/discussions/210625) describe runs starting hours late, and [another report](https://github.com/orgs/community/discussions/207370) says `workflow_dispatch` on the same workflows worked normally. If you have a PC or Raspberry Pi that stays on, a local cron job (`0 13 * * *`, in UTC) is an equally free option.

| What can go wrong | How the app handles it |
| --- | --- |
| Trend feed is down or returns empty data | Retry 3 times with waiting between tries; if still empty, skip the day and alert you (never post yesterday's trends as today's) |
| The feed returns fewer than 9 usable trends | Use the backup trends; if still short, publish a shorter carousel |
| Instagram video processing is slow | Poll about once a minute for up to 5 minutes, as Meta suggests, then retry the upload |
| Publish call fails | Retry with backoff; before retrying, check the database so the same post is never published twice |
| Daily publishing limit reached | Read `content_publishing_limit` before publishing; stop and alert if there is no room |
| Access token near expiry | A monthly job refreshes it and rewrites the GitHub secret through the GitHub API; if that is too fiddly, refresh by hand every 50 days with a calendar reminder. Alert if refresh fails, because a dead token needs a manual login |
| The whole job never started | An external heartbeat check pages you if no "run finished" ping arrives by a set time |
| Bad or unsafe trend slips through | Blocklist plus optional approval mode (v1.1), and a "delete post" runbook |
| GitHub starts the workflow late or not at all | Start it with workflow\_dispatch from an external cron, begin 30 minutes before posting time, and let the heartbeat check alert you if it never ran |
| Instagram rejects the video (codec, size or shape) | Check the file with ffprobe before uploading; on failure send you the error and keep the MP4 on the runner for that run so you can inspect it |

**Rules that keep it safe**

- Idempotent runs: one row per date and post; a rerun resumes, it does not duplicate.
- Every external call has a timeout and structured logs with a run ID.
- A manual "post now" and "dry run" command exist from day one, so you can test without publishing.

## 7. Database schema

Four tables cover everything the MVP needs: each daily run, the trends collected, and the day's Reel post with its cards.

| Table | Holds | Key rule |
| --- | --- | --- |
| `runs` | One row per day with status and errors | `run_date` is unique, so a day runs once |
| `trends` | Trends per run with category, blocked and selected flags, and the raw response | Keeps the next-ranked backups |
| `posts` | The day's Reel with caption, status, Instagram IDs, file size and attempts | One per run |
| `slides` | Each card's position, trend and image file path | Ordered within the post |

```sql
CREATE TABLE runs (
  id INTEGER PRIMARY KEY,
  run_date DATE NOT NULL UNIQUE,
  status TEXT NOT NULL,           -- started, collected, rendered, published, failed
  started_at TIMESTAMP,
  finished_at TIMESTAMP,
  error TEXT
);

CREATE TABLE trends (
  id INTEGER PRIMARY KEY,
  run_id INT NOT NULL REFERENCES runs(id),
  rank INT NOT NULL,
  query TEXT NOT NULL,
  category TEXT,                  -- sports, entertainment, technology, business, other
  approx_volume INT,
  blocked BOOLEAN DEFAULT FALSE,
  selected BOOLEAN DEFAULT FALSE,
  raw JSON
);

CREATE TABLE posts (
  id INTEGER PRIMARY KEY,
  run_id INT NOT NULL UNIQUE REFERENCES runs(id),
  caption TEXT,
  status TEXT NOT NULL,           -- pending, uploaded, processing, published, failed
  container_id TEXT,
  ig_media_id TEXT,
  video_bytes INT,
  attempts INT DEFAULT 0,
  published_at TIMESTAMP,
  error TEXT
);

CREATE TABLE slides (
  id INTEGER PRIMARY KEY,
  post_id INT NOT NULL REFERENCES posts(id),
  position INT NOT NULL,          -- 1 is the cover card
  trend_id INT REFERENCES trends(id),
  image_url TEXT NOT NULL         -- file path of the rendered card
);
```

Keep the Instagram access token out of these tables and out of the repo; store it as a GitHub Actions encrypted secret and record only its expiry date for the refresh job.

The SQLite file lives on a `data` branch and is committed after every run, because GitHub's runners start empty each time. That commit also keeps the repository active, since GitHub may pause scheduled workflows in repositories with no activity for 60 days.
