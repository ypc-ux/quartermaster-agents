#!/usr/bin/env python3
"""Launch Mode — Quartermaster. 7-day content plans for product launches."""

import json
from datetime import datetime, timedelta
from pathlib import Path

LAUNCH_PHASES = ["teaser", "announcement", "deep_dive", "social_proof", "urgency", "last_chance", "post_launch"]

CONTENT_TYPES = ["tweet", "email", "blog_post", "video_script", "carousel", "story"]

def generate_launch_plan(product_name, launch_date=None, audience=None):
    """Generate a 7-day launch content plan."""
    launch_date = launch_date or datetime.now()
    if isinstance(launch_date, str):
        launch_date = datetime.fromisoformat(launch_date)
    
    plan = {
        "product": product_name,
        "launch_date": launch_date.isoformat(),
        "audience": audience or "agency owners",
        "phases": [],
        "total_pieces": 0,
        "generated_at": datetime.now().isoformat()
    }
    
    for i, phase in enumerate(LAUNCH_PHASES):
        day = launch_date + timedelta(days=i)
        pieces = []
        for content_type in CONTENT_TYPES[:3]:  # 3 pieces per day
            pieces.append({
                "type": content_type,
                "phase": phase,
                "scheduled_for": day.isoformat(),
                "status": "drafted",
                "hook": f"[{phase}] {product_name} - {content_type} hook"
            })
        
        plan["phases"].append({
            "day": i + 1,
            "phase": phase,
            "date": day.strftime("%Y-%m-%d"),
            "pieces": pieces,
            "focus": f"{phase.replace('_', ' ').title()} content"
        })
        plan["total_pieces"] += len(pieces)
    
    return plan

def generate_email_sequence(product_name, launch_date=None):
    """Generate a 5-email launch sequence."""
    launch_date = launch_date or datetime.now()
    emails = [
        {"day": -3, "type": "teaser", "subject": f"Something's coming for {product_name}..."},
        {"day": 0, "type": "announcement", "subject": f"Introducing {product_name}"},
        {"day": 2, "type": "deep_dive", "subject": f"How {product_name} actually works"},
        {"day": 5, "type": "social_proof", "subject": f"What people are saying about {product_name}"},
        {"day": 6, "type": "last_chance", "subject": f"Last chance: {product_name} closes soon"}
    ]
    return {"type": "email_sequence", "product": product_name, "emails": emails}

def run(product_name="Quartermaster", launch_date=None):
    """Generate a full launch plan."""
    print(f"[Launch Mode] Generating 7-day launch plan for {product_name}...")
    plan = generate_launch_plan(product_name, launch_date)
    emails = generate_email_sequence(product_name, launch_date)
    
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    
    result = {
        "launch_plan": plan,
        "email_sequence": emails,
        "summary": {
            "total_content_pieces": plan["total_pieces"] + len(emails["emails"]),
            "launch_phases": len(LAUNCH_PHASES),
            "email_sequence_length": len(emails["emails"])
        }
    }
    
    out_path = out_dir / f"launch_plan_{product_name.lower().replace(' ', '_')}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"[Launch Mode] Launch plan generated:")
    print(f"  Product: {product_name}")
    print(f"  Phases: {len(LAUNCH_PHASES)}")
    print(f"  Content pieces: {plan['total_pieces']}")
    print(f"  Email sequence: {len(emails['emails'])} emails")
    print(f"  Saved to: {out_path}")
    return result

if __name__ == "__main__":
    import sys
    product = sys.argv[1] if len(sys.argv) > 1 else "Quartermaster"
    run(product)
