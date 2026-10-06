// Deterministic ICS parser. Calendar input is hostile — this only extracts
// VEVENT fields; nothing in the calendar ever triggers code paths or tool calls.

export interface IcsEvent {
  uid: string;
  summary: string;
  description: string;
  location: string;
  start: string | null;
  end: string | null;
  raw: Record<string, string>;
}

/** djb2 hash — used for unique ids and post-hash dedupe. */
export function djb2(input: string): string {
  let h = 5381;
  for (let i = 0; i < input.length; i++) {
    h = ((h << 5) + h + input.charCodeAt(i)) | 0;
  }
  return (h >>> 0).toString(16).padStart(8, '0');
}

function unescapeIcsValue(value: string): string {
  return value
    .replace(/\\n/gi, '\n')
    .replace(/\\,/g, ',')
    .replace(/\\;/g, ';')
    .replace(/\\\\/g, '\\');
}

export function parseIcsDate(value?: string): string | null {
  if (!value) return null;
  const v = value.trim();
  const m = /^(\d{4})(\d{2})(\d{2})T?(\d{2})?(\d{2})?(\d{2})?(Z)?$/.exec(v);
  if (!m) return null;
  const [, Y, Mo, D, h, mi, s, z] = m;
  if (!v.includes('T')) {
    return `${Y}-${Mo}-${D}T00:00:00`;
  }
  const timePart = `${h ?? '00'}:${mi ?? '00'}:${s ?? '00'}`;
  const iso = `${Y}-${Mo}-${D}T${timePart}${z ? 'Z' : ''}`;
  if (z) {
    const d = new Date(iso);
    return Number.isNaN(d.getTime()) ? null : d.toISOString();
  }
  return iso; // floating local time — stored as-is for MVP
}

export function parseIcs(text: string): IcsEvent[] {
  // Unfold continuation lines (RFC 5545 3.1)
  const unfolded = text.replace(/\r\n[ \t]/g, '').replace(/\n[ \t]/g, '');
  const lines = unfolded.split(/\r?\n/);
  const events: IcsEvent[] = [];
  let inEvent = false;
  let props: Record<string, string> = {};

  const flush = () => {
    if (!props.UID) return;
    events.push({
      uid: props.UID,
      summary: props.SUMMARY ?? '',
      description: props.DESCRIPTION ?? '',
      location: props.LOCATION ?? '',
      start: parseIcsDate(props.DTSTART),
      end: parseIcsDate(props.DTEND),
      raw: props,
    });
  };

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    if (trimmed === 'BEGIN:VEVENT') {
      inEvent = true;
      props = {};
      continue;
    }
    if (trimmed === 'END:VEVENT') {
      inEvent = false;
      flush();
      continue;
    }
    if (!inEvent) continue;
    const idx = line.indexOf(':');
    if (idx < 0) continue;
    const keyRaw = line.slice(0, idx).split(';')[0].toUpperCase();
    const value = unescapeIcsValue(line.slice(idx + 1));
    if (
      keyRaw === 'UID' ||
      keyRaw === 'SUMMARY' ||
      keyRaw === 'DESCRIPTION' ||
      keyRaw === 'LOCATION' ||
      keyRaw === 'DTSTART' ||
      keyRaw === 'DTEND'
    ) {
      props[keyRaw] = value;
    }
  }
  return events;
}
