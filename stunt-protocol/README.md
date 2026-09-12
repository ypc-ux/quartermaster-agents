# Stunt Protocol Engine

**Superagent #1.** A PR stunt is a shape. This finds the shape, makes it impossible without your product, runs it for real with receipts, finds the reporters who covered the originals, and drafts the pitches. Five steps, one tracker, no API keys required.

Based on **The Stunt Shape Protocol** by Angus Sewell.

---

## The Five Steps

| Step | Skill | What It Does |
|---|---|---|
| 1 | `stunt-shapes` | Fetches 5,279 stunts from famouscampaigns.com (live WordPress API), extracts 20 repeatable **shapes** with the brand taken out |
| 2 | `stunt-ideas` | Generates 20 ideas that are **impossible without your product** — the one hard rule |
| 3 | `stunt-log` | Logs **artifacts** with receipts: existed, reaction, number. All three required before pitching |
| 4 | `stunt-list` | Pulls bylines from coverage, finds **reporters** by name + outlet, no scraping |
| 5 | `stunt-pitch` | Drafts **5 personal emails** — subject <30 chars, body <120 words, figure-led |

---

## Run It

```bash
pip install -r requirements.txt

python run.py build      # Steps 1+2, build the Stunt Shape Tracker (.xlsx)
python run.py step3      # Log artifacts
python run.py step4      # Find reporters
python run.py step5      # Draft pitches
python run.py report     # Status across all sheets
```

**Verified working:** Step 1 fetched 300 real stunts live. All 5 steps ran end-to-end.

---

## The Tracker (built automatically)

`data/Stunt_Shape_Tracker.xlsx` — your mini-CRM, five sheets:

- **Stunts** — the shapes you stole, and who covered them
- **Ideas** — your 20, each with the sentence proving only you could run it
- **Artifacts** — proof your stunt actually happened
- **Reporters** — names, beats, profiles
- **Opt-outs** — anyone who told you to stop (checked before every send)

### Row lifecycle

- An idea moves: `drafted → chosen → running → done / dead`
- A reporter moves: `found → verified → pitched → replied → closed`
- Clay-coloured states are terminal. Nothing loops forever.

---

## The Company Line

> We build operating systems for obsessed risk-takers who ship.

Every idea is checked against one rule: **the stunt must be impossible without Quartermaster.** If you could swap the company out and the stunt still works, it's a gimmick — thrown away, rewritten.

---

## The Rule Nobody Follows

A stunt is a claim anyone can check. The whole risk is a claim that **survives being checked**. Sony's fake fan blog got WHOIS'd in 48 hours and confessed. Make the claim real.

Three artifacts before any pitch:
1. **Existed** — a stranger could have walked up to it
2. **Reaction** — somebody outside the company reacted
3. **Number** — one figure a reporter can headline without asking you

---

## Compliance

Steps 4 and 5 never scrape LinkedIn (banned by their agreement — the consequence lands on your account). Search the index, click, read. The pitch prompt writes all five CAN-SPAM elements: real name, real reply-to, honest subject, postal address, opt-out line. Two touches maximum, never three.

---

Part of **Quartermaster** — the operating system for obsessed risk-takers who ship.
