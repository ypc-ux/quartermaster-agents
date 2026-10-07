// Signed approval links — HMAC tokens scoped to ONE draft + ONE decision,
// expiring. The notification email embeds them; a tap approves/rejects
// without any account. The claim-by-transition logic in decideDraft makes
// replay impossible after the first successful decision.

import crypto from 'node:crypto';
import { ENV } from './env';

const TTL_MS = 7 * 24 * 60 * 60 * 1000; // links live 7 days

export type Decision = 'approved' | 'rejected';

function signingKey(): string {
  // CRON_SECRET doubles as the signing key — server-side only, never bundled.
  return ENV.cronSecret || ENV.adminKey || 'dev-insecure';
}

export function signDecisionToken(draftId: string, decision: Decision): string {
  const payload = { draftId, decision, exp: Date.now() + TTL_MS };
  const body = Buffer.from(JSON.stringify(payload)).toString('base64url');
  const sig = crypto.createHmac('sha256', signingKey()).update(body).digest('base64url');
  return `${body}.${sig}`;
}

export function verifyDecisionToken(
  token: string
): { draftId: string; decision: Decision } | null {
  try {
    const [body, sig] = token.split('.');
    if (!body || !sig) return null;
    const expected = crypto
      .createHmac('sha256', signingKey())
      .update(body)
      .digest('base64url');
    const a = Buffer.from(sig);
    const b = Buffer.from(expected);
    if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
    const payload = JSON.parse(Buffer.from(body, 'base64url').toString());
    if (typeof payload.draftId !== 'string') return null;
    if (payload.decision !== 'approved' && payload.decision !== 'rejected') return null;
    if (typeof payload.exp !== 'number' || payload.exp < Date.now()) return null;
    return { draftId: payload.draftId, decision: payload.decision as Decision };
  } catch {
    return null;
  }
}
