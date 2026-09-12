#!/usr/bin/env python3
"""Collab Tracker — Quartermaster. Track collaborations, partnerships, and joint ventures."""

import json
from datetime import datetime
from pathlib import Path

COLLAB_TYPES = ["podcast", "webinar", "guest_post", "co_creation", "affiliate", "joint_venture"]
STATUSES = ["proposed", "in_discussion", "agreed", "in_progress", "completed", "declined"]

def log_collab(partner_name, collab_type, description, target_date=None):
    """Log a new collaboration."""
    return {
        "id": f"collab_{int(datetime.now().timestamp())}",
        "partner": partner_name,
        "type": collab_type,
        "description": description,
        "status": "proposed",
        "proposed_at": datetime.now().isoformat(),
        "target_date": target_date,
        "notes": [],
        "outcomes": []
    }

def update_collab_status(collabs, collab_id, new_status, note=None):
    """Update a collaboration's status."""
    for collab in collabs:
        if collab["id"] == collab_id:
            collab["status"] = new_status
            collab["updated_at"] = datetime.now().isoformat()
            if note:
                collab["notes"].append({
                    "note": note,
                    "timestamp": datetime.now().isoformat()
                })
            return collab
    return None

def track_outcome(collabs, collab_id, outcome_type, metrics):
    """Track the outcome of a completed collaboration."""
    for collab in collabs:
        if collab["id"] == collab_id:
            collab["outcomes"].append({
                "type": outcome_type,
                "metrics": metrics,
                "recorded_at": datetime.now().isoformat()
            })
            collab["status"] = "completed"
            return collab
    return None

def run():
    """Demo: log sample collabs and save."""
    print("[Collab Tracker] Logging sample collaborations...")
    
    collabs = [
        log_collab("Agency Podcast Host", "podcast", "Guest appearance on agency growth podcast", "2026-09-20"),
        log_collab("SaaS Founder", "webinar", "Co-hosted webinar on automation for agencies", "2026-09-25"),
        log_collab("Marketing Expert", "guest_post", "Guest post exchange on content strategy", "2026-10-01"),
    ]
    
    # Update one to in_progress
    update_collab_status(collabs, collabs[0]["id"], "in_progress", "Confirmed recording date")
    
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    
    result = {
        "collaborations": collabs,
        "summary": {
            "total": len(collabs),
            "by_status": {s: sum(1 for c in collabs if c["status"] == s) for s in set(c["status"] for c in collabs)},
            "by_type": {t: sum(1 for c in collabs if c["type"] == t) for t in set(c["type"] for c in collabs)}
        },
        "updated_at": datetime.now().isoformat()
    }
    
    out_path = out_dir / "collaborations.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"[Collab Tracker] Logged {len(collabs)} collaborations")
    print(f"  By type: {result['summary']['by_type']}")
    print(f"  By status: {result['summary']['by_status']}")
    print(f"  Saved to: {out_path}")
    return result

if __name__ == "__main__":
    run()
