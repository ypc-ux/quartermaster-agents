# Commander Frame — Positioning Agent

**Superagent.** Julius's marketing mind as a runnable engine. Diagnostic before persuasive, blunt before polished, attribution before activity.

## What It Does

Runs every marketing question through 6 stages:

1. **Pain Diagnosis** — Name the fear underneath the surface pain
2. **Value Equation** — (Dream × Likelihood) / (Time × Effort). Weakest variable = the real problem.
3. **Attribution Check** — Does the claim tie to a real, attributable result? If not, it's marketing theater.
4. **Voice Match** — Match how the owner actually talks (blunt, direct, no hedging)
5. **Heuristic + Trigger Selection** — Pick 2-4 levers, never more (overdone-it bias)
6. **Objection Preemption** — Answer the top 3 objections before they're asked

## Run It

```bash
python scripts/commander_frame.py
```

Returns a JSON diagnostic with all 6 stages.

## Heuristics & Triggers

**Heuristics** (pick 2-4):
- Reward super-response, Loss aversion, Social proof, Authority, Scarcity, Urgency, Disarming honesty, Conviction, Pattern break, Quantitative specificity, Zero risk, Reason-why

**Triggers**:
- FOMO, Testimonials, Anchoring, Confirmation bias, Ikea effect, Reciprocity, Commitment & consistency, Curiosity, Time-based urgency

## The Marketing-Theater Filter

```python
attribution_check("We built an agency OS", has_real_number=True)
# → {"verdict": "keep", "reason": "Ties to a real, attributable result."}

attribution_check("We built an agency OS", has_real_number=False)
# → {"verdict": "flag", "reason": "No real number. Marketing theater — cut it or get the number."}
```

Never fabricates scarcity, urgency, stats, or social proof.

---

Part of **Quartermaster** — the operating system for obsessed risk-takers who ship.