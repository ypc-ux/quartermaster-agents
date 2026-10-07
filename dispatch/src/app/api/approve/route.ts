// ⑥ Approval — two surfaces:
//   GET  /api/approve?token=...  — one-tap signed email links (no account needed)
//   POST /api/approve            — programmatic (Bearer CRON_SECRET)

import { NextRequest } from 'next/server';
import { authorized } from '@/lib/guardrails';
import { decideDraft } from '@/lib/approve';
import { verifyDecisionToken } from '@/lib/approval-token';

export const dynamic = 'force-dynamic';

function resultPage(title: string, message: string): Response {
  const html = `<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>DISPATCH — ${title}</title>
<style>
body{background:#0a0a0a;color:#c0c0c0;font-family:Inter,Arial,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.card{max-width:420px;padding:32px;border:1px solid #262626;border-radius:12px;background:#141414;text-align:center}
h1{color:#ffffff;font-size:20px;margin:0 0 12px}
p{font-size:14px;margin:0}
a{color:#a855f7}
</style></head>
<body><div class="card">
<h1>${title}</h1>
<p>${message}</p>
<p style="margin-top:16px;font-size:13px"><a href="/">Back to the queue</a></p>
</div></body></html>`;
  return new Response(html, { headers: { 'content-type': 'text/html; charset=utf-8' } });
}

export async function GET(req: NextRequest): Promise<Response> {
  const token = req.nextUrl.searchParams.get('token') ?? '';
  const payload = verifyDecisionToken(token);
  if (!payload) {
    return resultPage('Link invalid or expired', 'Ask for a fresh notification email, or decide from the one-pager.');
  }
  const result = await decideDraft(payload.draftId, payload.decision, 'email-link');
  if (!result.ok) {
    return resultPage('Already decided', 'A decision link only works once. This draft was already handled.');
  }
  return resultPage(
    payload.decision === 'approved' ? 'Approved' : 'Rejected',
    payload.decision === 'approved'
      ? 'Logged. The engine will publish at the next SOP-01 slot (draft mode logs "would post").'
      : 'Logged. Nothing will publish.'
  );
}

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

