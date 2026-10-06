'use client';

// Client-side buttons only — the forms call server actions; no secrets here.

import { approveDraft, rejectDraft, toggleEngine } from '@/app/actions';

export interface QueueDraft {
  id: string;
  title: string;
  body: string;
  voice_score: number;
  tier: string;
  created_at: string;
}

export default function QueueActions({
  mode,
  drafts,
}: {
  mode: string;
  drafts: QueueDraft[];
}) {
  return (
    <div className="queue-wrap">
      {drafts.length === 0 && (
        <p className="muted">No pending drafts. The queue is clean.</p>
      )}
      {drafts.map((d) => (
        <article key={d.id} className="queue-card">
          <div className="queue-meta">
            <span className="tag">tier {d.tier}</span>
            <span className="tag">score {Number(d.voice_score)}</span>
            <span className="tag muted">{new Date(d.created_at).toLocaleString()}</span>
          </div>
          <p className="queue-title">{d.title}</p>
          <p className="queue-body">{d.body}</p>
          <div className="queue-buttons">
            <form action={approveDraft}>
              <input type="hidden" name="draftId" value={d.id} />
              <button className="btn btn-approve" type="submit">
                Approve
              </button>
            </form>
            <form action={rejectDraft}>
              <input type="hidden" name="draftId" value={d.id} />
              <button className="btn btn-reject" type="submit">
                Reject
              </button>
            </form>
          </div>
        </article>
      ))}
      <div className="cta-row">
        <form action={toggleEngine}>
          <input type="hidden" name="mode" value={mode === 'paused' ? 'draft' : 'paused'} />
          <button
            className={mode === 'paused' ? 'btn btn-resume' : 'btn btn-kill'}
            type="submit"
          >
            {mode === 'paused' ? 'Resume engine' : 'Kill switch — pause engine'}
          </button>
        </form>
        <a className="btn btn-ghost" href="/api/status" target="_blank" rel="noreferrer">
          Open status JSON ↗
        </a>
      </div>
    </div>
  );
}
