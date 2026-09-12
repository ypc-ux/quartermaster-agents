#!/usr/bin/env python3
"""Content Agent — Quartermaster. Generates content for all channels using Commander Frame."""

import json, random, time
from datetime import datetime
from pathlib import Path

CHANNELS = ["twitter", "email", "blog", "landing_page"]

TEMPLATES = {
    "twitter": {
        "hooks": [
            "8 years running an agency. Here's what nobody tells you:",
            "Your agency should run without you. Here's how:",
            "Saw this ad today. Here's why it's wasting money:",
            "Hot take: most agency advice is wrong. Here's why:",
            "Real talk: here's what I actually made running an agency.",
        ],
        "length": 280,
    },
    "email": {
        "hooks": [
            "Saw something in your space I had to share.",
            "Most {industry} owners make the same mistake. Here it is.",
            "Quick diagnostic: your {weakness} is costing you money.",
        ],
        "length": 500,
    },
    "blog": {
        "hooks": [
            "The Complete Guide to {topic} for Agency Owners",
            "How I {result} (And How You Can Too)",
            "Why Most {industry} Agencies Fail at {skill}",
        ],
        "length": 2000,
    },
}

def generate_content(channel, context=None):
    """Generate content for a specific channel."""
    ctx = context or {}
    industry = ctx.get("industry", "agency")
    topic = ctx.get("topic", "building systems")
    weakness = ctx.get("weakness", "marketing")
    result = ctx.get("result", "built an agency that runs itself")
    skill = ctx.get("skill", "scaling")
    
    template = TEMPLATES.get(channel, TEMPLATES["twitter"])
    hook = random.choice(template["hooks"]).format(**locals())
    
    if channel == "twitter":
        body = _generate_tweet_body(ctx)
        content = f"{hook}\n\n{body}"
    elif channel == "email":
        body = _generate_email_body(ctx)
        content = f"{hook}\n\n{body}"
    elif channel == "blog":
        body = _generate_blog_body(ctx)
        content = f"# {hook}\n\n{body}"
    else:
        content = hook
    
    return {
        "channel": channel,
        "hook": hook,
        "content": content[:template["length"]],
        "created": datetime.now().isoformat(),
        "status": "draft",
    }

def _generate_tweet_body(ctx):
    bodies = [
        "Build systems, not tasks. Tasks break. Systems scale.",
        "I don't do 1:1 calls anymore. Here's what replaced them.",
        "The best marketing doesn't feel like marketing. It feels like a diagnostic.",
        "Your offer is vague. Be specific. '$3K more MRR in 90 days' converts.",
        "Stop trading time for money. Start trading systems for scale.",
        "I ran my agency for 8 years. Best decision? Documenting every system.",
        "Fintech + agencies = the future. Payment infrastructure IS the moat.",
        "Most agency owners sell hours. I sell outcomes. That's the difference.",
    ]
    return random.choice(bodies)

def _generate_email_body(ctx):
    bodies = [
        "I've been running an agency for 8 years. Here's the #1 thing I see wrong with most {industry} businesses:\n\nNo documented systems.\n\nIf it's not written down, it doesn't exist. And if it doesn't exist, it doesn't scale.\n\nI built a framework for this. Happy to share if you're interested.",
        "Quick question: how much of your business runs without you touching it?\n\nIf the answer is 'not enough,' you're not alone. Most {industry} owners are the bottleneck.\n\nI built a system that fixed this for me. It's called Quartermaster. Happy to walk you through it.",
    ]
    return random.choice(bodies)

def _generate_blog_body(ctx):
    return """## Introduction

After 8 years of running an agency, I've learned one thing: **systems beat effort every time.**

## The Problem

Most agency owners are the business. If you stop working, revenue stops coming in.

## The Solution

Build operating systems. Document everything. Automate what you can. Delegate what you can't.

## The Framework

1. **Document** — Write down every process
2. **Automate** — Use tools to handle repetitive work
3. **Delegate** — Hire or build agents for execution
4. **Scale** — Systems compound, effort doesn't

## Conclusion

Your agency should run without you. That's not lazy — that's leverage."""

def run(channel="twitter", count=10):
    """Generate content and push to queue."""
    print(f"[Content Agent] Generating {count} {channel} pieces...")
    output = []
    for _ in range(count):
        c = generate_content(channel)
        output.append(c)
        print(f"  - {c['hook'][:60]}...")
    
    # Save to shared queue
    qp = Path(__file__).parent.parent / f"content_queue_{channel}.json"
    existing = json.load(open(qp)) if qp.exists() else []
    existing.extend(output)
    with open(qp, "w") as f:
        json.dump(existing, f, indent=2)
    
    print(f"[Content Agent] Saved {len(output)} items to {qp}")
    return output

if __name__ == "__main__":
    import sys
    ch = sys.argv[1] if len(sys.argv) > 1 else "twitter"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    run(ch, n)
