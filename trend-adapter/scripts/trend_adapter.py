#!/usr/bin/env python3
"""Trend Adapter — Quartermaster. Adapt trending topics to your brand voice."""

import json, random
from datetime import datetime
from pathlib import Path

TREND_SOURCES = ["twitter", "reddit", "hacker_news", "industry_news", "social_media"]

def fetch_trends(source="twitter", limit=10):
    """Fetch trending topics from a source."""
    # Simulated trends - in production, this would hit APIs
    trends = [
        {"topic": "AI automation in agencies", "volume": "high", "sentiment": "positive", "source": source},
        {"topic": "Remote work burnout", "volume": "medium", "sentiment": "negative", "source": source},
        {"topic": "No-code tools", "volume": "high", "sentiment": "positive", "source": source},
        {"topic": "Creator economy", "volume": "medium", "sentiment": "mixed", "source": source},
        {"topic": "Personal branding", "volume": "high", "sentiment": "positive", "source": source},
    ]
    return trends[:limit]

def adapt_trend(trend, brand_context, content_types=None):
    """Adapt a trend to your brand context across content types."""
    content_types = content_types or ["tweet", "blog_post", "email", "video_script"]
    
    adaptations = []
    for ctype in content_types:
        adaptation = {
            "content_type": ctype,
            "trend": trend["topic"],
            "angle": f"How {brand_context} relates to {trend['topic']}",
            "hook": f"Why {trend['topic']} matters for {brand_context}",
            "key_points": [
                f"What {trend['topic']} means for {brand_context}",
                "Common misconceptions",
                "Actionable takeaways",
                "Your unique perspective"
            ],
            "status": "drafted",
            "relevance_score": random.randint(7, 10)
        }
        adaptations.append(adaptation)
    
    return {
        "trend": trend,
        "brand_context": brand_context,
        "adaptations": adaptations,
        "adapted_at": datetime.now().isoformat()
    }

def score_adaptation(adaptation):
    """Score how well a trend adaptation fits the brand."""
    relevance = adaptation.get("relevance_score", 5)
    timeliness = 8 if adaptation["trend"]["volume"] == "high" else 6
    uniqueness = random.randint(6, 9)
    total = (relevance + timeliness + uniqueness) / 3
    
    return {
        "adaptation": adaptation,
        "scores": {
            "relevance": relevance,
            "timeliness": timeliness,
            "uniqueness": uniqueness,
            "total": round(total, 1)
        }
    }

def run(brand_context="agency owners", source="twitter", limit=5):
    """Fetch trends and adapt them to brand context."""
    print(f"[Trend Adapter] Fetching trends from {source}...")
    trends = fetch_trends(source, limit)
    
    print(f"[Trend Adapter] Adapting {len(trends)} trends for {brand_context}...")
    adapted = [adapt_trend(t, brand_context) for t in trends]
    scored = [score_adaptation(a) for a in adapted]
    
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    
    result = {
        "source": source,
        "brand_context": brand_context,
        "trends_adapted": adapted,
        "scores": scored,
        "top_adaptations": sorted(scored, key=lambda x: x["scores"]["total"], reverse=True)[:3],
        "adapted_at": datetime.now().isoformat()
    }
    
    out_path = out_dir / f"trend_adaptations_{datetime.now().strftime('%Y%m%d')}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"[Trend Adapter] Adapted {len(trends)} trends")
    print(f"  Top trend: {result['top_adaptations'][0]['adaptation']['trend']['topic']}")
    print(f"  Score: {result['top_adaptations'][0]['scores']['total']}/10")
    print(f"  Saved to: {out_path}")
    return result

if __name__ == "__main__":
    import sys
    brand = sys.argv[1] if len(sys.argv) > 1 else "agency owners"
    source = sys.argv[2] if len(sys.argv) > 2 else "twitter"
    run(brand, source)
