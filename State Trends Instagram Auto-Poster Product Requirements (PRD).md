# TrendBharat: Product Requirements (PRD)

Oct 30, 2026 · @Shubham Chaudhary

## 1. Product overview

TrendBharat finds what India is searching for today, turns the top trends into a ready-made Instagram Reel, and publishes it automatically at a fixed time every day.

**Problem.** Trend pages are hard to follow, and making a daily "what India is searching" post by hand takes hours.

**Solution.** A scheduled pipeline: collect trends, rank them, render the video and caption, publish through the official Instagram API, and log the result.

**Who it is for.** A single page owner running a news or trends Instagram account. Multi-account support comes later.

**Assumptions in this draft** (change any of them):

- "Trending" means the top trending searches on Google across India as a whole, not by state.
- The source is Google's free Trending now RSS feed for India, which carries about 10 trends.
- One run per day at a fixed time in IST, published to one Instagram professional account.
- Format is one Reel per day: a vertical 9:16 video of about 30 seconds that counts down India's top 9 trends.
- Zero cost: every component uses a free public feed, a free tier or open-source software.

## 2. Goals, non-goals and success metrics

The MVP succeeds if it posts correctly every day for 30 days without you touching it.

**Goals**

- Collect India's top trending searches daily with no manual step.
- Generate a clean, readable vertical video and caption automatically.
- Publish at the same time every day (for example 7:00 PM IST).
- Retry on failure and alert you when a post does not go out.
- Run for $0 a month, using only free feeds, free tiers and open-source libraries.

**Non-goals for v1**

- Multiple Instagram accounts or a customer-facing dashboard.
- Stories, Reels or video.
- Comment replies, DMs or analytics beyond basic logging.
- Regional-language captions (planned for v2).

| Metric | Target for the first 30 days |
| --- | --- |
| Days posted on schedule | 30 of 30 |
| Trend cards shown per run | 9 of 9 |
| Failed runs that auto-recover | 90% or more |
| Manual interventions | 0 per week |
| Time from trigger to published post | under 15 minutes |
| Monthly running cost | $0 |

## 3. User stories and features

The MVP is seven features; everything else waits until the daily post is stable.

**User stories**

- As the page owner, I want trends fetched automatically so I never open Google Trends myself.
- As the page owner, I want to preview or approve a post before it goes live (optional switch).
- As the page owner, I want a message on Telegram or email if a post fails.
- As a follower, I want a clear, good-looking post that shows what India is searching today.

| Feature | What it does | Phase |
| --- | --- | --- |
| Trend collector | Gets India's top trending searches every day | MVP |
| Cleaner and ranker | Removes duplicates and unsafe topics, keeps the top 9, tags each by category | MVP |
| Video generator | Renders a 9:16 video from trend cards (rank, trend, category, date) using free FFmpeg | MVP |
| Caption builder | Writes caption and hashtags from a fixed template | MVP |
| Publisher | Uploads the video and posts the Reel via Instagram API | MVP |
| Scheduler | Runs the job at a fixed time in IST | MVP |
| Logs and alerts | Stores every run and notifies on failure | MVP |
| Approval mode | Holds the post until you tap approve | v1.1 |
| AI-written captions | Short, natural caption per post using an LLM | v1.1 |
| Regional languages | Hindi and other captions | v2 |
| Dashboard and analytics | Reach, likes, best posting time | v2 |
| Audio | No music, or a royalty-free track whose license you checked | MVP |
| Carousel version | Same trends as a saveable carousel next to the Reel | v1.1 |

## 4. Post format, niche and content rules

Publish one Reel a day: about 30 seconds, vertical (9:16), counting down India's top 9 trending searches from number 9 to number 1. The free Trends feed carries about 10 trends, so one Reel uses nearly everything it provides.

| Option | What it means | Verdict |
| --- | --- | --- |
| Daily Reel: cover card + 9 trend cards, about 30 seconds | Reels reach more people who do not follow you yet | Recommended first |
| Daily carousel | Carousels earn more saves | Add in v1.1 from the same trends |
| Reel and carousel every day | Same trends in two formats | Good once the Reel runs without fixes |
| One post per trend | 9 or 10 posts a day | Floods followers and looks like spam |

**Which niche to pick**

Nobody can promise a viral niche, and the evidence here shows what India searches, not what goes viral on Instagram. Google's [India Year in Search 2025](https://www.businesstoday.in/latest/trends/story/googles-2025-search-trends-operation-sindoor-saiyaara-dharmendras-death-heres-what-captured-indias-attention-this-year-505034-2025-12-04) pointed to sports, AI, travel and entertainment, with sports-event searches led by [the IPL, Asia Cup and ICC events](https://t2online.in/tech/tech-news/google-s-year-in-search-2025--india-s-biggest-questions--trends-and-viral-moments-revealed/2002546) and tech searches led by [AI tools such as Gemini, DeepSeek and ChatGPT](https://currentaffairs.adda247.com/google-2025-top-searches-by-indian-users-this-year). Google's [Trending now page](https://trends.google.com/trending?category=14&geo=IN) also filters by category, including Sports, Entertainment, Technology, Business and Finance, and Jobs and Education.

| Niche | Why it fits a daily trend post | Watch out for | My rating |
| --- | --- | --- | --- |
| Cricket and sports | Cricket leads India's sports searches and spikes around matches, so there is almost always something new | Match photos are copyrighted, so use text-only slides | Best for reach |
| Entertainment (films, OTT, music) | Films and shows are a major search driver, for example Saiyaara, Kantara and Coolie in 2025 | Celebrity gossip and deaths can imply facts; skip personal-life trends | Best for shares |
| Technology and AI | Indians search AI tools heavily, and short explainers suit saving | A bare tool name is not useful; add a one-line meaning | Best for saves |
| Business and finance (gold, IPOs, markets) | Frequent daily trends that people bookmark | Anything that sounds like advice carries risk; say "searched", not "buy" | Add in phase 2 |
| Jobs and education (results, exams, vacancies) | A Google trend category with a large Indian audience (my judgment) | Spikes are seasonal; check dates before posting | Seasonal |
| Politics and crime | Many searches | Highest legal and platform risk | Avoid at launch |

**My pick.** Launch as a general "India Trending Today" page, tag every trend by category, and after 30 days check Instagram Insights for which categories earn the most saves and shares. Then narrow the page to the winner. Choosing one niche on day 1 would be a guess; the first month gives you data. If you want a single niche now, start with cricket and sports for reach, or tech and AI for saves.

**Why Reel first.** Reels reach far more people than carousels (one [analysis](https://www.tryordinal.com/blog/carousel-posts) puts it at 3.5 times the reach), while carousels earn more saves. A new page needs followers before it needs saves, so lead with the Reel and add the carousel from the same trends in v1.1.

| Slide | Content |
| --- | --- |
| Cover | Title such as "What India is searching today" and the date |
| Trend card | Rank number (9 to 1), the trend in large text, a category label, and approximate volume; about 3 seconds each |
| Footer on every card | Your handle, the date, and "Source: Google Trends" |

**Content rules**

- Show trends as what people searched, never as confirmed news.
- Skip topics on a blocklist (adult content, violence, hate, deaths) and use the next-ranked trend.
- If the feed returns fewer than 9 trends, publish a shorter Reel rather than padding it.
- Add alt text to every slide, and keep the hook in the first 125 characters of the caption.
- Use no music, or a royalty-free track whose license you checked; Instagram's own audio library cannot be attached with the login method used here.

## 5. Roadmap

Expect about five weeks of part-time work (my estimate, assuming 1 to 2 hours a day), with a go or no-go gate after phases 1 and 3, and after the first month live.

&#91;embedded content: build roadmap · 5 phases, 3 gates\]

If the feed returns fewer than 9 trends, publish a shorter Reel instead of delaying the build. Start the Meta app setup and the official Trends API application on day 1, since approvals can take time.

## 6. Risks and policy considerations

The biggest risks are not technical: they are the data source's terms and what a trending search can imply once it is on your page. Likelihood and impact are my own estimates.

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Google's Trends RSS feed is public but unofficial, so Google could change or block it | Medium | High | Request each feed once a day, apply for the official Trends API alpha, and keep the data source in one module so it can be swapped |
| A trend names a person tied to a crime, death or scandal and implies guilt | High | High | Keyword and name blocklist, approval mode, caption wording "searched", never "did" |
| Offensive, adult or communal topics reach the post | High | High | Blocklist plus fallback to the next-ranked trend; hold the slide if all top 5 are blocked |
| An unlicensed music track gets the Reel muted or flagged | Medium | Medium | Post with no music, your own audio, or a track whose license you checked (for example from the YouTube Audio Library) |
| Meta changes API versions, limits or permissions | Medium | Medium | Pin the API version and keep the publisher in one module |
| Access token expires or leaks | Medium | High | Automated refresh, secrets manager, alert on refresh failure |
| Trend data is relative or delayed | Medium | Low | Label as "trending search"; avoid exact numbers unless the source gives them |
| A post fails silently | Medium | Medium | Daily success summary and an external heartbeat check |
| Free data is thin (the feed carries only about 10 trends) | High | High | Check the feed in week 1; on thin days publish a shorter carousel, and apply for the official API for more data |
| Free tiers change, run late or ask for a card (GitHub schedule delays, storage limits) | Medium | Medium | Start runs with workflow\_dispatch from a free external cron, delete images after posting, and review each free tier's terms monthly |
| A rendered video fails Instagram's checks (codec, size or shape) | Medium | Medium | Check every file with ffprobe before upload and alert on failure |

**Policy checklist**

- Use only the official Instagram API for publishing; no unofficial login-based bots.
- Show "Source: Google Trends" on slides.
- Do not use other people's photos or logos in templates unless you own or license them.
- Read the data provider's terms and Meta's platform terms before going live, and take legal advice if you plan to run this commercially.

## 7. Zero-cost plan and open questions

The target is $0 a month: every part of the stack uses a free public feed, a free tier or open-source software. Free services come with no support and can change without notice, so the real cost is your time for fixes.

| Item | Cost | Free-tier detail and catch |
| --- | --- | --- |
| Trend data | $0 | Google's public Trends RSS feed for India; about 10 trends per feed |
| Scheduling and compute | $0 | GitHub Actions is free on public repos and gives 2,000 minutes a month on private ones ([source](https://thebiggish.pages.dev/news/github-actions-2-000-free-minutes-can-replace-your-20-month-cron-server)); a 10 to 15 minute daily run with video rendering (my estimate) uses 300 to 450 minutes |
| External trigger | $0 | A free cron service calls GitHub at the exact time; check that service's current free limits |
| Video rendering | $0 | FFmpeg and Pillow are free and open source; FFmpeg installs on a GitHub runner with apt-get |
| Video delivery | $0 | Upload straight to Instagram, so no hosting is needed; the fallback is Cloudflare R2's free tier (10 GB, [pricing](https://developers.cloudflare.com/r2/pricing/index.md)), which may ask for a card at sign-up |
| Audio | $0 | No music, or a royalty-free track you checked, for example from the YouTube Audio Library; no paid music |
| Database | $0 | SQLite file saved in the repository |
| Instagram API | $0 | Official API, no fee published in the docs reviewed |
| Alerts | $0 | Telegram bot |
| Fonts and libraries | $0 | Noto fonts, Pillow and requests are open source |

**Open questions (please decide)**

- [ ] Which niche do you want to lead with: cricket and sports, entertainment, tech and AI, or a general mix for the first 30 days?
- [ ] Do you want the carousel added in v1.1, so the same trends also earn saves?
- [ ] Posting time: is 7:00 PM IST right for your audience?
- [ ] Is the Instagram account already Business or Creator, and is it new or existing?
- [ ] English only, or Hindi and regional-language captions from the start?
- [ ] Do you want an approval step before each post goes live?
- [ ] Python or JavaScript for the build?
- [ ] What should the page be called, and do you have a logo or colours in mind?
- [ ] Should every slide show a category tag, so you can choose your niche from the data after 30 days?
- [ ] Music: no music, your own audio, or a royalty-free track?
