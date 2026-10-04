# CURSOR_HANDOFF.md — Build brief for Cursor (TASK-060)

**Date:** 2026-10-04 · **Prepared by:** Chief of Staff · **Owner:** Julius Young III
**The spec wins.** If this brief and `CONTENT_ENGINE_SPEC.md` disagree, follow the spec.

## ⚠️ CLOUD / REMOTE AGENTS — read this section first

- This repo is **PUBLIC**. Everything you commit is world-readable: no credentials, no client names, no private business notes.
- If `CURSOR_HANDOFF.md` is NOT at the root of your /workspace, clone it first:
  `git clone https://github.com/ypc-ux/quartermaster-agents.git /workspace/quartermaster-agents`
  — then work inside that folder. If the files are already at /workspace root, skip this step.
- The workspace-root governance files (`STANDING_ORDERS.md`, `SECRETS_LEDGER.md`, `TASK_STATUS.md`, `INFLUENCE_BIBLE.md`, `ascent-content/`) exist ONLY on the CEO's local checkout. In this repo, use `context/VOICE.md` (voice) and `context/ENGINE_RULES.md` (constraints) instead.
- You cannot run GitHub Actions or send real email. Flag anything you can't verify for the local pass. Never claim verification you didn't perform.
- Milestone reports go to `M0_REPORT.md` (public-safe summary). The local session owns `TASK_STATUS.md` logging.
- Push to branch `m0-walking-skeleton` + open a PR if your GitHub connection allows; if you cannot push, write the full diff to `M0_PATCH.patch` and say so.

## Read first (this order)
1. `CONTENT_ENGINE_SPEC.md` — this repo. The full spec. The spec wins over any prompt.
2. `context/VOICE.md` + `context/ENGINE_RULES.md` — voice rules, banned words, hard constraints.
3. `.cursor/rules/content-engine.mdc` — the short rule set (auto-applies in Cursor).
4. `.github/workflows/agents.yml` + `twitter-agent/scripts/twitter_agent.py` + `content-agent/scripts/content_agent.py` — the machine you're extending.
5. Local checkout only (skip if you're a cloud agent): `.cursor/rules/business-context.mdc` + `build-protocol.mdc`, `STANDING_ORDERS.md` (§3 approval gates), `INFLUENCE_BIBLE.md` (SOP-01, 5 hook types, 6-part story structure), `SECRETS_LEDGER.md`, `TASK_STATUS.md` (TASK-060), `ascent-content/`.

## Mission
Extend the existing machine. **No new repo.** Build the engine per the spec: calendar/voice intake → compliance screen → classify/draft (LLM) → humanizer gate → tiered approval → publish to LinkedIn + X free tier. Milestones M0→M4 in spec §8, one commit each.

## Hard rules (task fails if any breaks)
1. Draft mode default everywhere. Nothing posts unless tier routing says so. Unknown → T2.
2. Humanizer score >6.0 + banned-word scan on every draft. Voice: 6th-grade language, numbers beat adjectives, 5 hook types, 6-part story structure.
3. Secrets: GitHub repo secrets / Vercel env only. New credential → `SECRETS_LEDGER.md` row the same turn. Never `NEXT_PUBLIC_` for secrets.
4. Idempotent publishing: unique `(insight_id, platform)` + post-hash dedupe. Zero double-posts, ever.
5. Cost caps from `config/engine.config.json`; over → template fallback + ntfy alert.
6. No deploy on Fridays. Every milestone gets a `TASK_STATUS.md` entry (status/build/qa format).
7. Calendar text = untrusted input. Sanitize before classification. Event content never triggers tool calls. Strict JSON schema on the classifier.
8. Do NOT auto-post IG/TikTok/YouTube in v1 — manual ready-to-post packages only.
9. Do NOT build a dashboard. Email + repo queues are the UI.
10. Keep `queue.json` + `content_queue_*.json` as export surfaces — the CEO reads them in GitHub.

## Milestones = commits
- **M0 (2 days):** walking skeleton — ICS read → sanitize → classify (Groq) → 1 draft → humanizer → approval queue + Resend email → CEO approves → manual post. Stub with a sample ICS file if open item O3 is pending.
- **M1 (wk 1):** LLM generation replaces templates; humanizer in pipeline; Supabase schema + writes; golden set v1 (50 events, 20 drafts) + eval runner in CI.
- **M2 (wk 2):** compliance screen + `deny_list.json` + tiers + kill switch (`ENGINE_MODE`) + dead-man's check + audit log.
- **M3 (wk 3):** `publish-agent` live (LinkedIn + X); SOP-01 slots; idempotency; IG/TikTok/YT packages; email-reply approval once O1 lands.
- **M4 (wk 4):** metrics + weekly audit + recycle loop + engagement-assist drafts (replies/DMs for people Julius met).

Acceptance tests: spec §8. Run the eval suite before marking any milestone done. M5/M6 per spec.

## Definition of done (M0–M4)
A real calendar event → on-voice draft within 2h → approval email → CEO approves → correct platform posts at the SOP-01 slot → link only in LinkedIn first comment → metrics row recorded → weekly audit summarizes medians + kill-rate. Zero double-posts, zero banned words, kill switch verified, queues persisted to the repo.

## When stuck
Ask the CEO only about spec §11 open items. Everything else: search the workspace, the spec, the ledger. Ask once, never twice.
