'use client';

// Client-side buttons only — the forms call server actions; no secrets here.
// When `owner` is false the queue is read-only: decisions happen via the
// one-tap signed links in the notification email.

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
  owner,
}: {
  mode: string;
  drafts: QueueDraft[];
  owner: boolean;
}) {
  return (
    <div className="queue-wrap">
      {drafts.length === 0 && <p className="muted">No pending drafts. The queue is clean.</p>}
      {drafts.map((d) => (
        <article key={d.id} className="queue-card">
          <div className="queue-meta">
            <span className="tag">tier {d.tier}</span>
            <span className="tag">score {Number(d.voice_score)}</span>
            <span className="tag muted">{new Date(d.created_at).toLocaleString()}</span>
          </div>
          <p className="queue-title">{d.title}</p>
          <p className="queue-body">{d.body}</p>
          {owner && (
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
          )}
        </article>
      ))}
      {owner ? (
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
          <a className="btn btn-ghost" href="/api/owner?logout=1">
            Lock page
          </a>
        </div>
      ) : (
        <div className="cta-row owner-row">
          <p className="muted">
            Read-only window. Decisions happen from the notification email — one tap on your
            phone. Owner mode:
          </p>
          <form action="/api/owner" method="post" className="owner-form">
            <input
              type="password"
              name="key"
              placeholder="Owner key"
              className="owner-input"
              autoComplete="off"
            />
            <button className="btn btn-ghost" type="submit">
              Enable
            </button>
          </form>
          <a className="btn btn-ghost" href="/api/status" target="_blank" rel="noreferrer">
            Status JSON ↗
          </a>
        </div>
      )}
    </div>
  );
}

