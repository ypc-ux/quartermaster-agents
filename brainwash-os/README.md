# Brainwash OS — Culture Agent

**Superagent.** A 7-layer culture framework that turns a brand into a self-sustaining culture, not a product.

## What It Does

Runs a brand audit across 7 layers:
1. **Mind** — What does this brand believe? The laws it runs on.
2. **Exposure** — Where does the belief meet the audience, on what cadence?
3. **Practices** — What does the brand do over and over that proves the belief?
4. **Artifacts** — What objects carry the belief when you're not in the room?
5. **Protagonists** — Who are the heroes? Is the customer one?
6. **Aesthetics** — What does the belief look like?
7. **Conflict** — What is the enemy? What does the brand rally against?

## Run It

```bash
python scripts/brainwash_os.py
```

Returns a JSON audit with scores (0-10 per layer), identifies the weakest layer, and suggests what to fix first.

## Archetype Lens

Supports Ruler, Outlaw, Sage, Creator, Hero archetypes. Each archetype shows up differently in the audit.

## Example Output

```json
{
  "total": 47,
  "max": 70,
  "pct": 67,
  "weakest_layer": "Artifacts",
  "fix_first": "Build layer Artifacts: Things members keep, share, or wear.",
  "archetype": "Ruler"
}
```

---

Part of **Quartermaster** — the operating system for obsessed risk-takers who ship.