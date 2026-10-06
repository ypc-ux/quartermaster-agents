// Bundled sample ICS — used until GCAL_ICS_URL is set (open item O3).
// Public-safe demo events only. sample-002 proves the compliance screen:
// it contains deny-list terms and must be stored redacted + held T2.

export const SAMPLE_ICS = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//DISPATCH//Sample//EN
BEGIN:VEVENT
UID:sample-001-dispatch-walkthrough@dispatch
DTSTART:20261006T090000Z
DTEND:20261006T100000Z
SUMMARY:#public Dispatch walking skeleton demo
DESCRIPTION:#public Today I walked the calendar-to-content pipeline end to end. Ingest, compliance screen, classify, draft, humanizer gate, approval, publish log. One thin slice through all 8 stages. 8 stages, 1 day, 0 shortcuts.
LOCATION:Studio
END:VEVENT
BEGIN:VEVENT
UID:sample-002-internal-review@dispatch
DTSTART:20261006T140000Z
DTEND:20261006T150000Z
SUMMARY:Internal: legal review with counsel
DESCRIPTION:Confidential - attorney-client privileged discussion. Do not share.
END:VEVENT
BEGIN:VEVENT
UID:sample-003-coffee@dispatch
DTSTART:20261007T080000Z
DTEND:20261007T090000Z
SUMMARY:Coffee with a founder
DESCRIPTION:Catching up with an old friend who runs a fintech. Just catching up.
END:VEVENT
BEGIN:VEVENT
UID:sample-004-podcast@dispatch
DTSTART:20261008T160000Z
DTEND:20261008T170000Z
SUMMARY:#public Podcast recording: privacy for founders
DESCRIPTION:#public Recording episode 12 of the privacy show. Topic: what founders get wrong about data security. Guest: CTO of a healthcare startup.
END:VEVENT
END:VCALENDAR
`;
