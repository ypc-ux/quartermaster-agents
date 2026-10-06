# DISPATCH — MVP Plan

**"Your calendar in. Content out. Nothing ships without approval."**

The calendar dispatches; the engine turns each one into a dispatch. One word, works as a
domain/app name, operator energy. "Boardroom Engine" stays as the internal codename so the
existing TASK-060 spec/handoff stay valid; DISPATCH is the product + the Vercel project + this folder.

---

## The worst way (what we will not do)

1. Pretty dashboard first, fake data — demos great, never runs.
2. Hardcoded templates — output is slop nobody approves.
3. One mega-prompt does everything — non-deterministic, un-debuggable.
4. JSON files in the repo as the only state — race conditions, lost writes.
5. No idempotency — every cron run re-drafts/re-posts.
6. No compliance screen — private life leaks to public feeds, irreversible.
7. Auto-post everything — one bad draft burns the brand.
8. Secrets in the frontend (`NEXT_PUBLIC_`) — keys world-readable.
9. One giant function, no logs, no retries — silent failure.
10. Deploy Friday, verify nothing, claim done.

The failure mode in one line: *it looks like a product and behaves like a slideshow.*

## First principles

1. **Content is a pipeline with explicit state.** Status + next action per item. State lives in a database.
2. **Deterministic-first.** Parsing, dedupe, scheduling, tiering, publishing = plain code. The LLM only does judgment (classify, draft).
3. **Idempotent at every stage.** Run everything twice → nothing changes (unique keys + claim-by-status-transition).
4. **Calendar text is hostile input.** Sanitize; strict JSON schema; event content never triggers tool calls.
5. **The filter is the product.** Kill-rate ≥70% is the KPI. A gate (humanizer + banned words + compliance) sits between generation and the world.
6. **Human approval is a feature**, tiered (T0 auto / T1 one-tap / T2 manual; unknown → T2), never a limitation.
7. **Secrets server-side only.** Every external call gets a cost cap, a retry, and an audit row.
8. **Observability is part of "works."** Runs table, `/api/status`, dead-man's switch, audit log.
9. **The UI is a window.** The engine runs with the browser closed. The page only reads and approves.
10. **Ship the walking skeleton end-to-end first** (thin slice through all 8 stages), then widen one stage at a time.

## The pipeline

One Next.js app on Vercel + Supabase as state + Vercel Cron as the heartbeat.

| Stage | Runs as | Deterministic? | Writes |
|---|---|---|---|
| ① Ingest | `/api/cron/ingest` (15 min) | Yes — ICS parse, sanitize, upsert by event UID | `items` |
| ② Compliance screen | inline in generate | Yes — deny-list + tier rules | `items.tier` |
| ③ Classify | OpenRouter `:free` (Groq optional via env), strict JSON | LLM (judgment) | `items.topic` |
| ④ Draft | OpenRouter + `context/VOICE.md` rules | LLM (judgment) | `drafts` |
| ⑤ Humanizer gate | code — banned-word scan + score > 6.0 | Yes — hard gate | `drafts.status` |
| ⑥ Approval | `/api/approve` + one-pager + Resend email | Human (T1) | `approvals` |
| ⑦ Publish | `/api/cron/publish` (SOP-01 slots) | Yes — idempotent by `(item_id, platform, hash)` | `publishes` |
| ⑧ Metrics + audit | `/api/status`, runs table, dead-man check | Yes | `runs`, `audit_log` |

Guardrails wrapped around all of it: `ENGINE_MODE` kill switch checked at every stage (env +
runtime override row in `settings`) · cost caps with template fallback · exponential backoff
(max 3) · audit row per public action · zero `NEXT_PUBLIC_` secrets.

## MVP scope

**In (walking skeleton through every stage):**
- Sample ICS + real ICS support (env `GCAL_ICS_URL`) → items → classify → draft → gate → queue → approve → publish-log
- The one-pager with live status + approve/reject buttons
- Supabase tables: `items, drafts, approvals, publishes, runs, audit_log, settings, budget`
- Kill switch, cost cap, idempotency, `/api/status`, Resend notification on new drafts
- Deployed on Vercel with Vercel Cron

**Out (deliberately):** LinkedIn publish (O5), X live publish (O2 — draft mode until then),
voice memos, IG/TikTok packages, metrics learning loop, email-reply approval (O1).

## The one-pager

- Palette lock: 60% black `#000000`/`#0A0A0A`, 30% silver `#C0C0C0`, 10% purple `#A855F7` · Inter only · green `#00FF88` for live/success only
- 7 sections collapsed into one page: Hero → Pipeline (8 stages, live status dots) → Live KPIs (kill-rate, drafts pending, approved, published) → The Queue (approve/reject cards) → Proof (last 5 audit rows) → CTA ×3 (Approve queue · Open status JSON · Kill switch)
- Rules: <2s load, mobile 375 works, no decorative motion, every number has a source
- Honest framing: the front-end is a *window*, not the engine — it works with the tab closed

## Deploy facts

| Item | Value |
|---|---|
| Code location | `quartermaster-agents/dispatch/` (extends existing repo) |
| Vercel project | `dispatch` (team youngprivatecapital), root = this dir |
| Cron | ingest+generate `*/15 * * * *` · publish `0 8,12,17 * * 1-5` |
| State | Supabase `ntiufwvjebzwvkpavrtr` (ledger) |
| Env (server-side only) | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE`, `OPENROUTER_API_KEY`, `RESEND_API_KEY`, `ENGINE_MODE=draft`, `CRON_SECRET`, `DISPATCH_NOTIFY_EMAIL`, `GCAL_ICS_URL` (optional), `X_*` (optional), `GROQ_API_KEY` (optional — classify falls back to OpenRouter `:free`) |

## Definition of done ("actually works")

1. A calendar event → an on-voice, gate-passed draft in the queue within 15 minutes
2. Approve → publish row written (in `draft` mode: "would post", with the exact payload logged)
3. **Idempotency proof:** trigger every cron twice → zero duplicates
4. **Kill switch proof:** `ENGINE_MODE=paused` → all stages no-op within one cycle
5. **Compliance proof:** a test event containing deny-list terms auto-held as T2 (never stored verbatim)
6. **Dead-man proof:** `/api/status` shows last-success per stage; stale >6h → flagged
7. Banned-word scan = 0 hits on every draft
8. Zero secrets in the client bundle (grep the build output)
9. Playwright screenshots at 1920/1440/375 + TASK_STATUS entry

## Build order

0. Persist this plan + TASK-066 entry — DONE
1. Supabase schema + `/api/status` (prove the pipe exists before anything flows)
2. Ingest (sample ICS → real) + idempotent upsert
3. Compliance screen + tier assignment
4. Classify (OpenRouter `:free` / Groq) → Draft (OpenRouter) → humanizer gate
5. Approval surface (one-pager + Resend)
6. Publish (draft-mode first, then X when O2 lands)
7. Guardrails: kill switch, cost caps, retries, audit
8. One-pager per the Design Bible
9. Deploy + the 9 acceptance tests + log

*"Boardroom Engine" remains the internal codename (TASK-060). DISPATCH is the product.*

