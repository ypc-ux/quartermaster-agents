#!/usr/bin/env python3
"""Sunday Reset — Quartermaster. Weekly planning and reflection."""

import json
from datetime import datetime, timedelta
from pathlib import Path

def generate_weekly_review(last_week_goals, achievements, metrics):
    """Generate a review of last week."""
    completed = sum(1 for g in last_week_goals if g.get("completed", False))
    total = len(last_week_goals)
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    return {
        "goals_set": total,
        "goals_completed": completed,
        "completion_rate_pct": round(completion_rate, 1),
        "achievements": achievements,
        "metrics": metrics,
        "lessons_learned": [],
        "reviewed_at": datetime.now().isoformat()
    }

def plan_next_week(goals, focus_areas, commitments):
    """Plan the upcoming week."""
    next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
    
    return {
        "week_start": next_monday.strftime("%Y-%m-%d"),
        "goals": [{"goal": g, "status": "planned", "priority": "medium"} for g in goals],
        "focus_areas": focus_areas,
        "commitments": commitments,
        "planned_at": datetime.now().isoformat(),
        "time_blocks": [],
        "energy_management": {
            "peak_hours": "9am-12pm",
            "deep_work_slots": [],
            "meeting_free_days": []
        }
    }

def generate_reset_checklist():
    """Generate a Sunday reset checklist."""
    return [
        {"task": "Review last week's goals", "category": "reflection", "done": False},
        {"task": "Celebrate wins (big and small)", "category": "reflection", "done": False},
        {"task": "Identify lessons learned", "category": "reflection", "done": False},
        {"task": "Set next week's goals (3-5 max)", "category": "planning", "done": False},
        {"task": "Block time for deep work", "category": "planning", "done": False},
        {"task": "Review calendar and commitments", "category": "planning", "done": False},
        {"task": "Clear inbox and notifications", "category": "systems", "done": False},
        {"task": "Update content calendar", "category": "systems", "done": False},
        {"task": "Prepare Monday's priorities", "category": "preparation", "done": False},
        {"task": "Rest and recharge", "category": "self_care", "done": False}
    ]

def run():
    """Generate a Sunday reset plan."""
    print("[Sunday Reset] Generating weekly review and plan...")
    
    last_week_goals = [
        {"goal": "Launch Stunt Protocol", "completed": True},
        {"goal": "Write 10 blog posts", "completed": False},
        {"goal": "Record 3 videos", "completed": True}
    ]
    
    achievements = [
        "Launched Stunt Protocol with 40 shapes",
        "Gained 200 new followers",
        "Closed 2 new clients"
    ]
    
    metrics = {
        "revenue": 5000,
        "new_leads": 8,
        "content_pieces": 15,
        "followers_gained": 200
    }
    
    review = generate_weekly_review(last_week_goals, achievements, metrics)
    
    next_week_goals = [
        "Build Analytics Agent",
        "Launch new product",
        "Record 5 videos",
        "Write guest post"
    ]
    
    plan = plan_next_week(
        goals=next_week_goals,
        focus_areas=["Product development", "Content creation"],
        commitments=["Client calls Tue/Thu", "Podcast recording Wed"]
    )
    
    checklist = generate_reset_checklist()
    
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    
    result = {
        "review": review,
        "next_week_plan": plan,
        "checklist": checklist,
        "generated_at": datetime.now().isoformat()
    }
    
    out_path = out_dir / f"sunday_reset_{datetime.now().strftime('%Y%m%d')}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"[Sunday Reset] Weekly review:")
    print(f"  Goals completed: {review['goals_completed']}/{review['goals_set']}")
    print(f"  Completion rate: {review['completion_rate_pct']}%")
    print(f"  Achievements: {len(achievements)}")
    print(f"  Next week goals: {len(plan['goals'])}")
    print(f"  Saved to: {out_path}")
    return result

if __name__ == "__main__":
    run()
