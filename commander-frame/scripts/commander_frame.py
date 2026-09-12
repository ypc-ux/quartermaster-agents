#!/usr/bin/env python3
"""Commander Frame — Julius's marketing mind, as a runnable engine.

Diagnostic before persuasive, blunt before polished, attribution before activity.
Runs every marketing question through 6 stages, then picks 2-4 heuristics/triggers.
Never fabricates scarcity, urgency, stats, or social proof.
"""

import json, random

# ─── Stage 2: Value Equation ─────────────────────────────────────────────────
def value_equation(dream, likelihood, time_delay, effort):
    """(Dream x Likelihood) / (Time x Effort). Weakest variable = the real problem."""
    try:
        score = (dream * likelihood) / (time_delay * effort)
    except ZeroDivisionError:
        score = float("inf")
    normalized = {
        "dream_outcome": dream / 10,
        "perceived_likelihood": likelihood / 10,
        "time_delay": 1 - min(time_delay, 10) / 10,
        "effort": 1 - min(effort, 10) / 10,
    }
    weakest = min(normalized, key=normalized.get)
    return {"score": round(score, 2), "weakest": weakest,
            "fix_first": f"Fix {weakest.replace('_', ' ')} before touching the copy."}


# ─── Stage 3: Attribution Check (the marketing-theater filter) ───────────────
def attribution_check(claim, has_real_number):
    if has_real_number:
        return {"verdict": "keep", "reason": "Ties to a real, attributable result."}
    return {"verdict": "flag", "reason": "No real number. Marketing theater — cut it or get the number."}


# ─── Stage 1: Pain Diagnosis ─────────────────────────────────────────────────
PAIN_PATTERNS = [
    ("I need more leads", "I'm afraid I'm not good enough and it's starting to show"),
    ("I need better copy", "I don't trust that my offer is worth the price"),
    ("I need more followers", "I'm invisible and running out of time"),
]


def diagnose_pain(surface_pain):
    for surface, real in PAIN_PATTERNS:
        if surface.lower() in surface_pain.lower():
            return {"surface": surface, "real": real}
    return {"surface": surface_pain, "real": "(name the fear underneath — ask the buyer in their words)"}


# ─── Stage 5: Heuristic + Trigger Selection (pick 2-4, never more) ──────────
HEURISTICS = {
    "reward": "Reward super-response — lead with the incentive",
    "loss_aversion": "Deprival super-reaction — frame as get-it-or-lose-it",
    "social_proof": "Social proof — real numbers, not testimonials",
    "authority": "Authority misinfluence — borrowed or built authority",
    "scarcity": "Scarcity bias — cap it for real",
    "urgency": "Urgency bias — a real time-bound reason",
    "disarming_honesty": "Disarming honesty — state the true limitation, then pivot",
    "conviction": "Conviction bias — stated confidence is believed regardless of merit",
    "pattern_break": "Pattern break — anything that reads 'typical ad' gets binned",
    "quantitative_specificity": "Quantitative specificity — 83.3% beats 'most'",
    "zero_risk": "Zero risk bias — frame staying put as the risky option",
    "reason_why": "Reason-respecting — add 'because ___' after every CTA",
}

TRIGGERS = {
    "fomo": "FOMO — don't let a worse fit scoop it up",
    "testimonials": "Testimonials + popularity metrics",
    "anchoring": "Anchoring — first number sets the scale",
    "confirmation": "Confirmation bias — confirm what they believe, extend it",
    "ikea": "Ikea effect — let them conclude it themselves",
    "reciprocity": "Reciprocity — give first",
    "commitment": "Commitment & consistency — foot in the door",
    "curiosity": "Curiosity — leave the loop open",
    "time_urgency": "Time-based urgency",
}


def select_levers(count=3, seed=None):
    """Pick 2-4 heuristics + triggers combined. Overdone-it bias: never stack more."""
    if seed:
        random.seed(seed)
    count = max(2, min(4, count))
    h = random.sample(list(HEURISTICS.keys()), min(2, count))
    t = random.sample(list(TRIGGERS.keys()), max(0, count - len(h)))
    picks = [{"type": "heuristic", "key": k, "desc": HEURISTICS[k]} for k in h] + \
            [{"type": "trigger", "key": k, "desc": TRIGGERS[k]} for k in t]
    return {"picks": picks, "count": len(picks),
            "warning": "Overdone-it bias: more than 4 reads as manipulative." if count >= 4 else ""}


# ─── Stage 6: Objection Preemption ───────────────────────────────────────────
def preempt_objections(objections):
    return [{"objection": o, "answer_with": "Preempt this in the output — don't stay silent."} for o in objections]


def run_diagnostic(offer, surface_pain="I need more leads", dream=8, likelihood=5,
                   time_delay=6, effort=7, has_real_number=False, objections=None):
    """Run all 6 stages in order. Weak output traces back to a skipped stage."""
    return {
        "1_pain": diagnose_pain(surface_pain),
        "2_value_equation": value_equation(dream, likelihood, time_delay, effort),
        "3_attribution": attribution_check(offer, has_real_number),
        "4_voice": "Match how the owner actually talks — blunt, direct, no hedging.",
        "5_levers": select_levers(3),
        "6_objections": preempt_objections(objections or ["Is this real?", "Why now?", "Why you?"]),
    }


if __name__ == "__main__":
    result = run_diagnostic(
        offer="We build operating systems for obsessed risk-takers who ship.",
        surface_pain="I need more leads",
        dream=9, likelihood=6, time_delay=4, effort=5, has_real_number=True,
    )
    print(json.dumps(result, indent=2))
