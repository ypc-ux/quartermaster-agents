# Quartermaster Agents

**The agent arsenal.** 20 connected agents that run an agency without you touching it.

Part of [Quartermaster](https://github.com/ypc-ux/quartermaster) — the operating system for obsessed risk-takers who ship.

## The Arsenal (300+ points)

| # | Agent | Folder | Points | What It Does |
|---|---|---|---|---|
| 1 | Stunt Shape Protocol | `stunt-protocol/` | **70** | 5-step PR stunt engine (shapes → ideas → artifacts → reporters → pitches) |
| 2 | Quartermaster Orchestrator | `quartermaster.py` | **15** | Runs every agent from one command |
| 3 | Twitter Agent | `twitter-agent/` | **15** | 10-50 tweets/day with Commander Frame triggers |
| 4 | Content Engine | `content-agent/` | **15** | Content for all channels (twitter, email, blog, landing) |
| 5 | Positioning Agent | `commander-frame/` | **15** | 6-stage marketing diagnostic |
| 6 | Personal Brand Vault | `brand-vault/` | **15** | 1 idea → 6 platforms + 10 hooks |
| 7 | Brainwash OS | `brainwash-os/` | **15** | 7-layer culture audit |
| 8 | Research Agent | `research-agent/` | **15** | Competitor scans, market research, trend analysis |
| 9 | Analytics Agent | `analytics-agent/` | **15** | Multi-source KPI tracking + dashboards |
| 10 | Launch Mode | `launch-mode/` | **15** | 7-day content plans for product launches |
| 11 | Ops Digest | `ops-digest/` | **10** | Daily briefing pulling from all agents |
| 12 | Hook Workroom | `hook-workroom/` | **10** | Generate and score 20+ hooks per topic |
| 13 | Collab Tracker | `collab-tracker/` | **10** | Track collaborations, partnerships, outcomes |
| 14 | Finance Tracker | `finance-tracker/` | **10** | Revenue, expenses, profit margins |
| 15 | Batch Day Planner | `batch-day-planner/` | **10** | Plan batch content creation sessions |
| 16 | Trend Adapter | `trend-adapter/` | **10** | Adapt trending topics to your brand voice |
| 17 | Community Tracker | `community-tracker/` | **10** | Community engagement across platforms |
| 18 | Sunday Reset | `sunday-reset/` | **5** | Weekly review + next-week planning |
| 19 | Bio Optimizer | `bio-optimizer/` | **5** | Optimize social bios for conversion |
| 20 | Grid Preview | `grid-preview/` | **5** | Preview Instagram grid before posting |

**TOTAL: 315 points.**

## Run It

```bash
# Status of all agents
python quartermaster.py status

# Run any agent directly
python stunt-protocol/run.py build
python brand-vault/scripts/repurposer.py "your idea"
python commander-frame/scripts/commander_frame.py
python research-agent/scripts/research_agent.py competitor_scan
python analytics-agent/scripts/analytics_agent.py
python launch-mode/scripts/launch_mode.py "Product Name"
python ops-digest/scripts/ops_digest.py
python hook-workroom/scripts/hook_workroom.py "topic"
python collab-tracker/scripts/collab_tracker.py
python finance-tracker/scripts/finance_tracker.py
python batch-day-planner/scripts/batch_day_planner.py
python trend-adapter/scripts/trend_adapter.py "agency owners"
python community-tracker/scripts/community_tracker.py
python sunday-reset/scripts/sunday_reset.py
python bio-optimizer/scripts/bio_optimizer.py "your bio"
python grid-preview/scripts/grid_preview.py
```

## Design System

All agents follow the same pattern:
- **Navy/gold/Instrument Serif** branding
- **No API keys required** for core functionality
- **JSON output** in `data/` folders
- **Runnable as standalone** scripts or via the orchestrator

## The Rule

Every agent runs on a real cadence. None are opened once for a demo and shelved.

---

**Company line:** *"We build operating systems for obsessed risk-takers who ship."*
