# Twitter Agent — Quartermaster

Posts high-value tweets using Commander Frame triggers and the 207+ trigger matrix.

## Setup

```bash
pip install -r requirements.txt
```

## Environment Variables

```
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
- Min 30min between tweets
- Content pillars: agency_lessons, builder_mindset, marketing_teardown, fintech_stripe, systems_thinking, hustle_transparency, contrarian_take
