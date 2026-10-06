// Guardrails: kill switch, cron auth, stage guard, run bookkeeping.

import { ENV } from './env';
import { getSupabase } from './supabase';

export type EngineMode = 'active' | 'draft' | 'paused';

/** Effective mode: runtime override row in `settings` beats the env var. */
export async function engineMode(): Promise<EngineMode> {
  try {
    const { data } = await getSupabase()
      .from('settings')
      .select('value')
      .eq('key', 'engine_mode_override')
      .maybeSingle();
    if (data?.value === 'paused' || data?.value === 'active' || data?.value === 'draft') {
      return data.value as EngineMode;
    }
  } catch {
    // fall through to env
  }
  return ENV.engineMode === 'paused' || ENV.engineMode === 'active'
    ? (ENV.engineMode as EngineMode)
    : 'draft';
}

export async function setEngineMode(mode: EngineMode): Promise<void> {
  await getSupabase()
    .from('settings')
    .upsert({ key: 'engine_mode_override', value: mode, updated_at: new Date().toISOString() });
}

export function authorized(req: Request): boolean {
  if (!ENV.cronSecret) return false;
  const header = req.headers.get('authorization') ?? '';
  return header === `Bearer ${ENV.cronSecret}`;
}

export interface StageGuard {
  ok: boolean;
  reason?: string;
}

/** Every cron stage passes through here: auth first, then kill switch. */
export async function stageGuard(req: Request): Promise<StageGuard> {
  if (!authorized(req)) return { ok: false, reason: 'unauthorized' };
  const mode = await engineMode();
  if (mode === 'paused') return { ok: false, reason: 'paused' };
  return { ok: true };
}

/** Wraps a stage: auth/kill-switch check, runs row (success/failed), JSON response. */
export async function withRun(
  req: Request,
  stage: string,
  fn: () => Promise<Record<string, unknown>>
): Promise<Response> {
  const guard = await stageGuard(req);
  if (!guard.ok) {
    return Response.json({ ok: false, stage, skipped: true, reason: guard.reason });
  }
  const sb = getSupabase();
  const { data: runRow } = await sb
    .from('runs')
    .insert({ stage, status: 'running' })
    .select('id')
    .single();
  const runId = runRow?.id as string | undefined;
  try {
    const result = await fn();
    if (runId) {
      await sb
        .from('runs')
        .update({ status: 'success', finished_at: new Date().toISOString() })
        .eq('id', runId);
    }
    return Response.json({ ok: true, stage, ...result });
  } catch (e) {
    const message = e instanceof Error ? e.message : String(e);
    if (runId) {
      await sb
        .from('runs')
        .update({
          status: 'failed',
          finished_at: new Date().toISOString(),
          error: message.slice(0, 500),
        })
        .eq('id', runId);
    }
    return Response.json({ ok: false, stage, error: message }, { status: 500 });
  }
}
