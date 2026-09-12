#!/usr/bin/env python3
"""Ops Digest — Quartermaster. Daily briefing that pulls from all agents."""

import json
from datetime import datetime
from pathlib import Path

def generate_digest(agent_statuses, metrics=None):
    """Generate a daily ops digest from all agent statuses."""
    metrics = metrics or {}
    
    digest = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "agents_active": sum(1 for a in agent_statuses if a.get("status") == "active"),
            "agents_total": len(agent_statuses),
            "total_tasks_completed": metrics.get("tasks_completed", 0),
            "revenue_today": metrics.get("revenue", 0),
            "new_leads": metrics.get("leads", 0)
        },
        "agent_updates": [],
        "alerts": [],
        "action_items": [],
        "wins": []
    }
    
    for agent in agent_statuses:
        update = {
            "agent": agent["name"],
            "status": agent.get("status", "unknown"),
            "last_run": agent.get("last_run", "never"),
            "summary": agent.get("summary", "No activity")
        }
        digest["agent_updates"].append(update)
    
    # Auto-generate action items from alerts
    if metrics.get("revenue", 0) < 1000:
        digest["alerts"].append("Revenue below daily target")
        digest["action_items"].append("Review pricing or run a promotion")
    
    if metrics.get("leads", 0) == 0:
        digest["alerts"].append("No new leads today")
        digest["action_items"].append("Run Twitter Agent or Research Agent")
    
    return digest

def run(agent_statuses=None, metrics=None):
    """Generate and save the daily ops digest."""
    agent_statuses = agent_statuses or [
        {"name": "Twitter Agent", "status": "active", "last_run": "2h ago", "summary": "Posted 12 tweets"},
        {"name": "Content Agent", "status": "active", "last_run": "4h ago", "summary": "Generated 8 blog posts"},
        {"name": "Stunt Protocol", "status": "active", "last_run": "1d ago", "summary": "40 shapes, 20 ideas logged"},
    ]
    metrics = metrics or {"tasks_completed": 15, "revenue": 1200, "leads": 3}
    
    print("[Ops Digest] Generating daily briefing...")
    digest = generate_digest(agent_statuses, metrics)
    
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    
    out_path = out_dir / f"digest_{digest['date']}.json"
    with open(out_path, "w") as f:
        json.dump(digest, f, indent=2)
    
    print(f"[Ops Digest] {digest['date']}")
    print(f"  Agents active: {digest['summary']['agents_active']}/{digest['summary']['agents_total']}")
    print(f"  Tasks completed: {digest['summary']['total_tasks_completed']}")
    print(f"  Revenue: ${digest['summary']['revenue_today']}")
    print(f"  New leads: {digest['summary']['new_leads']}")
    print(f"  Alerts: {len(digest['alerts'])}")
    print(f"  Action items: {len(digest['action_items'])}")
    print(f"  Saved to: {out_path}")
    return digest

if __name__ == "__main__":
    run()
