#!/usr/bin/env python3
"""Stunt Protocol Engine — Step 5: Pitch, one at a time.

Not a sequence. Not a blast. One email, to one person, about the story
they already wrote. Subject under 30 chars. Body under 120 words.
Figure-led. One link, to the proof. One question answerable in a word.

The prompt writes all five compliance elements CAN-SPAM needs:
real name, real reply-to, honest subject, postal address, opt-out line.
"""

import json
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent.parent / "data"

# ─── Your real signature — fill these in once ────────────────────────────────
SIGNATURE = {
    "name": "Julius Young III",
    "reply_to": "REPLY_TO_ADDRESS",
    "postal": "POSTAL_ADDRESS",
}


def get_figure(idea_id):
    """Pull the 'number' artifact for this idea — the headline figure."""
    p = OUTPUT_DIR / "artifacts.json"
    if not p.exists():
        return None
    data = json.load(open(p))
    for a in data.get("artifacts", []):
        if a["idea_id"] == idea_id and a["proves"] == "number":
            return a.get("note") or a.get("url_or_path")
    return None


def get_proof_link(idea_id):
    """Link to the proof, not the homepage — an 'existed' artifact."""
    p = OUTPUT_DIR / "artifacts.json"
    if not p.exists():
        return ""
    data = json.load(open(p))
    for a in data.get("artifacts", []):
        if a["idea_id"] == idea_id and a["proves"] == "existed":
            return a.get("url_or_path", "")
    return ""


def draft_email(reporter, idea_id, figure, proof_link):
    """Write ONE email to ONE person. Under 120 words, subject under 30 chars."""
    name = reporter["name"]
    headline = reporter["coverage_headline"]
    first = name.split()[0] if name not in ("(unbylined)",) else None

    # Subject: say the thing, don't tease it. Under 30 chars.
    subject = "Sold a dead agency in 24h"

    if name == "(unbylined)":
        opener = f'You ran "{headline}". The next beat is live:'
    else:
        opener = f'{first} — your piece "{headline}" has a next beat.'

    body = (
        f"{opener} I bought a dead agency for $0 and had it operating in 24 hours, "
        f"no new code. The number: {figure}. "
        f"Proof here: {proof_link}\n\n"
        f"Worth a look?"
    )

    sig = (
        f"\n\n{SIGNATURE['name']} · {SIGNATURE['reply_to']} · {SIGNATURE['postal']}\n"
        f"Tell me to stop and I will."
    )

    full_body = body + sig
    word_count = len(body.split())
    warnings = []
    if len(subject) >= 30:
        warnings.append(f"subject is {len(subject)} chars (max 30)")
    if word_count > 120:
        warnings.append(f"body is {word_count} words (max 120, excl. signature)")

    return {"subject": subject, "body": full_body, "words": word_count, "warnings": warnings}


def save_pitch(reporter_id, idea_id, subject, body, touch=1):
    """Write a draft into Pitches. Does NOT send — you send it yourself, one at a time."""
    p = OUTPUT_DIR / "pitches.json"
    data = json.load(open(p)) if p.exists() else {"pitches": []}
    # Never write a second row with the same reporter_id + touch
    for existing in data["pitches"]:
        if existing["reporter_id"] == reporter_id and existing["touch"] == touch:
            print(f"[Stunt Protocol] Pitch already exists for {reporter_id} touch {touch} — skipping")
            return existing
    n = len(data["pitches"]) + 1
    row = {
        "pitch_id": f"pitch-{n:03d}",
        "reporter_id": reporter_id,
        "idea_id": idea_id,
        "touch": touch,
        "sent_at": "",
        "channel": "email",
        "subject": subject,
        "body": body,
        "reply": "",
        "outcome": "",
    }
    data["pitches"].append(row)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json.dump(data, open(p, "w"), indent=2)
    print(f"[Stunt Protocol] Drafted {row['pitch_id']} -> {reporter_id}")
    return row


def run(idea_id="idea-001", limit=5):
    """Draft the next 5 verified reporters. You read and send them yourself."""
    print("[Stunt Protocol] Step 5: Pitch, one at a time.")
    rp = OUTPUT_DIR / "reporters.json"
    reporters = json.load(open(rp))["reporters"] if rp.exists() else []
    figure = get_figure(idea_id) or "(add a number artifact)"
    link = get_proof_link(idea_id)

    drafted = 0
    for r in reporters:
        if drafted >= limit:
            break
        if r["status"] != "verified":
            continue
        email_draft = draft_email(r, idea_id, figure, link)
        save_pitch(r["reporter_id"], idea_id, email_draft["subject"], email_draft["body"])
        print(f"  Subject: {email_draft['subject']} ({len(email_draft['subject'])} chars)")
        print(f"  Body: {email_draft['words']} words")
        if email_draft["warnings"]:
            print(f"  WARN: {email_draft['warnings']}")
        drafted += 1

    print(f"[Stunt Protocol] Drafted {drafted} pitches. Send them yourself, before noon their time.")
    return drafted


if __name__ == "__main__":
    run()
