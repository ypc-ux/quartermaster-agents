#!/usr/bin/env python3
"""Quartermaster Agent Orchestrator — runs every agent from one command.

Usage:
  python quartermaster.py status          # what every agent is doing
  python quartermaster.py stunt build     # Stunt Protocol step 1+2
  python quartermaster.py stunt step3     # log artifacts
  python quartermaster.py diagnose        # Commander Frame 6-stage diagnostic
  python quartermaster.py culture         # Brainwash OS 7-layer audit
  python quartermaster.py repurpose "..." # one idea -> 6 platforms
  python quartermaster.py tweet           # generate + queue tweets
  python quartermaster.py content x 20    # generate content
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent


def status():
    print("\n=== QUARTERMASTER — AGENT STATUS ===")
    agents = [
        ("Stunt Protocol", "stunt-protocol/run.py", "5 steps, 20 ideas, artifact-gated"),
        ("Commander Frame", "commander-frame/scripts/commander_frame.py", "6-stage diagnostic"),
        ("Brainwash OS", "brainwash-os/scripts/brainwash_os.py", "7-layer culture audit"),
        ("Brand Vault", "brand-vault/scripts/repurposer.py", "1 idea -> 6 platforms"),
        ("Twitter Agent", "twitter-agent/scripts/twitter_agent.py", "10-50 tweets/day"),
        ("Content Agent", "content-agent/scripts/content_agent.py", "all channels"),
    ]
    for name, path, desc in agents:
        present = "[x]" if (ROOT / path).exists() else "[ ]"
        print(f"  {present} {name:18} {desc}")
    print("====================================\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        status()
        return
    cmd = sys.argv[1]
    if cmd == "status":
        status()
    elif cmd == "stunt":
        sys.path.insert(0, str(ROOT / "stunt-protocol"))
        import run as stunt_run
        stunt_run.main()
    elif cmd == "stunt-build":
        sys.path.insert(0, str(ROOT / "stunt-protocol"))
        import run as stunt_run
        sys.argv = ["run.py", "build"]; stunt_run.main()
    elif cmd == "diagnose":
        sys.path.insert(0, str(ROOT / "commander-frame/scripts"))
        import commander_frame as cf
        import json
        print(json.dumps(cf.run_diagnostic(
            "We build operating systems for obsessed risk-takers who ship.",
            has_real_number=True), indent=2))
    elif cmd == "culture":
        sys.path.insert(0, str(ROOT / "brainwash-os/scripts"))
        import brainwash_os as bw, json
        print(json.dumps(bw.audit_brand(
            {"mind": 9, "exposure": 7, "practices": 5, "artifacts": 3,
             "protagonists": 8, "aesthetics": 9, "conflict": 6}), indent=2))
    elif cmd == "repurpose":
        sys.path.insert(0, str(ROOT / "brand-vault/scripts"))
        import repurposer
        repurposer.run(" ".join(sys.argv[2:]) or "shipped 20 agents in 12 hours")
    elif cmd == "tweet":
        sys.path.insert(0, str(ROOT / "twitter-agent/scripts"))
        import twitter_agent
        twitter_agent.run()
    elif cmd == "content":
        sys.path.insert(0, str(ROOT / "content-agent/scripts"))
        import content_agent
        ch = sys.argv[2] if len(sys.argv) > 2 else "twitter"
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        content_agent.run(ch, n)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
