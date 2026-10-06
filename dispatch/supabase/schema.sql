-- DISPATCH — Supabase schema (system of record)
-- Run once: apply via Supabase SQL editor or Management API.
-- All app access uses the service-role key (server-side only, bypasses RLS).

create schema if not exists dispatch;

-- ① Ingest: calendar events
create table if not exists dispatch.items (
  id uuid primary key default gen_random_uuid(),
  uid text not null unique,
  source text not null default 'calendar',
  title text not null default '',
  description text not null default '',
  location text not null default '',
  start_at timestamptz,
  end_at timestamptz,
  raw jsonb not null default '{}'::jsonb,
  sanitized jsonb not null default '{}'::jsonb,
  compliance text not null default 'pass',      -- pass | deny | hold
  compliance_reason text not null default '',
  tier text not null default 't2',              -- t0 auto | t1 one-tap | t2 manual
  topic text not null default '',
  status text not null default 'new',           -- new | classified | drafted | queued | published | held | rejected | failed
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists items_status_idx on dispatch.items(status);

-- ④ Drafts (one per item+platform+hash — idempotent)
create table if not exists dispatch.drafts (
  id uuid primary key default gen_random_uuid(),
  item_id uuid references dispatch.items(id) on delete cascade,
  platform text not null default 'x',
  body text not null default '',
  payload jsonb not null default '{}'::jsonb,
  banned_hits jsonb not null default '[]'::jsonb,
  voice_score numeric not null default 0,
  status text not null default 'pending',       -- pending | approved | rejected | queued | published | failed
  post_hash text not null,
  fallback boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (item_id, platform, post_hash)
);
create index if not exists drafts_status_idx on dispatch.drafts(status);

-- ⑥ Approval decisions
create table if not exists dispatch.approvals (
  id uuid primary key default gen_random_uuid(),
  draft_id uuid references dispatch.drafts(id) on delete cascade,
  decision text not null,                       -- approved | rejected
  decided_by text not null default 'one-pager',
  reason text not null default '',
  created_at timestamptz not null default now()
);

-- ⑦ Publish log (idempotent by draft+platform+hash)
create table if not exists dispatch.publishes (
  id uuid primary key default gen_random_uuid(),
  draft_id uuid references dispatch.drafts(id) on delete cascade,
  platform text not null default 'x',
  payload_hash text not null,
  status text not null default 'simulated',     -- simulated | posted | failed
  response jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (draft_id, platform, payload_hash)
);

-- ⑧ Runs table — observability
create table if not exists dispatch.runs (
  id uuid primary key default gen_random_uuid(),
  stage text not null,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  status text not null default 'running',       -- running | success | failed
  error text not null default '',
  meta jsonb not null default '{}'::jsonb
);
create index if not exists runs_stage_idx on dispatch.runs(stage, started_at desc);

-- Audit log — every public-facing action
create table if not exists dispatch.audit_log (
  id uuid primary key default gen_random_uuid(),
  action text not null,
  actor text not null default 'engine',
  target text not null default '',
  detail jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists audit_created_idx on dispatch.audit_log(created_at desc);

-- Runtime settings (kill-switch override)
create table if not exists dispatch.settings (
  key text primary key,
  value text not null default '',
  updated_at timestamptz not null default now()
);

-- Daily LLM cost budget
create table if not exists dispatch.budget (
  day date primary key,
  spend_usd numeric not null default 0
);

-- Roles: custom schemas need explicit grants (public schema gets them automatically).
grant usage on schema dispatch to service_role, authenticated, anon;
grant all on all tables in schema dispatch to service_role;
grant all on all sequences in schema dispatch to service_role;
