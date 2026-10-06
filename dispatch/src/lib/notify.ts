// Resend notification on new drafts. Best-effort: failure audits and never blocks the pipeline.

import { ENV } from './env';
import { audit } from './audit';

export async function notifyNewDraft(opts: {
  title: string;
  body: string;
  draftId: string;
}): Promise<boolean> {
  if (!ENV.resendKey || !ENV.notifyEmail) return false;
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
        text: `A draft passed the gate and needs a decision.\n\n${opts.body}\n\nApprove or reject on the one-pager.`,
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
