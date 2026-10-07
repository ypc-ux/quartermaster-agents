// Resend notification on new drafts with one-tap signed approval links.
// Best-effort: failure audits and never blocks the pipeline.

import { ENV } from './env';
import { audit } from './audit';
import { signDecisionToken } from './approval-token';

function escapeHtml(input: string): string {
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export async function notifyNewDraft(opts: {
  title: string;
  body: string;
  draftId: string;
}): Promise<boolean> {
  if (!ENV.resendKey || !ENV.notifyEmail) return false;
  const approveUrl = `${ENV.dispatchUrl}/api/approve?token=${signDecisionToken(opts.draftId, 'approved')}`;
  const rejectUrl = `${ENV.dispatchUrl}/api/approve?token=${signDecisionToken(opts.draftId, 'rejected')}`;
  const text = [
    `A draft passed the gate and needs a decision.`,
    '',
    opts.body,
    '',
    `Approve: ${approveUrl}`,
    `Reject:  ${rejectUrl}`,
    '',
    'Links expire in 7 days and work exactly once.',
  ].join('\n');
  const html = `<div style="font-family:Inter,Arial,sans-serif;max-width:520px;background:#0a0a0a;color:#c0c0c0;padding:24px;border-radius:8px">
  <p style="margin:0 0 12px">A draft passed the gate and needs a decision.</p>
  <blockquote style="margin:0 0 16px;border-left:3px solid #a855f7;padding:12px 16px;background:#141414;border-radius:0 8px 8px 0;color:#ffffff">${escapeHtml(opts.body)}</blockquote>
  <p style="margin:0 0 16px">
    <a href="${approveUrl}" style="background:#00ff88;color:#000000;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:700;margin-right:8px">Approve</a>
    <a href="${rejectUrl}" style="border:1px solid #3a3a3a;color:#c0c0c0;padding:10px 20px;border-radius:6px;text-decoration:none">Reject</a>
  </p>
  <p style="margin:0;color:#8a8a8a;font-size:12px">One tap, from your phone. Links expire in 7 days and work exactly once. The queue page is read-only by design.</p>
</div>`;
  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${ENV.resendKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'DISPATCH <onboarding@resend.dev>',
        to: [ENV.notifyEmail],
        subject: `DISPATCH: draft ready — "${opts.title.slice(0, 60)}"`,
        text,
        html,
      }),
      signal: AbortSignal.timeout(15_000),
    });
    if (!res.ok) {
      await audit('notify_failed', {
        target: opts.draftId,
        detail: { status: res.status },
      });
      return false;
    }
    await audit('notify_sent', { target: opts.draftId });
    return true;
  } catch (e) {
    await audit('notify_failed', {
      target: opts.draftId,
      detail: { error: e instanceof Error ? e.message : String(e) },
    });
    return false;
  }
}

