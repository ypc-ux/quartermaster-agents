// Approval decisions. Claim-by-status-transition: only a `pending` draft can be decided,
// so a double-click can never double-decide.

import { getSupabase } from './supabase';
import { audit } from './audit';

export type Decision = 'approved' | 'rejected';

export async function decideDraft(
  draftId: string,
  decision: Decision,
  actor: string
): Promise<{ ok: boolean; reason?: string }> {
  const sb = getSupabase();
  const now = new Date().toISOString();
  const { data: claimed } = await sb
    .from('drafts')
    .update({ status: decision, updated_at: now })
    .eq('id', draftId)
    .eq('status', 'pending')
    .select('id, item_id')
    .single();
  if (!claimed) return { ok: false, reason: 'draft not pending' };
  await sb.from('approvals').insert({
    draft_id: draftId,
    decision,
    decided_by: actor,
  });
  await sb
    .from('items')
    .update({ status: decision === 'approved' ? 'queued' : 'rejected', updated_at: now })
    .eq('id', claimed.item_id);
  await audit(decision === 'approved' ? 'draft_approved' : 'draft_rejected', {
    actor,
    target: draftId,
  });
  return { ok: true };
}
