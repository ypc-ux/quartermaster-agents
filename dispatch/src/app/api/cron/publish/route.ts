// ⑦ Publish — approved drafts, claimed by status transition, idempotent by
// (draft_id, platform, payload_hash). Draft mode logs "would post" with the exact payload.

import { NextRequest } from 'next/server';
import { withRun, engineMode } from '@/lib/guardrails';
import { getSupabase } from '@/lib/supabase';
import { audit } from '@/lib/audit';
import { postToX, hasXKeys } from '@/lib/xpost';

export const dynamic = 'force-dynamic';
export const maxDuration = 120;

interface DraftRow {
  id: string;
  body: string;
  post_hash: string;
  item_id: string;
  payload: Record<string, unknown>;
}

/** SOP-01 publish slots: 08/12/17 UTC, weekdays only. */
function inPublishSlot(now: Date): boolean {
  const day = now.getUTCDay();
  const hour = now.getUTCHours();
  return day >= 1 && day <= 5 && (hour === 8 || hour === 12 || hour === 17);
}

export async function GET(req: NextRequest): Promise<Response> {
  return withRun(req, 'publish', async () => {
    const force = req.nextUrl.searchParams.get('force') === 'yes';
    if (!inPublishSlot(new Date()) && !force) {
      return { skipped: true, reason: 'outside-slot (SOP-01: 08/12/17 UTC, Mon-Fri)' };
    }
    const sb = getSupabase();
    const mode = await engineMode();
    const { data: drafts } = await sb
      .from('drafts')
      .select('id, body, post_hash, item_id, payload')
      .eq('status', 'approved')
      .limit(10);
    let published = 0;
    let failed = 0;
    const now = new Date().toISOString();
    const live = mode === 'active' && hasXKeys();

    for (const d of (drafts ?? []) as DraftRow[]) {
      // Atomic claim: approved -> queued. A second run cannot re-claim.
      const { data: claimed } = await sb
        .from('drafts')
        .update({ status: 'queued' })
        .eq('id', d.id)
        .eq('status', 'approved')
        .select('id')
        .single();
      if (!claimed) continue;

      let pubStatus: 'simulated' | 'posted' | 'failed' = 'simulated';
      let response: Record<string, unknown> = {
        note: `draft mode — would post (mode=${mode})`,
        payload: d.payload,
      };
      if (live) {
        const xr = await postToX(d.body);
        pubStatus = xr.ok ? 'posted' : 'failed';
        response = { provider: 'x', ok: xr.ok, id: xr.id ?? null, error: xr.error ?? null };
      }

      const { error } = await sb
        .from('publishes')
        .insert({
          draft_id: d.id,
          platform: 'x',
          payload_hash: d.post_hash,
          status: pubStatus,
          response,
        })
        .select('id')
        .single();
      if (!error) {
        const finalStatus = pubStatus === 'failed' ? 'failed' : 'published';
        await sb.from('drafts').update({ status: finalStatus, updated_at: now }).eq('id', d.id);
        await sb
          .from('items')
          .update({ status: pubStatus === 'failed' ? 'failed' : 'published', updated_at: now })
          .eq('id', d.item_id);
        await audit('publish', { target: d.id, detail: { status: pubStatus } });
        if (pubStatus === 'failed') failed++;
        else published++;
      } else if (error.code === '23505') {
        // Already published once — idempotent no-op, keep terminal state.
        await sb.from('drafts').update({ status: 'published', updated_at: now }).eq('id', d.id);
      } else {
        // Unexpected insert error — roll the claim back so a later run can retry.
        await sb.from('drafts').update({ status: 'approved', updated_at: now }).eq('id', d.id);
        throw new Error(`publish insert: ${error.message}`);
      }
    }

    return { mode, live, published, failed };
  });
}
