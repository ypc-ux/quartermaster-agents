#!/usr/bin/env python3
"""Stunt Protocol Engine — Step 3: Run it. Log everything.

A stunt is a claim anyone can check. Three artifacts required before pitching:
  1. existed  — the thing actually happened (listing, photo, invoice)
  2. reaction — somebody outside the company reacted (reply, comment, counter-offer)
  3. number   — one figure a reporter can put in a headline
"""

import json
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent.parent / "data"
REQUIRED_PROOFS = ["existed", "reaction", "number"]

VALID_TYPES = ["listing", "screenshot", "reply", "receipt", "photo", "video", "post"]


def load_ideas():
    p = OUTPUT_DIR / "stunt_ideas.json"
    return json.load(open(p)) if p.exists() else {"ideas": []}


def load_artifacts():
    p = OUTPUT_DIR / "artifacts.json"
    return json.load(open(p)) if p.exists() else {"artifacts": []}


def save_artifacts(data):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json.dump(data, open(OUTPUT_DIR / "artifacts.json", "w"), indent=2)


def add_artifact(idea_id, type_, proves, url_or_path, captured_at=None, note=""):
    """Add one artifact row. Assigns art-NNN once, never regenerates."""
    if type_ not in VALID_TYPES:
        raise ValueError(f"type must be one of {VALID_TYPES}")
    if proves not in REQUIRED_PROOFS:
        raise ValueError(f"proves must be one of {REQUIRED_PROOFS}")
    data = load_artifacts()
    n = len(data["artifacts"]) + 1
    row = {
        "artifact_id": f"art-{n:03d}",
        "idea_id": idea_id,
        "type": type_,
        "proves": proves,
        "url_or_path": url_or_path,
        "captured_at": captured_at or datetime.now().isoformat(),
        "note": f"{note}" if proves != "number" else note or "(no figure)",
    }
    data["artifacts"].append(row)
    save_artifacts(data)
    print(f"[Stunt Protocol] Logged {row['artifact_id']} ({proves}) for {idea_id}")
    return row


def check_ready(idea_id):
    """Check an idea has one artifact of each proof type before pitching."""
    data = load_artifacts()
    got = {a["proves"] for a in data["artifacts"] if a["idea_id"] == idea_id}
    missing = [p for p in REQUIRED_PROOFS if p not in got]
    return {"idea_id": idea_id, "ready": not missing, "missing": missing, "have": sorted(got)}


def set_status(idea_id, status):
    """drafted -> chosen -> running -> done / dead."""
    data = load_ideas()
    for idea in data.get("ideas", []):
        if idea["id"] == idea_id:
            idea["status"] = status
            json.dump(data, open(OUTPUT_DIR / "stunt_ideas.json", "w"), indent=2)
            print(f"[Stunt Protocol] {idea_id} -> {status}")
            return idea
    print(f"[Stunt Protocol] Idea {idea_id} not found")
    return None


def finish(idea_id):
    """Only set done when all three proofs exist."""
    r = check_ready(idea_id)
    if not r["ready"]:
        print(f"[Stunt Protocol] CANNOT finish {idea_id}. Missing proofs: {r['missing']}")
        return False
    return set_status(idea_id, "done") is not None


def run():
    """Demo: show what a complete artifact set looks like."""
    print("[Stunt Protocol] Step 3: Run it. Log everything.")
    demo = [
        ("idea-001", "listing", "existed", "https://flippa.com/listing/dead-agency-xyz", "The live listing. Any stranger could open it."),
        ("idea-001", "reply", "reaction", "screenshot-0001.png", "Buyer DM: 'Is this real?' — outside reaction."),
        ("idea-001", "screenshot", "number", "quartermaster-dashboard.png", "0 new code, 8 repos, 1 agency running in 24h"),
    ]
    for idea_id, t, proves, url, note in demo:
        add_artifact(idea_id, t, proves, url, note=note)
    print(f"[Stunt Protocol] Ready check idea-001: {check_ready('idea-001')}")


if __name__ == "__main__":
    run()
