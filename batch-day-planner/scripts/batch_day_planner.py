#!/usr/bin/env python3
"""Batch Day Planner — Quartermaster. Plan batch content creation sessions."""

import json
from datetime import datetime, timedelta
from pathlib import Path

CONTENT_TYPES = ["blog_post", "video_script", "carousel", "tweet_thread", "email", "podcast_episode"]

def plan_batch_day(date=None, content_types=None, count_per_type=3):
    """Plan a batch content creation day."""
    date = date or datetime.now() + timedelta(days=7)
    if isinstance(date, str):
        date = datetime.fromisoformat(date)
    
    content_types = content_types or CONTENT_TYPES[:4]
    
    plan = {
        "batch_date": date.strftime("%Y-%m-%d"),
        "planned_at": datetime.now().isoformat(),
        "content_pieces": [],
        "total_pieces": 0,
        "estimated_time_hours": 0,
        "preparation_checklist": []
    }
    
    for ctype in content_types:
        for i in range(count_per_type):
            plan["content_pieces"].append({
                "type": ctype,
                "topic": f"[Topic {i+1} for {ctype}]",
                "status": "planned",
                "estimated_minutes": 60 if ctype in ["video_script", "blog_post"] else 30,
                "notes": ""
            })
    
    plan["total_pieces"] = len(plan["content_pieces"])
    plan["estimated_time_hours"] = sum(p["estimated_minutes"] for p in plan["content_pieces"]) / 60
    
    plan["preparation_checklist"] = [
        "Research topics and gather data",
        "Create outlines for each piece",
        "Prepare visuals/assets",
        "Set up recording environment (if video)",
        "Review brand guidelines and voice",
        "Schedule breaks between sessions"
    ]
    
    return plan

def run(date=None, content_types=None):
    """Generate a batch day plan."""
    print("[Batch Day Planner] Planning batch content day...")
    plan = plan_batch_day(date, content_types)
    
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    
    result = {
        "batch_plan": plan,
        "summary": {
            "date": plan["batch_date"],
            "total_pieces": plan["total_pieces"],
            "estimated_hours": round(plan["estimated_time_hours"], 1),
            "content_types": list(set(p["type"] for p in plan["content_pieces"]))
        }
    }
    
    out_path = out_dir / f"batch_plan_{plan['batch_date']}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"[Batch Day Planner] Batch day planned:")
    print(f"  Date: {plan['batch_date']}")
    print(f"  Content pieces: {plan['total_pieces']}")
    print(f"  Estimated time: {plan['estimated_time_hours']:.1f} hours")
    print(f"  Saved to: {out_path}")
    return result

if __name__ == "__main__":
    run()
