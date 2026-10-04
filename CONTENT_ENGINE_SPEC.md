# CONTENT_ENGINE_SPEC.md — The Boardroom Engine (TASK-060)

**Status:** SPEC_READY → assigned to Builder
**Created:** 2026-10-04 · **Author:** Chief of Staff (Architect pass)
**Repo:** github.com/ypc-ux/quartermaster-agents — **PUBLIC. Treat every commit as world-readable.**
**Local checkout:** workspace `chat/quartermaster-agents` (governance files live only there)
**Handoff brief:** `CURSOR_HANDOFF.md` (same folder) — Cursor reads that first.

---

## 0. Decisions locked (CEO, 2026-10-04)

| # | Decision | Effect |
|---|---|---|
| 1 | **Distribution v1 = $0 native.** LinkedIn API (self-serve member posting) + X free tier (1,500 posts/mo, text-only). | No Postiz/Ayrshare spend in v1. IG/TikTok/YouTube = manual ready-to-post packages. |
| 2 | **Autonomy = tiered.** T0 auto / T1 one-tap / T2 manual. Unknown → T2. | §6. Zero auto-posting of raw calendar text, ever. |
| 3 | **State = Supabase** (project ref lives in the local `SECRETS_LEDGER.md` — never committed) as system of record. | Repo JSON queues stay as the human-review surface (CEO reads them in GitHub). |
| 4 | **Approval v1 = repo-file queue** (`approval/pending → approved/rejected`) + Resend email notify. | Email-reply approval = M3 upgrade, blocked only on O1. |
| 5 | **Voice:** Groq Whisper for intake now; ElevenLabs clone deferred to M5 (own voice only, disclosed on every synthetic piece). | EU AI Act Art. 50 transparency is in force (since Aug 2026). |
| 6 | **Newsletter = Resend** (already wired). | Sunday recap = best of the week + one recycled winner. |
| 7 | **Brand = black/silver/purple lock** (`DESIGN.md`). | Patch the cyan section in `INFLUENCE_BIBLE.md` Part 1 (open item O4). |

## 1. Problem

Julius runs SOP-01 (45 min/day: Capture → Ship → Connect) by hand. The existing agents (`twitter-agent`, `content-agent`) fill queues with hardcoded template content in the wrong persona (old "agency/Stripe" voice). Nothing reads the calendar or voice notes. Nothing can post. There is no compliance screen between private life (Secria internals, counsel matters, client deals, financials) and public feeds. Result: the machine runs every 2 hours and ships nothing. TASK-051 (Twitter keys) has sat blocked since 2026-09 because the answer was never written down: **X's free tier gives 1,500 posts/month**.

## 2. Solution — the pipeline

```
Voice memo ──┐
GCal ICS ────┼→ Insight Store (Supabase) → ① Compliance Screen → ② Classifier
DMs/notes ───┘      (Groq free, strict JSON schema) → ③ Draft Studio (OpenRouter/
                    Groq + brand rules + style-RAG + hook-workroom) → ④ Humanizer
                    gate (>6.0) → ⑤ Tier + Approval (repo queue + Resend email) →
                    ⑥ Scheduler (fixed SOP-01 slots) → ⑦ Publish (LinkedIn API +
                    X free tier; manual packages for IG/TikTok/YT) → ⑧ Metrics
                    ingest → ⑨ Weekly audit + recycle (brand-vault) → back to ①

Kill switch (ENGINE_MODE) · dead-man's switch (ntfy) · audit log · cost caps ·
idempotency — wrap everything.
```

## 3. What exists / what we extend

| Asset | Disposition |
|---|---|
| `.github/workflows/agents.yml` | **EXTEND** — add `calendar-agent`, `publish-agent`, `metrics-agent` jobs; keep the persist job pattern |
| `twitter-agent/` | **UPGRADE** — replace random templates with LLM drafts; keep draft-mode flag; keep `queue.json` as export surface |
| `content-agent/` | **UPGRADE** — same; humanizer gate before any queue write |
| `inbox-agent/` | **REUSE (M3)** — email-reply approval once O1 lands |
| `hook-workroom/` | **REUSE** — feed its 20+ hooks/topic into Draft Studio |
| `brand-vault/repurposer.py` | **REUSE (M4)** — recycle loop |
| `ops-digest/`, `sunday-reset/` | **REUSE (M4)** — weekly audit |
| `analytics-agent/` | **REUSE (M4)** — metrics formatting |
| ntfy alert pattern (`NTFY_TOPIC`) | **REUSE** — failure + dead-man alerts |
| Supabase MCP / REST | **USE** — schema in `supabase/schema.sql` |
| `ascent-content/twitter/` (local checkout only) | **SEED CORPUS** — on-brand tweets/threads for style-RAG examples (cloud agents use `context/VOICE.md`) |

## 4. New files

| Path | Purpose |
|---|---|
| `calendar-agent/scripts/calendar_agent.py` | ICS poll (2h) → sanitize → classify → write insights to Supabase + approval queue |
| `calendar-agent/requirements.txt` | `ics` (or `icalendar`), HTTP client for OpenRouter/Groq |
| `publish-agent/scripts/publish_agent.py` | Claims approved drafts → posts LinkedIn (requests) + X (tweepy) → idempotent, retries, backoff |
| `metrics-agent/scripts/metrics_agent.py` | Pulls LinkedIn/X numbers where free endpoints allow; manual CSV import fallback |
| `compliance/deny_list.json` | Deny-list terms (§6) |
| `compliance/rules.md` | The screen's checks, in order |
| `golden_set/events_sample.json` | 50 labeled events (category, tier, expected action) |
| `golden_set/drafts_sample.json` | 20 drafts with humanizer scores |
| `config/engine.config.json` | Tiers, caps (≤2 posts/day), slots (SOP-01), LLM budget, allowlisted calendars |
| `supabase/schema.sql` | Tables + idempotency keys (§5) |
| `approval/pending/` `approved/` `rejected/` | Repo-file approval queue; persist job commits it |

## 5. Data model (Supabase — project ref in local `SECRETS_LEDGER.md`)

| Table | Key columns | Notes |
|---|---|---|
| `insights` | id, source (ics|voice|manual), raw_hash, sanitized_text, category, tier, score, status | Raw text stored only after sanitize; deny-list hits are never stored |
| `drafts` | id, insight_id, platform, variant, body, humanizer_score, hook_type, tier, status | UNIQUE (insight_id, platform, variant) |
| `approvals` | id, draft_id, sent_at, action, acted_at, actor | One row per decision |
| `posts` | id, draft_id UNIQUE, platform, external_id, posted_at, permalink, post_hash | post_hash = dedupe guard |
| `metrics` | post_id, date, impressions, engagements, clicks, profile_visits, source | Append-only |
| `deny_list` | id, term, type (client|org|person|topic), reason, added_at | |
| `golden_set` | id, kind (event|draft), input, expected, notes | |
| `audit_log` | id, actor, action, payload_json, ts | Every public-facing action gets a row |
| `budget` | day, llm_spend, posts_published | |

## 6. Compliance screen + risk tiers

Screen runs BEFORE the classifier, in this order:
1. **Allowlist** — only events from calendars in `engine.config`. Never process attendee-supplied text (prompt injection).
2. **Deny-list match** — org/name/term in `deny_list.json` → block + log; raw text never stored.
3. **PII scan** — emails, phones, financial figures → strip or hold.
4. **Materiality flag** — public companies, unannounced product, counsel matters → force T2.
5. **Sanitize** — strip links, attachments, invite bodies.

| Tier | Class | Action | CEO time |
|---|---|---|---|
| T0 | Recycled evergreen frameworks; previously-approved winners with new hooks | Auto-post after compliance + humanizer pass; cap 2/wk | 0 |
| T1 | Voice-note insights, anonymized lessons, industry takes, follow-ups | Land in `approval/pending`; email with draft; CEO flips file (M3: email reply) | ~10 sec |
| T2 | Client-named, Secria non-public, counsel, financials, any screen failure | Held in `approval/rejected` with reason; explicit rewrite only | minutes, rare |

Default for unknown = T2. No exceptions.

## 7. Platform rules (verified 2026-10)

| Platform | Rule |
|---|---|
| LinkedIn | Self-serve member posting (`w_member_social`); text + images ok; no native scheduling — we queue ourselves; **links go in the first comment**, never the post body; ≤1 post/day v1 |
| X | Free tier = 1,500 posts/mo, **text-only** (no media upload), 1 app / 1 user; ≤2 posts/day v1; no links on X posts in v1 (reach penalty + free-tier limits); threads = chained creates |
| IG / TikTok / YouTube | `publish-agent` does NOT post. M3 builds ready-to-post packages (caption, media spec, posting time, first-comment text) into the approval queue. Julius posts manually. |
| Newsletter | Sunday recap via Resend = best of the week + one recycled winner. |

## 8. Milestones

| M | Scope | Acceptance |
|---|---|---|
| **M0 (2 days)** | Walking skeleton: ICS → sanitize → classify (Groq) → 1 draft → humanizer → approval queue + Resend email → CEO approves → manual post | A real calendar event becomes an on-voice, compliance-passed draft within 2h; approval file flips; zero banned words |
| **M1 (wk 1)** | Replace twitter/content template generators with LLM + brand rules + style-RAG; humanizer in pipeline; Supabase schema + writes; golden set v1 + eval runner in CI | ≥70% of drafts approved with light edits; banned-word scan = 0 hits; evals pass in CI |
| **M2 (wk 2)** | Compliance screen + deny_list + tier assignment + kill switch (`ENGINE_MODE`) + dead-man's check + audit log | Test event mentioning Secria internals auto-held; kill switch stops everything in one cron cycle |
| **M3 (wk 3)** | `publish-agent` live (LinkedIn + X); fixed SOP-01 slots; idempotency; IG/TikTok/YT packages; email-reply approval once O1 lands | 5 consecutive days at correct slots, zero double-posts; links only in LinkedIn first comment |
| **M4 (wk 4)** | metrics-agent + weekly audit email + recycle loop (brand-vault) + engagement-assist drafts (replies/DMs for people Julius met) | Sunday audit lands with medians + kill-rate; 2 recycled winners shipped |
| **M5 (wk 5)** | Voice intake (Groq Whisper) live; ElevenLabs own-voice clone + disclosure; OpenMontage video experiment | A voice memo becomes a draft <5 min; synthetic audio carries disclosure label |
| **M6 (wk 6+)** | Learning loop only at n≥100 posts; bandit for slots; platform expansion; 3 custom skills | Optimization decisions are statistically honest |

Every milestone: build passes, security checklist, QA, TASK_STATUS entry. **No deploy on Fridays.**

## 9. Security & ops

- `ENGINE_MODE` env (`active|draft|paused`) checked at every stage. GitHub variable = kill switch.
- Dead-man's switch: ops-digest job checks each agent's last-success timestamp; >6h stale → ntfy alert.
- Idempotency: unique `(insight_id, platform)` + post_hash dedupe; claim drafts with an atomic file move (rename) in the repo queue.
- Retries: exponential backoff, max 3; failure → ntfy + status row.
- Secrets: GitHub repo secrets + Vercel env only. Never `NEXT_PUBLIC_`. New credential → `SECRETS_LEDGER.md` same turn.
- Cost caps: daily LLM budget in `engine.config`; over → template fallback + ntfy. Groq free tier first; OpenRouter for final polish.
- Prompt injection: calendar text is untrusted input. Sanitize before classification. Event content never triggers tool calls. Strict JSON schema on the classifier.
- Audit log: every public-facing action gets an `audit_log` row (who/what/when/hash).

## 10. KPIs

| Layer | KPIs |
|---|---|
| System | kill-rate ≥70% · approval latency <60 sec/day · publish reliability >95% · double-posts = 0 · LLM cost ≤$5/mo · human-minutes-per-piece falling monthly |
| Content | **median** engagement rate trend (never max) · profile visits · inbound DMs · newsletter replies |
| Funnel | meetings attributed to content (UTM on LinkedIn first-comment links) · Skool joins · content-sourced opportunities logged back to the calendar |
| Anti-KPIs | never optimize for raw post count; never chase the viral outlier |

## 11. Open items (owner steps — the only human wiring)

| # | Item | Steps | Blocks |
|---|---|---|---|
| O1 | Resend full-access key + MX | Resend dashboard key + Google Domains MX `inbound-smtp.us-east-1.amazonaws.com` (10 min, one sitting) | Only email-REPLY approval; repo-file approval works today |
| O2 | X developer app keys | developer.x.com → free app → 5 keys → GitHub repo secrets | X posting (M3) |
| O3 | Google Calendar secret ICS URL | Calendar → settings → "Secret address in iCal format" → GitHub secret | Calendar intake (M0 — builder stubs with sample ICS) |
| O4 | Brand color patch | `INFLUENCE_BIBLE.md` Part 1 cyan section → black/silver/purple (`DESIGN.md` lock) | Visual assets only (M3+) |
| O5 | LinkedIn OAuth | Create app → `w_member_social` → 3-legged OAuth as Julius → store refresh token | LinkedIn posting (M3) |

## 12. Definition of done (M0–M4)

A real calendar event → on-voice draft within 2h → approval email → CEO approves → correct platform posts at the SOP-01 slot → link only in LinkedIn first comment → metrics row recorded → weekly audit summarizes medians + kill-rate. Zero double-posts, zero banned words, kill switch verified, queues persisted to the repo.

## 13. Scoring (per .clinerules)

- Every code diff: Priming-for-Code ≥ 5.0 (BLOCK below).
- Every draft: humanizer > 6.0 + banned-word scan.
- Classifier: eval on `golden_set` before every prompt change.
- Handoff: Builder → Tester QA → Main logs. TASK-060 tracks the whole run.


