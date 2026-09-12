# Brand Vault — Personal Brand Vault + Repurposer

**Superagent.** Takes ONE business update, win, or feature and chops it into platform-native content for X, Instagram, LinkedIn, TikTok, email, and blog.

## What It Does

- **Repurpose**: 1 idea → 6 platforms (X, Instagram, LinkedIn, TikTok, email, blog)
- **Hook Generation**: 10 opening hooks per idea, labelled by type (curiosity, bold statement, story, relatable, question, contrarian)
- **Pillar Balance**: Checks if your recent posts are balanced across content pillars (ship, money, mind, proof)

## Run It

```bash
python scripts/repurposer.py "shipped 20 connected agents in 12 hours"
```

Outputs to `data/repurposed.json` with all platform pieces + 10 hooks.

## Content Pillars

- **ship** — Shipping fast, build in public, velocity, receipts
- **money** — Making money, cash flow, offers, the actual numbers
- **mind** — Builder mindset, discipline, focus, ignoring noise
- **proof** — Results, teardowns, before/after, case studies

## Example

Input: "shipped 20 connected agents in 12 hours"

Output:
- **X**: Tweet + thread (5 tweets)
- **Instagram**: 5-slide carousel + caption
- **LinkedIn**: Post with engagement question
- **TikTok**: Hook + 3 beats + length (45-60s)
- **Email**: Subject line + body
- **Blog**: Full post with intro, situation, why it matters, the play

Plus 10 hooks like:
- `[curiosity] Nobody talks about what happened after shipped 20 connected agents in 12 hours.`
- `[bold_statement] shipped 20 connected agents in 12 hours. Here's the part nobody posts.`

---

Part of **Quartermaster** — the operating system for obsessed risk-takers who ship.