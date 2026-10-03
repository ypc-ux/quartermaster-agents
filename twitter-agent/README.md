# Twitter Agent — Quartermaster

Posts high-value tweets using Commander Frame triggers and the 207+ trigger matrix.

## Setup

```bash
pip install -r requirements.txt
```

## Draft mode (safety default)

The agent runs in **draft mode by default**: it generates content and writes the
queue, but never calls the Twitter API and never sleeps between items.

```bash
TWITTER_DRAFT=true python scripts/twitter_agent.py   # default: draft, no posting
TWITTER_DRAFT=false python scripts/twitter_agent.py  # live posting (requires keys)
```

## Environment Variables

```
TWITTER_DRAFT=true|false   # false enables live posting
TWITTER_BEARER_TOKEN=...
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...
```

## Run

```bash
python scripts/twitter_agent.py
```

## Config

- Max 50 tweets/day (configurable)
- Min 30min between tweets (only applies in live mode)
- Content pillars: agency_lessons, builder_mindset, marketing_teardown, fintech_stripe, systems_thinking, hustle_transparency, contrarian_take
- Queue persists to `queue.json`; the workflow commits it back so the daily cap holds across runs
