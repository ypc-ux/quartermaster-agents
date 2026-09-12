#!/usr/bin/env python3
"""Stunt Protocol Engine — Orchestrator.

Runs all five steps, builds the Stunt Shape Tracker (.xlsx), and reports status.
Five sheets: Stunts, Ideas, Artifacts, Reporters, Opt-outs (+ Pitches).

Run:
  python run.py build      # step 1 + 2, build the tracker
  python run.py report     # status across all sheets
  python run.py step3      # log demo artifacts
  python run.py step4      # find reporters
  python run.py step5      # draft pitches
"""

import json, sys
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))


def load(name, key):
    p = DATA / name
    if not p.exists():
        return []
    data = json.load(open(p))
    if isinstance(data, list):
        return data
    return data.get(key, [])


def build_tracker():
    """Write the Stunt Shape Tracker .xlsx with all sheets."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
    except ImportError:
        print("[Stunt Protocol] openpyxl not installed. pip install openpyxl")
        print("[Stunt Protocol] (JSON data is still written to data/)")
        return None

    wb = Workbook()
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="0B1426")

    sheets = {
        "Stunts": (["stunt_id", "shape", "mechanic", "why_covered"],
                   [[s["id"], s["shape"], s["mechanic"], s["why_covered"]] for s in load("stunt_shapes.json", "shapes") or []]),
        "Ideas": (["idea_id", "parent_stunt_id", "idea", "impossible_without", "cost_band", "days_to_run", "status"],
                  [[i["id"], i["parent"], i["idea"], i["impossible_without"], i["cost"], i["days"], i.get("status", "drafted")] for i in load("stunt_ideas.json", "ideas")]),
        "Artifacts": (["artifact_id", "idea_id", "type", "proves", "url_or_path", "captured_at", "note"],
                      [[a["artifact_id"], a["idea_id"], a["type"], a["proves"], a["url_or_path"], a["captured_at"], a["note"]] for a in load("artifacts.json", "artifacts")]),
        "Reporters": (["reporter_id", "name", "outlet", "beat", "coverage_headline", "status", "confidence"],
                      [[r["reporter_id"], r["name"], r["outlet"], r["beat"], r["coverage_headline"], r["status"], r["confidence"]] for r in load("reporters.json", "reporters")]),
        "Opt-outs": (["email", "date", "source"], []),
    }

    for idx, (name, (cols, rows)) in enumerate(sheets.items()):
        ws = wb.active if idx == 0 else wb.create_sheet()
        ws.title = name
        for c, col in enumerate(cols, 1):
            cell = ws.cell(row=1, column=c, value=col)
            cell.font = header_font
            cell.fill = header_fill
        for r, row in enumerate(rows, 2):
            for c, val in enumerate(row, 1):
                ws.cell(row=r, column=c, value=val)

    out = DATA / "Stunt_Shape_Tracker.xlsx"
    DATA.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    print(f"[Stunt Protocol] Wrote {out}")
    return out


def report():
    stunts = load("stunt_shapes.json", "shapes")
    ideas = load("stunt_ideas.json", "ideas")
    arts = load("artifacts.json", "artifacts")
    reps = load("reporters.json", "reporters")
    pitches = load("pitches.json", "pitches")
    print("\n=== STUNT SHAPE TRACKER ===")
    print(f"  Stunts:    {len(stunts)}")
    print(f"  Ideas:     {len(ideas)}")
    print(f"  Artifacts: {len(arts)}  ({len({a['proves'] for a in arts})}/3 proof types)")
    print(f"  Reporters: {len(reps)}  ({sum(1 for r in reps if r['status']=='verified')} verified)")
    print(f"  Pitches:   {len(pitches)}")
    print("===========================\n")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        import step1_steal_shapes, step2_generate_ideas
        step1_steal_shapes.run()
        step2_generate_ideas.run()
        build_tracker()
        report()
    elif cmd == "step3":
        import step3_artifacts; step3_artifacts.run(); report()
    elif cmd == "step4":
        import step4_reporters; step4_reporters.run(); report()
    elif cmd == "step5":
        import step5_pitch; step5_pitch.run(); report()
    elif cmd == "sheet":
        build_tracker()
    elif cmd == "report":
        report()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
