#!/usr/bin/env python3
"""Brand Vault Repurposer — one idea, every platform.

The feature that makes the Personal Brand Vault worth opening every morning:
take ONE business update, win, or feature and chop it into platform-native
content for X, Instagram, LinkedIn, TikTok, email, and blog. Plus 10 hooks
per idea and a content pillar balance check.

No API keys required — runs offline against templates + Commander Frame levers.
"""

import json, random
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "data"

PLATFORMS = ["x", "instagram", "linkedin", "tiktok", "email", "blog"]

# Content pillars for men under 25 on X + people who sell to them
PILLARS = {
    "ship": "Shipping fast — build in public, velocity, receipts",
    "money": "Making money — cash flow, offers, the actual numbers",
    "mind": "Builder mindset — discipline, focus, ignoring noise",
    "proof": "Proof — results, teardowns, before/after, case studies",
}


def generate_hooks(idea, n=10):
    """10 opening hooks, labelled by type. Under 10 words, speakable in 3 seconds."""
    short = idea.strip().rstrip(".")[:60]
    types = ["curiosity", "bold_statement", "story", "relatable", "question", "contrarian"]
    bank = {
        "curiosity": [f"Nobody talks about what happened after {short}."],
        "bold_statement": [f"{short}. Here's the part nobody posts."],
        "story": [f"Last week I {short.lower()}. It changed the math."],
        "relatable": [f"You're going to do {short.lower()} too. Here's how it goes."],
        "question": [f"What if {short.lower()} was the easy part?"],
        "contrarian": [f"Everyone says {short.lower()} is smart. It's not."],
    }
    hooks = []
    for i in range(n):
        t = types[i % len(types)]
        base = random.choice(bank[t])
        words = base.split()
        if len(words) > 10:
            base = " ".join(words[:10])
        hooks.append({"type": t, "hook": base, "words": len(base.split())})
    return hooks


def repurpose(idea, pillars=None, lesson=None):
    """Take ONE idea → platform-native pieces."""
    pillars = pillars or ["ship"]
    lesson = lesson or idea
    pillar = random.choice(pillars)
    return {
        "source_idea": idea,
        "pillar": pillar,
        "pillar_desc": PILLARS.get(pillar, ""),
        "created": datetime.now().isoformat(),
        "pieces": {
            "x": f"{idea}\n\n{lesson}\n\nBuild systems, not tasks.",
            "x_thread": [f"1/ {idea}", f"2/ {lesson}", "3/ Here's the exact play:", "4/ Ship it.", "5/ Follow for more."],
            "instagram": {"carousel": [f"Slide 1: {idea}", f"Slide 2: {lesson}", "Slide 3: The play", "Slide 4: The result", "Slide 5: CTA"], "caption": f"{idea}\n\n{lesson}\n\nSave this."},
            "linkedin": f"{idea}\n\nHere's what most people miss:\n\n{lesson}\n\nWhat would you add?",
            "tiktok": {"hook": generate_hooks(idea, 1)[0]["hook"], "beats": [idea, lesson, "The result"], "length": "45-60s"},
            "email": f"Subject: {idea[:40]}\n\n{lesson}\n\nWorth a look?",
            "blog": f"# {idea}\n\n## The situation\n{lesson}\n\n## Why it matters\n\tMost people stop here. Builders don't.\n\n## The play\n1. Do the thing\n2. Log the receipt\n3. Ship the next one",
        },
    }


def pillar_balance(recent_posts):
    """recent_posts = list of pillar keys. Flag a neglected pillar."""
    counts = {p: recent_posts.count(p) for p in PILLARS}
    total = len(recent_posts) or 1
    balance = {p: round(c / total * 100) for p, c in counts.items()}
    neglected = [p for p, c in counts.items() if c == 0]
    return {"counts": counts, "balance_pct": balance, "neglected": neglected,
            "flag": f"Neglecting: {', '.join(neglected)}" if neglected else "Balanced."}


def run(idea):
    out = repurpose(idea)
    hooks = generate_hooks(idea, 10)
    out["hooks"] = hooks
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DIR / "repurposed.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"[Brand Vault] Repurposed 1 idea -> {len(PLATFORMS)} platforms")
    for h in hooks[:5]:
        print(f"  [{h['type']:14}] {h['hook']}")
    return out


if __name__ == "__main__":
    run("shipped 20 connected agents in 12 hours")
