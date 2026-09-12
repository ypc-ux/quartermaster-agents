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
        # Strategy (pts)
        ("Stunt Protocol",      "stunt-protocol/run.py",                          "5 steps, 20 ideas, artifact-gated", 70),
        ("Commander Frame",     "commander-frame/scripts/commander_frame.py",     "6-stage marketing diagnostic",      15),
        ("Brainwash OS",        "brainwash-os/scripts/brainwash_os.py",           "7-layer culture audit",             15),
        ("Research Agent",      "research-agent/scripts/research_agent.py",       "competitor/market/trend research",  15),
        ("Trend Adapter",       "trend-adapter/scripts/trend_adapter.py",         "adapt trends to brand voice",       10),
        ("Launch Mode",         "launch-mode/scripts/launch_mode.py",             "7-day launch content plans",        15),
        # Content
        ("Twitter Agent",       "twitter-agent/scripts/twitter_agent.py",         "10-50 tweets/day",                  15),
        ("Content Engine",      "content-agent/scripts/content_agent.py",         "all channels",                      15),
        ("Brand Vault",         "brand-vault/scripts/repurposer.py",              "1 idea -> 6 platforms + 10 hooks",  15),
        ("Hook Workroom",       "hook-workroom/scripts/hook_workroom.py",         "generate + score 20+ hooks",        10),
        ("Batch Day Planner",   "batch-day-planner/scripts/batch_day_planner.py", "plan batch content sessions",       10),
        ("Bio Optimizer",       "bio-optimizer/scripts/bio_optimizer.py",         "optimize social bios",              5),
        ("Grid Preview",        "grid-preview/scripts/grid_preview.py",           "Instagram grid preview",            5),
        # Operations
        ("Ops Digest",          "ops-digest/scripts/ops_digest.py",               "daily briefing, all agents",        10),
        ("Analytics Agent",     "analytics-agent/scripts/analytics_agent.py",     "multi-source KPI tracking",         15),
        ("Finance Tracker",     "finance-tracker/scripts/finance_tracker.py",     "revenue, expenses, margins",        10),
        ("Collab Tracker",      "collab-tracker/scripts/collab_tracker.py",       "partnerships + joint ventures",     10),
        ("Community Tracker",   "community-tracker/scripts/community_tracker.py", "engagement across platforms",       10),
        ("Sunday Reset",        "sunday-reset/scripts/sunday_reset.py",           "weekly review + planning",          5),
    ]
    total = sum(a[3] for a in agents)
    active = sum(1 for a in agents if (ROOT / a[1]).exists())
    for name, path, desc, pts in agents:
        present = "[x]" if (ROOT / path).exists() else "[ ]"
        print(f"  {present} {name:22} {desc:42} ({pts}pts)")
    print(f"==================================== ({active}/{len(agents)} active, {total} pts)\n")


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
    elif cmd == "research":
        sys.path.insert(0, str(ROOT / "research-agent/scripts"))
        import research_agent
        research_agent.run(sys.argv[2] if len(sys.argv) > 2 else "competitor_scan")
    elif cmd == "analytics":
        sys.path.insert(0, str(ROOT / "analytics-agent/scripts"))
        import analytics_agent
        analytics_agent.run()
    elif cmd == "launch":
        sys.path.insert(0, str(ROOT / "launch-mode/scripts"))
        import launch_mode
        launch_mode.run(sys.argv[2] if len(sys.argv) > 2 else "Quartermaster")
    elif cmd == "digest":
        sys.path.insert(0, str(ROOT / "ops-digest/scripts"))
        import ops_digest
        ops_digest.run()
    elif cmd == "hooks":
        sys.path.insert(0, str(ROOT / "hook-workroom/scripts"))
        import hook_workroom
        hook_workroom.run(" ".join(sys.argv[2:]) or "building agency systems")
    elif cmd == "collab":
        sys.path.insert(0, str(ROOT / "collab-tracker/scripts"))
        import collab_tracker
        collab_tracker.run()
    elif cmd == "finance":
        sys.path.insert(0, str(ROOT / "finance-tracker/scripts"))
        import finance_tracker
        finance_tracker.run()
    elif cmd == "batch":
        sys.path.insert(0, str(ROOT / "batch-day-planner/scripts"))
        import batch_day_planner
        batch_day_planner.run()
    elif cmd == "trends":
        sys.path.insert(0, str(ROOT / "trend-adapter/scripts"))
        import trend_adapter
        trend_adapter.run(" ".join(sys.argv[2:]) or "agency owners")
    elif cmd == "community":
        sys.path.insert(0, str(ROOT / "community-tracker/scripts"))
        import community_tracker
        community_tracker.run()
    elif cmd == "reset":
        sys.path.insert(0, str(ROOT / "sunday-reset/scripts"))
        import sunday_reset
        sunday_reset.run()
    elif cmd == "bio":
        sys.path.insert(0, str(ROOT / "bio-optimizer/scripts"))
        import bio_optimizer
        bio_optimizer.run(" ".join(sys.argv[2:]) or "Building operating systems for agencies")
    elif cmd == "grid":
        sys.path.insert(0, str(ROOT / "grid-preview/scripts"))
        import grid_preview
        grid_preview.run()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
