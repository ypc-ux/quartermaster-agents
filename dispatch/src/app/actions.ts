'use server';

// One-pager actions. Owner-gated: the ADMIN_KEY cookie is required before
// any decision or kill-switch action runs. All secret access stays on the
// server — nothing here ever reaches the client bundle.

import { revalidatePath } from 'next/cache';
import { decideDraft } from '@/lib/approve';
import { setEngineMode, engineMode } from '@/lib/guardrails';
import { audit } from '@/lib/audit';
import { isOwner } from '@/lib/owner';

export async function approveDraft(formData: FormData): Promise<void> {
  if (!(await isOwner())) return;
  const draftId = String(formData.get('draftId') ?? '');
  if (!draftId) return;
  await decideDraft(draftId, 'approved', 'one-pager');
  revalidatePath('/');
}

export async function rejectDraft(formData: FormData): Promise<void> {
  if (!(await isOwner())) return;
  const draftId = String(formData.get('draftId') ?? '');
  if (!draftId) return;
  await decideDraft(draftId, 'rejected', 'one-pager');
  revalidatePath('/');
}

export async function toggleEngine(formData: FormData): Promise<void> {
  if (!(await isOwner())) return;
  const target = String(formData.get('mode') ?? '');
  const current = await engineMode();
  const valid = ['paused', 'draft', 'active'] as const;
  const next = valid.includes(target as (typeof valid)[number])
    ? (target as (typeof valid)[number])
    : current === 'paused'
      ? 'draft'
      : 'paused';
  await setEngineMode(next);
  await audit('engine_mode_set', { actor: 'one-pager', detail: { mode: next } });
  revalidatePath('/');
}
