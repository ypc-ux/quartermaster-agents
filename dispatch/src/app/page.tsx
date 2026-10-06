// The one-pager — a window, not the engine. Reads live state, approves drafts.
// The engine runs with the browser closed.

import { getSupabase } from '@/lib/supabase';
import { engineMode } from '@/lib/guardrails';
import QueueActions, { QueueDraft } from '@/components/queue-actions';

export const dynamic = 'force-dynamic';

const STALE_MS = 6 * 60 * 60 * 1000;

interface StageState {
  status: 'success' | 'failed' | 'running';
  finished_at: string | null;
}

interface PageData {
  mode: string;
  itemCounts: Record<string, number>;
  draftCounts: Record<string, number>;
  pendingDrafts: QueueDraft[];
  auditRows: { action: string; target: string; created_at: string }[];
  stageLast: Record<string, StageState>;
  killRate: number | null;
  budgetUsd: number;
}

function tally(rows: { status: string }[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const r of rows) {
    const k = r.status || 'unknown';
    out[k] = (out[k] ?? 0) + 1;
  }
  return out;
}

async function getData(): Promise<PageData> {
  const sb = getSupabase();
  const mode = await engineMode();

  const [itemsRows, draftsRows, pendingRows, auditRes, runsRes, budgetRes] = await Promise.all([
    sb.from('items').select('status').limit(10000),
    sb.from('drafts').select('status').limit(10000),
    sb
      .from('drafts')
      .select('id, body, voice_score, created_at, items(title, tier)')
      .eq('status', 'pending')
      .order('created_at', { ascending: true })
      .limit(25),
    sb
      .from('audit_log')
      .select('action, target, created_at')
      .order('created_at', { ascending: false })
      .limit(5),
    sb
      .from('runs')
      .select('stage, status, finished_at')
      .order('started_at', { ascending: false })
      .limit(60),
    sb.from('budget').select('day, spend_usd').order('day', { ascending: false }).limit(1),
  ]);

  const itemCounts = tally((itemsRows.data ?? []) as { status: string }[]);
  const draftCounts = tally((draftsRows.data ?? []) as { status: string }[]);

  const stageLast: Record<string, StageState> = {};
  for (const r of (runsRes.data ?? []) as {
    stage: string;
    status: string;
    finished_at: string | null;
  }[]) {
    if (!stageLast[r.stage]) {
      stageLast[r.stage] = {
        status: (r.status === 'failed'
          ? 'failed'
          : r.status === 'running'
            ? 'running'
            : 'success') as StageState['status'],
        finished_at: r.finished_at,
      };
    }
  }

  const pendingDrafts: QueueDraft[] = (
    (pendingRows.data ?? []) as unknown as {
      id: string;
      body: string;
      voice_score: number;
      created_at: string;
      items: { title: string; tier: string } | { title: string; tier: string }[] | null;
    }[]
  ).map((d) => {
    const item = Array.isArray(d.items) ? d.items[0] : d.items;
    return {
      id: d.id,
      title: item?.title ?? '(no title)',
      body: d.body,
      voice_score: d.voice_score,
      tier: item?.tier ?? 't2',
      created_at: d.created_at,
    };
  });

  const totalIn = Object.values(itemCounts).reduce((a, b) => a + b, 0);
  const totalDrafts = Object.values(draftCounts).reduce((a, b) => a + b, 0);
  const killed =
    (itemCounts.held ?? 0) + (draftCounts.rejected ?? 0) + (itemCounts.rejected ?? 0);
  const killRate =
    totalIn + totalDrafts > 0 ? Math.round((killed / (totalIn + totalDrafts)) * 1000) / 10 : null;

  return {
    mode,
    itemCounts,
    draftCounts,
    pendingDrafts,
    auditRows: (auditRes.data ?? []) as PageData['auditRows'],
    stageLast,
    killRate,
    budgetUsd: Number(budgetRes.data?.[0]?.spend_usd ?? 0),
  };
}

function stageDot(state: StageState | undefined, waiting: boolean, mode: string): string {
  if (mode === 'paused') return 'failed';
  if (!state) return waiting ? 'waiting' : '';
  if (state.status === 'failed') return 'failed';
  if (state.status === 'running') return 'waiting';
  const finished = state.finished_at ? new Date(state.finished_at).getTime() : NaN;
  if (Number.isNaN(finished) || Date.now() - finished > STALE_MS) return 'waiting';
  return 'live';
}

export default async function Page() {
  const d = await getData();
  const gen = d.stageLast.generate;

  const stages: { name: string; sub: string; dot: string }[] = [
    { name: '① Ingest', sub: 'ICS → items', dot: stageDot(d.stageLast.ingest, false, d.mode) },
    { name: '② Compliance', sub: 'deny-list + tier', dot: stageDot(gen, false, d.mode) },
    { name: '③ Classify', sub: 'topic + pillar', dot: stageDot(gen, false, d.mode) },
    { name: '④ Draft', sub: 'voice rules', dot: stageDot(gen, false, d.mode) },
    { name: '⑤ Gate', sub: 'banned words + score', dot: stageDot(gen, false, d.mode) },
    {
      name: '⑥ Approval',
      sub: `${d.draftCounts.pending ?? 0} waiting`,
      dot: (d.draftCounts.pending ?? 0) > 0 ? 'waiting' : stageDot(gen, false, d.mode),
    },
    { name: '⑦ Publish', sub: 'SOP-01 slots', dot: stageDot(d.stageLast.publish, true, d.mode) },
    { name: '⑧ Audit', sub: 'runs + log', dot: d.mode === 'paused' ? 'failed' : 'live' },
  ];

  return (
    <div className="container">
      <header className="hero">
        <h1>
          DISPATCH<span className="accent">.</span>
        </h1>
        <p>Your calendar in. Content out. Nothing ships without approval.</p>
        <span
          className={`mode-badge ${d.mode === 'active' ? 'live' : d.mode === 'paused' ? 'paused' : ''}`}
        >
          engine: {d.mode}
        </span>
      </header>

      <section>
        <h2>
          Pipeline <span className="count">8 stages · live state</span>
        </h2>
        <div className="pipeline">
          {stages.map((s) => (
            <div className="pipe-stage" key={s.name}>
              <span className={`dot ${s.dot}`} />
              <div>
                <div className="name">{s.name}</div>
                <div className="sub">{s.sub}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2>
          Live KPIs <span className="count">source: items/drafts tables</span>
        </h2>
        <div className="kpis">
          <div className="kpi">
            <div className="value">{d.killRate === null ? '—' : `${d.killRate}%`}</div>
            <div className="label">Kill-rate</div>
            <div className="source">held + rejected / processed</div>
          </div>
          <div className="kpi">
            <div className="value">{d.draftCounts.pending ?? 0}</div>
            <div className="label">Drafts pending</div>
            <div className="source">drafts.status=pending</div>
          </div>
          <div className="kpi">
            <div className="value">{d.draftCounts.approved ?? 0}</div>
            <div className="label">Approved</div>
            <div className="source">drafts.status=approved</div>
          </div>
          <div className="kpi">
            <div className="value">{d.draftCounts.published ?? 0}</div>
            <div className="label">Published</div>
            <div className="source">drafts.status=published</div>
          </div>
          <div className="kpi">
            <div className="value">${d.budgetUsd.toFixed(4)}</div>
            <div className="label">LLM spend today</div>
            <div className="source">budget table</div>
          </div>
        </div>
      </section>

      <section>
        <h2>
          The Queue <span className="count">approve or reject</span>
        </h2>
        <QueueActions mode={d.mode} drafts={d.pendingDrafts} />
      </section>

      <section>
        <h2>
          Proof <span className="count">last 5 audit rows</span>
        </h2>
        <table className="audit-table">
          <thead>
            <tr>
              <th>When</th>
              <th>Action</th>
              <th>Target</th>
            </tr>
          </thead>
          <tbody>
            {d.auditRows.map((r, i) => (
              <tr key={i}>
                <td className="mono">{new Date(r.created_at).toLocaleString()}</td>
                <td>{r.action}</td>
                <td className="mono">{r.target}</td>
              </tr>
            ))}
            {d.auditRows.length === 0 && (
              <tr>
                <td colSpan={3} className="muted">
                  No audit rows yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>

      <footer>
        DISPATCH is a window, not the engine — the pipeline runs on Vercel Cron with the tab
        closed. Draft mode: nothing posts for real until X keys land (open item O2).
      </footer>
    </div>
  );
}

