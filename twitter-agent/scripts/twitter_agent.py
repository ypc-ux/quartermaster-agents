#!/usr/bin/env python3
"""Twitter Agent — Quartermaster. Posts high-value tweets using Commander Frame triggers.

Safety: runs in DRAFT MODE by default. It generates content and records it, but
does NOT call the Twitter API. Set TWITTER_DRAFT=false to enable live posting.
"""

import json, os, random, time
from datetime import datetime
from pathlib import Path

MAX_TWEETS_PER_DAY = 50
MIN_TWEETS_PER_DAY = 10
MIN_INTERVAL_MINUTES = 30

# Draft mode: true unless explicitly disabled. Only post when the owner opts in.
DRAFT_MODE = os.getenv("TWITTER_DRAFT", "true").lower() not in ("false", "0", "no")

PILLARS = ["agency_lessons","builder_mindset","marketing_teardown","fintech_stripe","systems_thinking","hustle_transparency","contrarian_take"]

TRIGGER_HOOKS = {
    "agency_lessons": [
        "8 years running an agency. Here's what nobody tells you:",
        "I ran an agency for 8 years. Made every mistake so you don't have to:",
        "Agency owners: the real money isn't where you think.",
    ],
    "builder_mindset": [
        "Your agency should run without you touching it. Here's how:",
        "Build systems, not tasks. Tasks break. Systems scale.",
        "The best agency owners don't sell services. They sell operating systems.",
    ],
    "marketing_teardown": [
        "Saw this ad today. Here's why it's wasting money:",
        "Your copy is weak. Here's the diagnostic:",
        "Most marketing is theater. Here's how to tell:",
    ],
    "fintech_stripe": [
        "Stripe takes care of payments. But here's what they don't do:",
        "Fintech is the arena. Here's why agency owners should care:",
        "Payment infrastructure = invisible moat. Here's why:",
    ],
    "systems_thinking": [
        "An operating system > a business plan. Here's why:",
        "Every business runs on systems. Most just don't write them down.",
        "I built my own IDE for running an agency. Here's how:",
    ],
    "hustle_transparency": [
        "Real talk: here's what I actually made running an agency.",
        "I haven't made the most money. But here's what I gained:",
        "Transparency: 8 years, 14K followers, here's what I learned:",
    ],
    "contrarian_take": [
        "Hot take: most agency advice is wrong. Here's why:",
        "Unpopular opinion: you don't need more leads. You need:",
        "Everyone says niche down. I say the opposite. Here's why:",
    ],
}

LESSONS = [
    {"p": "I ran an agency for 8 years. Best decision? Building systems that ran without me.", "pillar": "agency_lessons"},
    {"p": "Stopped 1:1 calls. Replaced with booking link + voice agent. Revenue doubled.", "pillar": "systems_thinking"},
    {"p": "Traveled to 12 countries running my agency. The secret? No secret. Just systems.", "pillar": "hustle_transparency"},
    {"p": "14K Instagram followers. Zero viral posts. Just consistency + value + time.", "pillar": "hustle_transparency"},
    {"p": "Most agency owners sell hours. I sell outcomes. That's the difference.", "pillar": "builder_mindset"},
    {"p": "Stripe's real product isn't payments. It's trust infrastructure.", "pillar": "fintech_stripe"},
    {"p": "Your agency has 7 layers. Build them intentional or they build themselves wrong.", "pillar": "systems_thinking"},
    {"p": "I made every mistake. Hired wrong. Priced wrong. Niche wrong. Each taught me something.", "pillar": "agency_lessons"},
    {"p": "The best marketing doesn't feel like marketing. It feels like a diagnostic.", "pillar": "marketing_teardown"},
    {"p": "Fintech + agencies = the future. Payment infrastructure IS the moat.", "pillar": "fintech_stripe"},
]

TEARDOWNS = [
    "The headline is generic. No specific number. No clear outcome. Fix the headline, fix the conversion.",
    "No objection preemption. The #1 objection is right there and they're ignoring it.",
    "The offer is vague. 'Grow your business' isn't an offer. '$3K more MRR in 90 days' is.",
    "Social proof is missing or fake-looking. Real numbers > testimonials.",
    "The CTA is weak. 'Learn more' gets ignored. 'Book a 15-min diagnostic call' converts.",
]

CONTRARIAN = [
    "You don't need a personal brand. You need a portfolio of shipped work.",
    "Niche down is bad advice for agencies. Go wide, then let clients self-select.",
    "Cold email is overrated. Build something people want to find you for.",
    "You don't need more followers. You need the right 100 clients.",
]

def generate_tweet():
    """Generate a single tweet from content pillars + trigger hooks."""
    pillar = random.choice(PILLARS)
    hook = random.choice(TRIGGER_HOOKS.get(pillar, TRIGGER_HOOKS["agency_lessons"]))
    matching = [l for l in LESSONS if l["pillar"] == pillar]
    if not matching:
        matching = LESSONS
    lesson = random.choice(matching)

    if pillar == "marketing_teardown":
        tweet = f"{hook}\n\n{random.choice(['The problem: ','Issue: ','Diagnosis: '])}{random.choice(TEARDOWNS)}"
    elif pillar == "contrarian_take":
        tweet = f"{hook}\n\n{random.choice(CONTRARIAN)}"
    else:
        tweet = f"{hook}\n\n{lesson['p']}"
    return tweet

def get_queue():
    qp = Path(__file__).parent.parent / "queue.json"
    return json.load(open(qp)) if qp.exists() else []

def save_queue(queue):
    qp = Path(__file__).parent.parent / "queue.json"
    with open(qp, "w") as f:
        json.dump(queue, f, indent=2)

def post_tweet(text):
    """Post via Twitter API v2. Requires env vars. No-op in draft mode."""
    if DRAFT_MODE:
        print("[Twitter Agent] DRAFT MODE — not posting:", text[:60] + "...")
        return {"ok": False, "err": "draft_mode"}
    try:
        import tweepy
        client = tweepy.Client(
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
        )
        resp = client.create_tweet(text=text)
        tid = resp.data["id"]
        print(f"[Twitter Agent] Posted {tid}: {text[:50]}...")
        return {"ok": True, "id": tid}
    except ImportError:
        print("[Twitter Agent] tweepy not installed. pip install tweepy")
        return {"ok": False, "err": "no tweepy"}
    except Exception as e:
        print(f"[Twitter Agent] Error: {e}")
        return {"ok": False, "err": str(e)}

def run():
    print(f"[Twitter Agent] Starting {datetime.now().isoformat()}" + (" (DRAFT MODE)" if DRAFT_MODE else ""))
    queue = get_queue()

    if not queue:
        n = random.randint(MIN_TWEETS_PER_DAY, MAX_TWEETS_PER_DAY)
        print(f"[Twitter Agent] Generating {n} tweets...")
        for _ in range(n):
            queue.append({
                "id": f"t_{int(time.time())}_{random.randint(1000,9999)}",
                "text": generate_tweet(),
                "status": "pending",
                "created": datetime.now().isoformat(),
            })
        save_queue(queue)

    posted = sum(1 for t in queue if t.get("status") == "posted" and
                 datetime.fromisoformat(t.get("posted_at","2020-01-01")).date() == datetime.now().date())

    if posted >= MAX_TWEETS_PER_DAY:
        print(f"[Twitter Agent] Daily limit reached ({posted}/{MAX_TWEETS_PER_DAY})")
        return

    pending = [t for t in queue if t["status"] == "pending"]
    to_post = min(len(pending), MAX_TWEETS_PER_DAY - posted)
    print(f"[Twitter Agent] Posting {to_post}/{len(pending)}...")

    for i, t in enumerate(pending[:to_post]):
        if DRAFT_MODE:
            # Leave items pending so they can post once live mode is enabled.
            print(f"[Twitter Agent] DRAFT — would post: {t['text'][:60]}...")
            break
        r = post_tweet(t["text"])
        t["status"] = "posted" if r["ok"] else "failed"
        t["posted_at"] = datetime.now().isoformat()
        if r["ok"]:
            t["tweet_id"] = r["id"]
        save_queue(queue)
        if i < to_post - 1:
            delay = random.randint(MIN_INTERVAL_MINUTES * 60, (MIN_INTERVAL_MINUTES + 30) * 60)
            print(f"[Twitter Agent] Sleeping {delay}s...")
            time.sleep(delay)

    print(f"[Twitter Agent] Done. Posted today: {posted + to_post}")

if __name__ == "__main__":
    run()
