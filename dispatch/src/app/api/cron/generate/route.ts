// ②-⑤ Compliance (re-screen) → Classify → Draft → Humanizer gate.
// Claim-by-status-transition keeps every step idempotent.

import { NextRequest } from 'next/server';
import { withRun, engineMode } from '@/lib/guardrails';
import { getSupabase } from '@/lib/supabase';
import { screenEvent } from '@/lib/compliance';
import { classifyEvent, draftPost, fallbackTemplate } from '@/lib/llm';
import { gateDraft } from '@/lib/humanizer';
import { audit } from '@/lib/audit';
import { notifyNewDraft } from '@/lib/notify';
import { djb2 } from '@/lib/ics';
import { ENV } from '@/lib/env';

export const dynamic = 'force-dynamic';
export const maxDuration = 300;

interface ItemRow {
  id: string;
  uid: string;
  title: string;
  description: string;
  tier: string;
  status: string;
}

export async function GET(req: NextRequest): Promise<Response> {
  return withRun(req, 'generate', async () => {
    const sb = getSupabase();
    const mode = await engineMode();
    const now = new Date().toISOString();

    // Claim up to N new items with an atomic status transition.
    const claimed: ItemRow[] = [];
    const { data: candidates } = await sb
      .from('items')
      .select('id, uid, title, description, tier, status')
      .eq('status', 'new')
      .order('created_at', { ascending: true })
      .limit(ENV.maxItemsPerRun);
    for (const row of (candidates ?? []) as ItemRow[]) {
      const { data: got } = await sb
        .from('items')
        .update({ status: 'classified' })
        .eq('id', row.id)
        .eq('status', 'new')
        .select('id, uid, title, description, tier, status')
        .single();
      if (got) claimed.push(got as ItemRow);
    }

    let drafted = 0;
    let heldNow = 0;
    let gatedOut = 0;
    let llmFailed = 0;
    let notified = 0;

    for (const item of claimed) {
      // ② Compliance re-screen (defense in depth — ingest already screened).
      const verdict = screenEvent(item.title, item.description);
      if (verdict.verdict !== 'pass') {
        await sb
          .from('items')
          .update({
            status: 'held',
            tier: 't2',
            compliance: verdict.verdict,
            compliance_reason: verdict.reason,
            updated_at: now,
          })
          .eq('id', item.id);
        await audit('generate_held', { target: item.uid, detail: { reason: verdict.reason } });
        heldNow++;
        continue;
      }

      // ③ Classify
      const classification = await classifyEvent({ title: item.title, description: item.description });
      const topic = classification?.topic ?? 'uncategorized';
      const pillar = classification?.pillar ?? 'other';

      // ④ Draft (template fallback on LLM failure / cost cap)
      let body = await draftPost({ title: item.title, description: item.description, topic });
      let usedFallback = false;
      if (!body) {
        body = fallbackTemplate({ title: item.title, description: item.description });
        usedFallback = true;
        llmFailed++;
      }

      // ⑤ Humanizer gate
      const gate = gateDraft(body);
      const postHash = djb2(body);
      const payload = {
        platform: 'x',
        body,
        topic,
        pillar,
        tier: item.tier,
        mode,
        generated_at: now,
      };
      const { data: draftRow, error } = await sb
        .from('drafts')
        .insert({
          item_id: item.id,
          platform: 'x',
          body,
          payload,
          banned_hits: gate.bannedHits,
          voice_score: gate.score,
          status: gate.passed ? 'pending' : 'rejected',
          post_hash: postHash,
          fallback: usedFallback,
        })
        .select('id')
        .single();
      if (error && error.code !== '23505') {
        throw new Error(`draft insert: ${error.message}`);
      }
      const draftId = draftRow?.id as string | undefined;
      await sb
        .from('items')
        .update({ status: 'drafted', topic, tier: item.tier, updated_at: now })
        .eq('id', item.id);

      if (gate.passed) {
        drafted++;
        await audit('draft_created', {
          target: item.uid,
          detail: { draft: draftId ?? null, score: gate.score, fallback: usedFallback },
        });
        if (draftId) {
          notified += (await notifyNewDraft({ title: item.title, body, draftId })) ? 1 : 0;
        }
        // T0 auto-approve (explicit #auto marker + active mode only)
        if (item.tier === 't0' && mode === 'active' && draftId) {
          await sb
            .from('drafts')
            .update({ status: 'approved', updated_at: now })
            .eq('id', draftId)
            .eq('status', 'pending');
          await sb.from('approvals').insert({
            draft_id: draftId,
            decision: 'approved',
            decided_by: 'tier-t0-auto',
          });
          await sb
            .from('items')
            .update({ status: 'queued', updated_at: now })
            .eq('id', item.id);
          await audit('draft_auto_approved', { target: item.uid, detail: { draft: draftId } });
        }
      } else {
        gatedOut++;
        await audit('draft_rejected_by_gate', {
          target: item.uid,
          detail: { banned: gate.bannedHits, score: gate.score },
        });
      }
    }

    return { claimed: claimed.length, drafted, gatedOut, heldNow, llmFailed, notified };
  });
}
