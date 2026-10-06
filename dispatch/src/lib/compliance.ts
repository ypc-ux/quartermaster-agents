// Compliance screen — runs BEFORE any LLM or public action.
// deny  -> event stored only as a redacted shell (title "[redacted]", no text), held T2.
// hold  -> stored, but held as T2, never drafted automatically.
// pass  -> tier assignment decides autonomy.
// Matching is word-boundary aware: "nda" must be a standalone token, never a
// substring of "calendar".

const DENY_TERMS = [
  'secria internals',
  'attorney-client',
  'privileged',
  'confidential',
  'counsel',
  'term sheet',
  'board deck',
  'non-disclosure',
  'nda',
  'trade secret',
  'classified',
  'do not share',
  'off the record',
  'internal-only',
  'acquisition target',
  'lawsuit',
  'settlement',
  'payroll',
  'revenue forecast',
] as const;

const HOLD_TERMS = [
  'internal',
  'private',
  'family',
  'doctor',
  'medical',
  'therapy',
  'bank',
  'account number',
  'password',
  'api key',
  'secret key',
  'm&a',
  'legal review',
  'tax',
  'finances',
  'client deal',
  'investor update',
] as const;

const PUBLIC_MARKERS = [
  '#public',
  '[public]',
  'public:',
  'content:',
  'launch',
  'podcast',
  'webinar',
  'conference',
  'keynote',
  'workshop',
  'product demo',
  'announce',
  'meetup',
  'interview',
  'ship',
] as const;

function buildMatchers(terms: readonly string[]): RegExp[] {
  return terms.map((t) => {
    const escaped = t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    // \b only works next to word chars — skip it when the term starts/ends
    // with a non-word char (e.g. "#public" must not require a boundary at "#").
    const lead = /^\w/.test(t) ? '\\b' : '';
    const trail = /\w$/.test(t) ? '\\b' : '';
    return new RegExp(`${lead}${escaped}${trail}`, 'i');
  });
}

const DENY_RE = buildMatchers(DENY_TERMS);
const HOLD_RE = buildMatchers(HOLD_TERMS);
const MARKER_RE = buildMatchers(PUBLIC_MARKERS);

export type ComplianceVerdict = 'pass' | 'deny' | 'hold';

export interface ScreenResult {
  verdict: ComplianceVerdict;
  reason: string;
}

export function screenEvent(title: string, description: string): ScreenResult {
  const text = `${title} ${description}`.toLowerCase();
  for (let i = 0; i < DENY_RE.length; i++) {
    if (DENY_RE[i].test(text)) {
      return { verdict: 'deny', reason: `deny-list term: ${DENY_TERMS[i]}` };
    }
  }
  for (let i = 0; i < HOLD_RE.length; i++) {
    if (HOLD_RE[i].test(text)) {
      return { verdict: 'hold', reason: `sensitive term: ${HOLD_TERMS[i]}` };
    }
  }
  return { verdict: 'pass', reason: '' };
}

export type Tier = 't0' | 't1' | 't2';

/** T0 auto / T1 one-tap / T2 manual. Unknown -> T2. */
export function assignTier(title: string, description: string, verdict: ComplianceVerdict): Tier {
  if (verdict !== 'pass') return 't2';
  const text = `${title} ${description}`.toLowerCase();
  const explicitAuto = text.includes('#auto');
  const markedPublic = MARKER_RE.some((re) => re.test(text));
  if (explicitAuto) return 't0';
  if (markedPublic) return 't1';
  return 't2';
}

