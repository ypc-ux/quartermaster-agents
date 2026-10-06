// ⑧ /api/status — public JSON: counts, last-success per stage, kill-rate, budget.
// Never exposes content, only numbers + timestamps.

import { NextRequest } from 'next/server';
import { getSupabase } from '@/lib/supabase';
import { engineMode } from '@/lib/guardrails';

export const dynamic = 'force-dynamic';

function tally(rows: { status: string }[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const r of rows) {
    const k = r.status || 'unknown';
    out[k] = (out[k] ?? 0) + 1;
  }
  return out;
}

export async function GET(_req: NextRequest): Promise<Response> {
  const sb = getSupabase();
  const mode = await engineMode();
  const now = Date.now();
  const STALE_MS = 6 * 60 * 60 * 1000;

  const [itemsRows, draftsRows, lastRuns, recentAudit, budgetRow] = await Promise.all([
    sb.from('items').select('status').limit(10000),
    sb.from('drafts').select('status').limit(10000),
    sb.from('runs').select('stage, status, finished_at').order('started_at', { ascending: false }).limit(60),
    sb.from('audit_log').select('action, target, created_at').order('created_at', { ascending: false }).limit(5),
    sb.from('budget').select('day, spend_usd').order('day', { ascending: false }).limit(1),
  ]);

  const itemCounts = tally((itemsRows.data ?? []) as { status: string }[]);
  const draftCounts = tally((draftsRows.data ?? []) as { status: string }[]);

  // Last success per stage + staleness (dead-man check)
  const stageLast: Record<string, { status: string; finished_at: string | null }> = {};
  for (const r of (lastRuns.data ?? []) as { stage: string; status: string; finished_at: string | null }[]) {
    if (!stageLast[r.stage]) stageLast[r.stage] = { status: r.status, finished_at: r.finished_at };
  }
  const staleStages: string[] = [];
  for (const [stage, r] of Object.entries(stageLast)) {
    const finished = r.finished_at ? new Date(r.finished_at).getTime() : NaN;
    if (r.status !== 'success' || Number.isNaN(finished) || now - finished > STALE_MS) {
      staleStages.push(stage);
    }
  }

  const totalIn = Object.values(itemCounts).reduce((a, b) => a + b, 0);
  const totalDrafts = Object.values(draftCounts).reduce((a, b) => a + b, 0);
  const killed =
    (itemCounts.held ?? 0) + (draftCounts.rejected ?? 0) + (itemCounts.rejected ?? 0);
  const killRate =
    totalIn + totalDrafts > 0
      ? Math.round((killed / (totalIn + totalDrafts)) * 1000) / 10
      : null;

  return Response.json({
    ok: true,
    mode,
    generated_at: new Date().toISOString(),
    counts: {
      items: itemCounts,
      drafts: draftCounts,
    },
    kill_rate_percent: killRate,
    stages: stageLast,
    stale_stages: staleStages,
    dead_man: { stale_after_hours: 6, alerts: staleStages.length > 0 ? staleStages : null },
    budget_today_usd: budgetRow.data?.[0]?.spend_usd ?? 0,
    recent_audit: recentAudit.data ?? [],
  });
}
