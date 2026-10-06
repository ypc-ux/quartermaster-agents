// Humanizer gate — deterministic code, not an LLM.
// Hard pass: zero banned words AND score > 6.0.

import { BANNED_WORDS } from './voice';

const CLICHES = [
  'at the end of the day',
  'let’s face it',
  "let's face it",
  'that being said',
  'if you will',
  'it goes without saying',
  'outside the box',
  'think outside',
  'in the world of',
  'dive into',
  'embark on',
] as const;

export interface GateResult {
  passed: boolean;
  score: number;
  bannedHits: string[];
  note: string;
}

function syllableCount(word: string): number {
  const w = word.toLowerCase().replace(/[^a-z]/g, '');
  if (!w) return 0;
  const groups = w.match(/[aeiouy]+/g);
  let count = groups ? groups.length : 1;
  if (w.endsWith('e') && count > 1) count -= 1;
  return Math.max(1, count);
}

/** Flesch reading ease 0-100 (higher = easier). */
function fleschReadingEase(text: string): number {
  const sentences = text.split(/[.!?]+/).map((s) => s.trim()).filter(Boolean);
  const sentenceCount = sentences.length || 1;
  const words = text.split(/\s+/).filter((w) => /[a-zA-Z0-9]/.test(w));
  const wordCount = words.length || 1;
  const syllables = words.reduce((sum, w) => sum + syllableCount(w), 0);
  return 206.835 - 1.015 * (wordCount / sentenceCount) - 84.6 * (syllables / wordCount);
}

export function gateDraft(text: string): GateResult {
  const lower = text.toLowerCase();
  const bannedHits = BANNED_WORDS.filter((w) => lower.includes(w));
  const clicheHits = CLICHES.filter((c) => lower.includes(c));

  let score = fleschReadingEase(text) / 10;
  if (/[0-9]/.test(text)) score += 0.5; // receipts beat adjectives
  score -= clicheHits.length * 0.5;
  score = Math.round(Math.max(0, Math.min(10, score)) * 10) / 10;

  const notes: string[] = [];
  if (bannedHits.length > 0) notes.push(`banned words: ${bannedHits.join(', ')}`);
  if (clicheHits.length > 0) notes.push(`clichés: ${clicheHits.length}`);
  if (!/[0-9]/.test(text)) notes.push('no receipt (no number)');

  const passed = bannedHits.length === 0 && score > 6.0;
  return { passed, score, bannedHits, note: notes.join('; ') };
}
