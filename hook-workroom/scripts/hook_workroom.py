#!/usr/bin/env python3
"""Hook Workroom — Quartermaster. Generate and refine hooks for content."""

import json, random
from datetime import datetime
from pathlib import Path

HOOK_TYPES = [
    "curiosity", "bold_statement", "story", "relatable", "question",
    "contrarian", "teaching", "vulnerability", "data_point", "myth_bust"
]

def generate_hooks(topic, n=20, hook_types=None):
    """Generate n hooks for a topic."""
    hook_types = hook_types or HOOK_TYPES
    hooks = []
    
    templates = {
        "curiosity": [
            f"Nobody talks about what happened after {topic}.",
            f"The real reason {topic} works isn't what you think.",
            f"I tested {topic} for 30 days. Here's what broke."
        ],
        "bold_statement": [
            f"{topic} is dead. Here's what replaced it.",
            f"Most people doing {topic} are wasting their time.",
            f"You don't need {topic}. You need this instead."
        ],
        "story": [
            f"Last week I {topic}. It changed everything.",
            f"I failed at {topic} for 2 years. Then I figured this out.",
            f"A client asked me about {topic}. My answer surprised them."
        ],
        "relatable": [
            f"You're going to try {topic} too. Here's how it goes.",
            f"Everyone starts with {topic}. Most quit. Here's why.",
            f"If you've struggled with {topic}, you're not alone."
        ],
        "question": [
            f"What if {topic} was the easy part?",
            f"Why does {topic} work for some people but not others?",
            f"Is {topic} actually worth your time?"
        ],
        "contrarian": [
            f"Everyone says {topic} is smart. It's not.",
            f"Stop doing {topic}. Do this instead.",
            f"The advice about {topic} is backwards."
        ],
        "teaching": [
            f"Here's how to {topic} in 3 steps.",
            f"The framework I use for {topic}.",
            f"Let me show you how {topic} actually works."
        ],
        "vulnerability": [
            f"I was wrong about {topic}. Here's what I learned.",
            f"I almost quit {topic}. Here's what kept me going.",
            f"The truth about {topic} that nobody posts."
        ],
        "data_point": [
            f"83% of {topic} attempts fail. Here's why.",
            f"I tracked {topic} for 6 months. The numbers are wild.",
            f"One stat about {topic} changed my entire approach."
        ],
        "myth_bust": [
            f"The biggest myth about {topic}.",
            f"Stop believing this about {topic}.",
            f"What they don't tell you about {topic}."
        ]
    }
    
    for i in range(n):
        htype = random.choice(hook_types)
        base = random.choice(templates.get(htype, [f"Hook about {topic}"]))
        words = base.split()
        if len(words) > 12:
            base = " ".join(words[:12])
        hooks.append({
            "id": i + 1,
            "type": htype,
            "hook": base,
            "words": len(base.split()),
            "topic": topic,
            "status": "draft"
        })
    
    return hooks

def score_hook(hook):
    """Score a hook on clarity, curiosity, and speakability."""
    words = hook.split()
    clarity = min(10, max(1, 10 - abs(len(words) - 8)))
    curiosity = 8 if any(w in hook.lower() for w in ["why", "how", "what", "secret", "truth"]) else 5
    speakable = 9 if len(words) <= 10 else 6
    return {
        "hook": hook,
        "scores": {"clarity": clarity, "curiosity": curiosity, "speakable": speakable},
        "total": clarity + curiosity + speakable,
        "max": 30
    }

def run(topic="building agency systems", n=20):
    """Generate and score hooks."""
    print(f"[Hook Workroom] Generating {n} hooks for '{topic}'...")
    hooks = generate_hooks(topic, n)
    scored = [score_hook(h["hook"]) for h in hooks]
    
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    
    result = {
        "topic": topic,
        "generated_at": datetime.now().isoformat(),
        "hooks": hooks,
        "scores": scored,
        "top_5": sorted(scored, key=lambda x: x["total"], reverse=True)[:5]
    }
    
    out_path = out_dir / f"hooks_{topic.replace(' ', '_')}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"[Hook Workroom] Generated {n} hooks")
    print(f"  Top hook: {result['top_5'][0]['hook']}")
    print(f"  Score: {result['top_5'][0]['total']}/30")
    print(f"  Saved to: {out_path}")
    return result

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "building agency systems"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    run(topic, n)
