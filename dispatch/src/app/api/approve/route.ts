// ⑥ /api/approve — programmatic approval (Bearer CRON_SECRET).
// The one-pager uses server actions on the same core logic.

import { NextRequest } from 'next/server';
import { authorized } from '@/lib/guardrails';
import { decideDraft } from '@/lib/approve';

export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest): Promise<Response> {
  if (!authorized(req)) {
    return Response.json({ ok: false, reason: 'unauthorized' }, { status: 401 });
  }
  let body: { draftId?: string; decision?: string } = {};
  try {
    body = await req.json();
  } catch {
    // invalid json -> 400 below
  }
  const decision =
    body.decision === 'approved' ? 'approved' : body.decision === 'rejected' ? 'rejected' : null;
  if (!body.draftId || !decision) {
    return Response.json(
      { ok: false, reason: 'draftId + decision (approved|rejected) required' },
      { status: 400 }
    );
  }
  const result = await decideDraft(body.draftId, decision, 'api');
  return Response.json(result, { status: result.ok ? 200 : 409 });
}
