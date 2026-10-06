// Audit log — a row per public-facing action. Never throws.

import { getSupabase } from './supabase';

export async function audit(
  action: string,
  opts: { actor?: string; target?: string; detail?: Record<string, unknown> } = {}
): Promise<void> {
  try {
    await getSupabase().from('audit_log').insert({
      action,
      actor: opts.actor ?? 'engine',
      target: opts.target ?? '',
      detail: opts.detail ?? {},
    });
  } catch (e) {
    console.error('[audit] failed:', e);
  }
}
