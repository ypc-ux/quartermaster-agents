// ① Ingest — parse ICS, sanitize, compliance screen, idempotent upsert by UID.
// Deny-list events are stored as a redacted shell (title "[redacted]", no text), held T2.

import { NextRequest } from 'next/server';
import { parseIcs } from '@/lib/ics';
import { sanitizeText } from '@/lib/sanitize';
import { screenEvent, assignTier } from '@/lib/compliance';
import { audit } from '@/lib/audit';
import { getSupabase } from '@/lib/supabase';
import { withRun } from '@/lib/guardrails';
import { ENV } from '@/lib/env';
import { SAMPLE_ICS } from '@/lib/sample';

export const dynamic = 'force-dynamic';
export const maxDuration = 60;

async function fetchIcsText(): Promise<{ text: string; source: string }> {
  if (ENV.gcalIcsUrl) {
    const res = await fetch(ENV.gcalIcsUrl, {
      signal: AbortSignal.timeout(15_000),
      headers: { 'user-agent': 'dispatch-engine/0.1' },
    });
    if (!res.ok) throw new Error(`ICS fetch failed: HTTP ${res.status}`);
    const text = await res.text();
    if (text.length > 2_000_000) throw new Error('ICS too large');
    return { text, source: 'gcal' };
  }
  return { text: SAMPLE_ICS, source: 'sample' };
}

export async function GET(req: NextRequest): Promise<Response> {
  return withRun(req, 'ingest', async () => {
    const { text, source } = await fetchIcsText();
    const events = parseIcs(text);
    const sb = getSupabase();
    const now = new Date().toISOString();
    let upserted = 0;
    let denied = 0;
    let held = 0;
    let skipped = 0;

    for (const ev of events) {
      const title = sanitizeText(ev.summary, 300);
      const description = sanitizeText(ev.description, 4000);
      const { data: existing } = await sb
        .from('items')
        .select('id, status')
        .eq('uid', ev.uid)
        .maybeSingle();
      if (existing && existing.status !== 'new') {
        skipped++;
        continue;
      }
      const verdict = screenEvent(title, description);
      if (verdict.verdict === 'deny') {
        const { error: denyErr } = await sb.from('items').upsert(
          {
            uid: ev.uid,
            source,
            title: '[redacted]',
            description: '',
            raw: { uid: ev.uid },
            sanitized: {},
            compliance: 'deny',
            compliance_reason: verdict.reason,
            tier: 't2',
            status: 'held',
            start_at: ev.start,
            end_at: ev.end,
            updated_at: now,
          },
          { onConflict: 'uid' }
        );
        if (denyErr) throw new Error(`deny upsert failed: ${denyErr.message}`);
        await audit('ingest_denied', { target: ev.uid, detail: { reason: verdict.reason } });
        denied++;
        continue;
      }
      const tier = assignTier(title, description, verdict.verdict);
      const status = verdict.verdict === 'hold' ? 'held' : 'new';
      const { error: upErr } = await sb.from('items').upsert(
        {
          uid: ev.uid,
          source,
          title,
          description,
          location: sanitizeText(ev.location, 300),
          start_at: ev.start,
          end_at: ev.end,
          raw: ev.raw,
          sanitized: { title, description },
          compliance: verdict.verdict,
          compliance_reason: verdict.reason,
          tier,
          status,
          updated_at: now,
        },
        { onConflict: 'uid' }
      );
      if (upErr) throw new Error(`item upsert failed: ${upErr.message}`);
      if (verdict.verdict === 'hold') {
        await audit('ingest_held', { target: ev.uid, detail: { reason: verdict.reason } });
        held++;
      } else {
        upserted++;
      }
    }
    return { source, events: events.length, upserted, denied, held, skipped };
  });
}
