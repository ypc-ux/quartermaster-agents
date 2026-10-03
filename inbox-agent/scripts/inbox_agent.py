#!/usr/bin/env python3
"""Inbox Agent — Julius's email command loop.

Julius emails the inbox address. This agent runs on GitHub Actions (cloud),
reads new received emails via the Resend API, executes the command, and
emails the result back. Nothing runs on the laptop.

Requires a FULL-ACCESS Resend API key (the sending-only key cannot read
received mail). Graceful failure if the key is restricted: prints the
reason and exits 0 so the pipeline stays green.
"""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RESEND_KEY = os.environ.get("RESEND_API_KEY", "")
OWNER_EMAIL = os.environ.get("INBOX_OWNER_EMAIL", "")
INBOX_ADDRESS = os.environ.get("INBOX_ADDRESS", "boss@theinfluencecapital.com")
API = "https://api.resend.com"

ROOT = Path(__file__).resolve().parent
PROCESSED = ROOT / "processed.json"
REPLY_FROM = "Julius's Office <onboarding@resend.dev>"


def http(method, path, payload=None):
    req = urllib.request.Request(
        API + path,
        method=method,
        headers={
            "Authorization": "Bearer " + RESEND_KEY,
            "Content-Type": "application/json",
        },
        data=json.dumps(payload).encode() if payload is not None else None,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        return e.code, {"error": body}
    except Exception as e:  # noqa: BLE001
        return 0, {"error": str(e)}


def load_processed():
    if PROCESSED.exists():
        try:
            return set(json.loads(PROCESSED.read_text()))
        except Exception:  # noqa: BLE001
            return set()
    return set()


def save_processed(ids):
    PROCESSED.write_text(json.dumps(sorted(ids), indent=2))


def list_received():
    for path in ("/emails?direction=received", "/received-emails"):
        status, data = http("GET", path)
        if status == 200 and isinstance(data, dict):
            return data.get("data", [])
        if status in (401, 403):
            print(f"[inbox] {path} -> {status}: {json.dumps(data)[:200]}")
            return "RESTRICTED"
    return []


def send_reply(to, subject, text):
    return http("POST", "/emails", {
        "from": REPLY_FROM,
        "to": [to],
        "subject": "Re: " + subject[:70],
        "text": text,
        "reply_to": [INBOX_ADDRESS],
    })


def run_command(cmd, arg):
    cmd = cmd.lower()
    if cmd in ("help", "commands"):
        return (
            "Here's what I can do from email:\n\n"
            "status          — machine health: agents, queues, GPU data\n"
            "tweets          — pending tweet drafts and count\n"
            "content         — pending content queue counts\n"
            "research: X     — queue a research task for the research agent\n"
            "help            — this message\n\n"
            "Anything else gets logged and flagged for review."
        )
    if cmd == "status":
        lines = ["MACHINE STATUS", "=" * 30]
        q = ROOT.parent.parent / "twitter-agent" / "queue.json"
        if q.exists():
            try:
                tq = json.loads(q.read_text())
                n = len(tq) if isinstance(tq, list) else len(tq.get("tweets", tq.get("queue", [])))
                lines.append(f"Tweet drafts queued: {n}")
            except Exception:  # noqa: BLE001
                lines.append("Tweet queue: unreadable")
        else:
            lines.append("Tweet queue: empty")
        for name in ("content_queue_twitter.json", "content_queue_email.json"):
            p = ROOT.parent.parent / "content-agent" / name
            if p.exists():
                try:
                    c = json.loads(p.read_text())
                    n = len(c) if isinstance(c, list) else len(c.get("items", c))
                    lines.append(f"{name}: {n} items")
                except Exception:  # noqa: BLE001
                    lines.append(f"{name}: unreadable")
        lines.append("GPU ingest: hourly in the cloud (ypc-ux/gpu-broker)")
        lines.append("Sites: influence-capital, lifeline-layer, valence-vision, agentdatasync")
        return "\n".join(lines)
    if cmd == "tweets":
        q = ROOT.parent.parent / "twitter-agent" / "queue.json"
        if not q.exists():
            return "No tweet drafts queued right now."
        try:
            tq = json.loads(q.read_text())
            tweets = tq if isinstance(tq, list) else tq.get("tweets", tq.get("queue", []))
            lines = [f"{len(tweets)} drafts waiting:", ""]
            for i, t in enumerate(tweets[:5], 1):
                txt = t.get("text", str(t)) if isinstance(t, dict) else str(t)
                lines.append(f"{i}. {txt[:160]}")
            return "\n".join(lines)
        except Exception:  # noqa: BLE001
            return "Tweet queue exists but I couldn't parse it."
    if cmd.startswith("research"):
        topic = arg or (cmd.split(":", 1)[1] if ":" in cmd else "")
        inbox = ROOT.parent.parent / "research-agent" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        fname = f"{int(time.time())}.json"
        (inbox / fname).write_text(json.dumps({
            "from": "email", "topic": topic.strip(),
            "received": datetime.now(timezone.utc).isoformat()
        }, indent=2))
        return f"Research queued: '{topic.strip()[:80]}'. The research agent picks it up on its next run."
    return None


def main():
    if not RESEND_KEY:
        print("[inbox] RESEND_API_KEY not set — skipping")
        return
    if not OWNER_EMAIL:
        print("[inbox] INBOX_OWNER_EMAIL not set — skipping")
        return

    received = list_received()
    if received == "RESTRICTED":
        print("[inbox] Resend key is sending-only. The email loop needs a full-access key. Skipping gracefully.")
        return

    processed = load_processed()
    new_ids = []
    handled = []
    for msg in received:
        mid = msg.get("id")
        if mid in processed:
            continue
        new_ids.append(mid)
        frm = msg.get("from", "unknown")
        subject = msg.get("subject", "(no subject)")
        text = (msg.get("text") or msg.get("html") or "").strip()
        words = text.split()
        cmd = words[0].rstrip(":").lower() if words else "help"
        arg = " ".join(words[1:])
        result = run_command(cmd, arg)
        if result is None:
            result = (
                "I didn't recognize that command.\n\n"
                "Send 'help' for the list of things I can do from email.\n"
                "Your message was logged and flagged for review."
            )
        status, _ = send_reply(OWNER_EMAIL, subject, result)
        handled.append({"id": mid, "from": frm, "subject": subject[:60], "reply_status": status})
        print(f"[inbox] {frm} → '{cmd}' → reply {status}")

    if handled:
        processed |= set(new_ids)
        save_processed(processed)
        print(f"[inbox] handled {len(handled)} messages")
    else:
        print("[inbox] no new messages")


if __name__ == "__main__":
    main()
    sys.exit(0)
