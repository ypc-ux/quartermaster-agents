# DISPATCH

**Your calendar in. Content out. Nothing ships without approval.**

A calendar-to-content pipeline: one Next.js app on Vercel + Supabase as state + Vercel Cron
as the heartbeat. Internal codename: the Boardroom Engine (TASK-060). This folder is the
walking skeleton — a thin slice through every stage, with the browser closed.

```
Calendar (ICS) → ① Ingest → ② Compliance screen → ③ Classify → ④ Draft → ⑤ Humanizer gate
→ ⑥ Approval → ⑦ Publish → ⑧ Metrics + audit
```

## Stages

| Stage | Route | Runs as |
|---|---|---|
| Ingest | `/api/cron/ingest` | Deterministic ICS parse + sanitize + idempotent upsert by event UID |
| Compliance | inline in generate | Deny-list (redacted, never stored verbatim) + tier rules (T0/T1/T2; unknown → T2) |
| Classify | inline in generate | LLM judgment (OpenRouter `:free`, Groq optional), strict JSON |
| Draft | inline in generate | LLM judgment + voice rules (`context/VOICE.md`) |
| Humanizer gate | inline in generate | Deterministic code: banned words = 0 AND score > 6.0 |
| Approval | one-pager + `/api/approve` | Human (T1 one-tap / T2 manual); Resend email on new drafts |
| Publish | `/api/cron/publish` | Idempotent by `(item_id, platform, hash)`; draft mode logs "would post" |
| Status | `/api/status` | Counts, last-success per stage, kill-rate, budget — public JSON, no content |

## Guardrails

- `ENGINE_MODE` = `active | draft | paused`, checked at every stage. Runtime override row in
  `dispatch.settings` (the one-pager kill switch) beats the env var.
- Cost cap: `LLM_DAILY_BUDGET_USD` per day → deterministic template fallback.
- Retries: exponential backoff, max 3. Audit row per public action.
- Idempotency: upsert by UID, claim-by-status-transition, unique `(item_id, platform, post_hash)`.
- Zero `NEXT_PUBLIC_` secrets. All keys server-side only (Vercel env / `.env.local`, gitignored).

## Local run

```bash
npm install
cp .env.example .env.local   # fill from the secrets ledger
npm run dev
```

Cron endpoints require `Authorization: Bearer $CRON_SECRET`.
Sample ICS is bundled (`src/lib/sample.ts`) until `GCAL_ICS_URL` is set.

## Deploy

```bash
vercel --prod    # project: dispatch, root: this directory
```

Crons (vercel.json): ingest + generate every 15 min; publish at 8/12/17 UTC on weekdays.

## Open items

| # | Item | Blocks |
|---|---|---|
| O3 | Google Calendar secret ICS URL | Real calendar intake (sample ICS works today) |
| O2 | X developer keys | Live posting (draft-mode publish log works today) |
| O5 | LinkedIn OAuth | LinkedIn posting |

## Schema

`supabase/schema.sql` — tables: `items, drafts, approvals, publishes, runs, audit_log, settings, budget`.

*The engine runs with the browser closed. The page is a window.*
