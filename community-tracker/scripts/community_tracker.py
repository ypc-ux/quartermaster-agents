#!/usr/bin/env python3
"""Community Tracker — Quartermaster. Track community engagement and growth."""

import json
from datetime import datetime
from pathlib import Path

PLATFORMS = ["discord", "slack", "twitter", "linkedin", "reddit", "facebook_group"]

def track_engagement(platform, metrics):
    """Track engagement metrics for a platform."""
    return {
        "platform": platform,
        "tracked_at": datetime.now().isoformat(),
        "metrics": metrics,
        "trends": {
            "member_growth_rate": "[calculate from historical]",
            "engagement_rate": "[calculate from historical]",
            "top_posts": []
        }
    }

def track_top_members(platform, members, period="7d"):
    """Track top contributing members."""
    tracked = []
    for member in members:
        tracked.append({
            "member": member["name"],
            "contributions": member.get("contributions", 0),
            "engagement_score": member.get("score", 0),
            "period": period,
            "platform": platform,
            "recognized_at": datetime.now().isoformat()
        })
    return tracked

def generate_community_report(community_data):
    """Generate a community health report."""
    total_members = sum(c.get("metrics", {}).get("total_members", 0) for c in community_data)
    total_posts = sum(c.get("metrics", {}).get("posts_this_week", 0) for c in community_data)
    total_comments = sum(c.get("metrics", {}).get("comments_this_week", 0) for c in community_data)
    
    engagement_rate = (total_posts + total_comments) / max(total_members, 1) * 100
    
    return {
        "generated_at": datetime.now().isoformat(),
        "platforms_tracked": len(community_data),
        "total_members": total_members,
        "weekly_activity": {
            "posts": total_posts,
            "comments": total_comments,
            "engagement_rate_pct": round(engagement_rate, 2)
        },
        "health_score": min(100, int(engagement_rate * 10)),
        "insights": [
            "Engagement is healthy" if engagement_rate > 5 else "Engagement needs attention",
            f"Tracking {len(community_data)} platforms",
            f"{total_members} total community members"
        ]
    }

def run():
    """Demo: track community engagement and generate report."""
    print("[Community Tracker] Tracking community engagement...")
    
    community_data = [
        track_engagement("discord", {
            "total_members": 500,
            "active_members": 150,
            "posts_this_week": 45,
            "comments_this_week": 230,
            "new_members": 25
        }),
        track_engagement("twitter", {
            "total_followers": 14000,
            "posts_this_week": 35,
            "likes_this_week": 450,
            "replies_this_week": 120,
            "retweets_this_week": 80
        }),
        track_engagement("slack", {
            "total_members": 200,
            "active_members": 80,
            "messages_this_week": 180
        })
    ]
    
    report = generate_community_report(community_data)
    
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    
    result = {
        "community_data": community_data,
        "report": report,
        "updated_at": datetime.now().isoformat()
    }
    
    out_path = out_dir / "community_report.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"[Community Tracker] Community report:")
    print(f"  Platforms: {report['platforms_tracked']}")
    print(f"  Total members: {report['total_members']:,}")
    print(f"  Weekly posts: {report['weekly_activity']['posts']}")
    print(f"  Weekly comments: {report['weekly_activity']['comments']}")
    print(f"  Engagement rate: {report['weekly_activity']['engagement_rate_pct']}%")
    print(f"  Health score: {report['health_score']}/100")
    print(f"  Saved to: {out_path}")
    return result

if __name__ == "__main__":
    run()
