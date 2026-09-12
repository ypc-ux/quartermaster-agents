#!/usr/bin/env python3
"""Brainwash OS — 7-layer culture framework as a runnable engine.

Turns a brand into a self-sustaining culture, not a product.
Seven layers: Mind, Exposure, Practices, Artifacts, Protagonists, Aesthetics, Conflict.
Scores any brand on all 7, returns a gap analysis.
"""

import json

LAYERS = [
    {"n": 1, "key": "mind", "name": "Mind",
     "q": "What does this brand believe? Name the laws it runs on.",
     "signal": "13 stated laws a customer could recite back."},
    {"n": 2, "key": "exposure", "name": "Exposure",
     "q": "Where does the belief meet the audience, on what cadence?",
     "signal": "2-3 channels, not six. A 30-day plan, not vibes."},
    {"n": 3, "key": "practices", "name": "Practices",
     "q": "What does the brand do over and over that proves the belief?",
     "signal": "Repeatable rituals, not one-off campaigns."},
    {"n": 4, "key": "artifacts", "name": "Artifacts",
     "q": "What objects carry the belief when you're not in the room?",
     "signal": "Things members keep, share, or wear."},
    {"n": 5, "key": "protagonists", "name": "Protagonists",
     "q": "Who are the heroes of this story? Is the customer one?",
     "signal": "The customer is the hero; the brand is the guide."},
    {"n": 6, "key": "aesthetics", "name": "Aesthetics",
     "q": "What does the belief look like? (type, color, restraint)",
     "signal": "A recognizable look, not a template."},
    {"n": 7, "key": "conflict", "name": "Conflict",
     "q": "What is the enemy? What does the brand rally against?",
     "signal": "A named enemy the audience already hates."},
]

# Archetype lens (Ruler / Outlaw / etc.) — from the Blueprint
ARCHETYPES = {
    "Ruler": "restraint, premium visuals, declarative copy, refuses to compete on price",
    "Outlaw": "confronts the category norm, refuses the standard tropes, tells the uncomfortable truth",
    "Sage": "teaches, cites evidence, never hypes",
    "Creator": "craft-forward, process visible, tolerates imperfection as authenticity",
    "Hero": "proof of effort, underdog arc, before/after",
}


def audit_brand(answers, archetype="Ruler"):
    """Score a brand on all 7 layers. answers = {layer_key: 0-10}."""
    scores = []
    for layer in LAYERS:
        score = answers.get(layer["key"], 0)
        gap = layer["signal"] if score < 7 else "Solid."
        scores.append({"layer": layer["name"], "score": score, "signal": layer["signal"], "gap": gap})
    total = sum(s["score"] for s in scores)
    weakest = min(scores, key=lambda s: s["score"])
    return {
        "total": total,
        "max": 70,
        "pct": round(total / 70 * 100),
        "weakest_layer": weakest["layer"],
        "fix_first": f"Build layer {weakest['layer']}: {weakest['signal']}",
        "archetype": archetype,
        "archetype_shows_up_as": ARCHETYPES.get(archetype, ""),
        "layers": scores,
    }


def build_blueprint(business, audience, enemy, answers):
    """Produce the 7-layer blueprint skeleton a workshop would fill in."""
    return {
        "business": business,
        "audience": audience,
        "enemy": enemy,
        "layers": {l["name"]: {"question": l["q"], "signal": l["signal"]} for l in LAYERS},
        "audit": audit_brand(answers),
    }


if __name__ == "__main__":
    demo = audit_brand(
        {"mind": 9, "exposure": 7, "practices": 5, "artifacts": 3,
         "protagonists": 8, "aesthetics": 9, "conflict": 6},
        archetype="Ruler",
    )
    print(json.dumps(demo, indent=2))
