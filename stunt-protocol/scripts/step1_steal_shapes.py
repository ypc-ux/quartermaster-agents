#!/usr/bin/env python3
"""Stunt Protocol Engine — Step 1: Steal the Shape."""

import json, re, time
from pathlib import Path
from datetime import datetime

ARCHIVE_URL = "https://www.famouscampaigns.com/wp-json/wp/v2/posts"
OUTPUT_DIR = Path(__file__).parent.parent / "data"

STUNT_SHAPES = [
    {"id": "stunt-001", "shape": "Buy the thing nobody thought was for sale, then sell it back.", "mechanic": "Purchase an unexpected asset, create scarcity, resell.", "why_covered": "Subverts ownership expectations."},
    {"id": "stunt-002", "shape": "Turn a limitation into the entire product.", "mechanic": "Take a constraint and make it the feature.", "why_covered": "Reveals product capability through extreme demonstration."},
    {"id": "stunt-003", "shape": "Do publicly what others do in private.", "mechanic": "Make a private industry practice visible.", "why_covered": "Creates controversy + transparency narrative."},
    {"id": "stunt-004", "shape": "Set an impossible deadline, then hit it.", "mechanic": "Public commitment to extreme timeline, deliver.", "why_covered": "Human interest + proof of execution."},
    {"id": "stunt-005", "shape": "Give away the thing competitors charge for.", "mechanic": "Identify revenue source, make it free.", "why_covered": "Disrupts pricing expectations."},
    {"id": "stunt-006", "shape": "Hire the person nobody else would.", "mechanic": "Find unconventional talent, make them the face.", "why_covered": "Human story + underdog narrative."},
    {"id": "stunt-007", "shape": "Turn a bug into a feature.", "mechanic": "When something breaks, make it the product.", "why_covered": "Shows adaptability + humor."},
    {"id": "stunt-008", "shape": "Do it live — no edits, no safety net.", "mechanic": "Execute complex task in real-time, public.", "why_covered": "Risk + authenticity = compelling content."},
    {"id": "stunt-009", "shape": "Partner with your biggest competitor.", "mechanic": "Collaborate with rival on limited project.", "why_covered": "Unexpected alliance creates news."},
    {"id": "stunt-010", "shape": "Launch without telling anyone, let them discover it.", "mechanic": "Soft launch, let organic discovery drive narrative.", "why_covered": "Mystery + exclusivity drives coverage."},
    {"id": "stunt-011", "shape": "Price it at $0, let the market decide value.", "mechanic": "Pay-what-you-want or free with voluntary payment.", "why_covered": "Challenges pricing norms, generates data story."},
    {"id": "stunt-012", "shape": "Turn customer complaints into the product roadmap.", "mechanic": "Publicly address worst feedback, ship fixes live.", "why_covered": "Transparency + responsiveness narrative."},
    {"id": "stunt-013", "shape": "Buy a competitor's product and tear it apart.", "mechanic": "Public teardown of rival offering.", "why_covered": "Conflict + comparison drives engagement."},
    {"id": "stunt-014", "shape": "Make the terms of service the marketing.", "mechanic": "Write unusual ToS, make it public-facing.", "why_covered": "Humor + transparency, highly shareable."},
    {"id": "stunt-015", "shape": "Replace your logo with user-generated content.", "mechanic": "Let community create brand assets.", "why_covered": "Community ownership + UGC narrative."},
    {"id": "stunt-016", "shape": "Ship a feature in 24 hours, stream the whole thing.", "mechanic": "Live-build a requested feature under time pressure.", "why_covered": "Proof of velocity + transparency."},
    {"id": "stunt-017", "shape": "Turn a legal threat into a product launch.", "mechanic": "When threatened, turn it into marketing.", "why_covered": "David vs. Goliath narrative."},
    {"id": "stunt-018", "shape": "Give away equity to your users.", "mechanic": "Distribute ownership to early adopters.", "why_covered": "Radical ownership model."},
    {"id": "stunt-019", "shape": "Launch a product that makes your old product obsolete.", "mechanic": "Cannibalize yourself before someone else does.", "why_covered": "Shows confidence + innovation velocity."},
    {"id": "stunt-020", "shape": "Do a stunt so boring it becomes interesting.", "mechanic": "Take something mundane, do it at extreme scale.", "why_covered": "Absurdist humor + contrast creates virality."},
]

def fetch_archive():
    posts = []
    for page in range(1, 4):
        try:
            import urllib.request
            url = f"{ARCHIVE_URL}?per_page=100&page={page}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                posts.extend(data)
                print(f"[Stunt Protocol] Fetched page {page}: {len(data)} posts")
        except Exception as e:
            print(f"[Stunt Protocol] Error page {page}: {e}")
            break
        time.sleep(1)
    return posts

def run():
    print("[Stunt Protocol] Step 1: Steal the Shape")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    posts = fetch_archive()
    if posts:
        shapes = [{"source_url": p.get("link",""), "title": p.get("title",{}).get("rendered",""), "summary": re.sub(r"<[^>]+>","",p.get("content",{}).get("rendered",""))[:200], "date": p.get("date","")} for p in posts]
        with open(OUTPUT_DIR / "fetched_stunts.json", "w") as f:
            json.dump({"fetched": datetime.now().isoformat(), "count": len(shapes), "shapes": shapes}, f, indent=2)
        print(f"[Stunt Protocol] Saved {len(shapes)} fetched stunts")
    with open(OUTPUT_DIR / "stunt_shapes.json", "w") as f:
        json.dump(STUNT_SHAPES, f, indent=2)
    print(f"[Stunt Protocol] Saved {len(STUNT_SHAPES)} curated shapes")
    return STUNT_SHAPES

if __name__ == "__main__":
    run()
