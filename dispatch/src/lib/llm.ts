// LLM layer — the ONLY place judgment happens.
// Deterministic fallbacks: cost-cap over -> null (caller falls back to template),
// bad JSON -> null, 3x exponential backoff. Free tier first (OpenRouter :free / Groq).

import { ENV } from './env';
import { getSupabase } from './supabase';
import { VOICE_RULES, INJECTION_GUARD } from './voice';

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export interface LlmResult {
  text: string;
  content: string;
  reasoning: string;
  usageUsd: number;
  provider: 'openrouter' | 'groq';
  truncated: boolean;
}

async function budgetOk(): Promise<boolean> {
  const today = new Date().toISOString().slice(0, 10);
  const { data } = await getSupabase()
    .from('budget')
    .select('spend_usd')
    .eq('day', today)
    .maybeSingle();
  return (Number(data?.spend_usd ?? 0)) < ENV.budgetUsd;
}

async function recordSpend(usd: number): Promise<void> {
  if (usd <= 0) return;
  const today = new Date().toISOString().slice(0, 10);
  const sb = getSupabase();
  const { data } = await sb.from('budget').select('spend_usd').eq('day', today).maybeSingle();
  const total = Number(data?.spend_usd ?? 0) + usd;
  await sb.from('budget').upsert({ day: today, spend_usd: total }, { onConflict: 'day' });
}

function estimateCost(provider: string, model: string, usage: unknown): number {
  const u = usage as { prompt_tokens?: number; completion_tokens?: number } | undefined;
  if (!u) return 0;
  if (model.includes(':free') || provider === 'groq') return 0;
  const prompt = u.prompt_tokens ?? 0;
  const completion = u.completion_tokens ?? 0;
  return Math.round(((prompt * 0.15 + completion * 0.6) / 1_000_000) * 1_000_000) / 1_000_000;
}

export async function chatCompletion(opts: {
  system: string;
  user: string;
  maxTokens?: number;
  json?: boolean;
  temperature?: number;
  model?: string;
}): Promise<LlmResult | null> {
  const hasGroq = Boolean(ENV.groqKey);
  if (!(await budgetOk())) {
    console.error('[llm] budget exceeded — falling back');
    return null;
  }
  const provider = hasGroq ? 'groq' : 'openrouter';
  const defaultModel =
    provider === 'groq' ? ENV.groqDraftModel : ENV.draftModel;
  // Cascade: try each model in the comma-separated list until one succeeds.
  const models = (opts.model ?? defaultModel)
    .split(',')
    .map((m) => m.trim())
    .filter(Boolean);
  const maxTokens = opts.maxTokens ?? 512;
  let lastError = '';
  console.error(`[llm] provider=${provider} models=${models.join('|')}`);

  for (const model of models) {
    for (let attempt = 1; attempt <= 2; attempt++) {
      try {
        const body: Record<string, unknown> = {
          model,
          messages: [
            { role: 'system', content: opts.system },
            { role: 'user', content: opts.user },
          ],
          max_tokens: maxTokens,
          temperature: opts.temperature ?? 0.7,
        };

        const url =
          provider === 'groq'
            ? 'https://api.groq.com/openai/v1/chat/completions'
            : 'https://openrouter.ai/api/v1/chat/completions';
        const headers: Record<string, string> = { 'Content-Type': 'application/json' };
        headers.Authorization = `Bearer ${provider === 'groq' ? ENV.groqKey : ENV.openrouterKey}`;
        if (provider === 'openrouter') headers['HTTP-Referer'] = 'https://dispatch.vercel.app';

        const res = await fetch(url, {
          method: 'POST',
          headers,
          body: JSON.stringify(body),
          signal: AbortSignal.timeout(60_000),
        });
        if (!res.ok) {
          lastError = `${model}: HTTP ${res.status}`;
          throw new Error(lastError);
        }
        const data = await res.json();
        const msg = data?.choices?.[0]?.message ?? {};
        // Reasoning models can return content:null with the planned output inside
        // `reasoning`. Prefer content, fall back to reasoning.
        const content: string = msg.content || '';
        const reasoning: string = msg.reasoning || '';
        const text: string = content || reasoning;
        if (!text) {
          lastError = `${model}: empty completion`;
          throw new Error(lastError);
        }
        const truncated = data?.choices?.[0]?.finish_reason === 'length';
        const usageUsd = estimateCost(provider, model, data?.usage);
        await recordSpend(usageUsd);
        return { text, content, reasoning, usageUsd, provider, truncated };
      } catch (e) {
        lastError = e instanceof Error ? e.message : String(e);
        await sleep(attempt * 800);
      }
    }
  }
  console.error('[llm] all models failed:', lastError);
  return null;
}

export interface Classification {
  topic: string;
  pillar: 'building_public' | 'sales_confidence' | 'privacy_security' | 'other';
  confidence: number;
}

function extractJson(text: string): Record<string, unknown> | null {
  const cleaned = text.replace(/```json/gi, '').replace(/```/g, '').trim();
  const match = /\{[\s\S]*\}/.exec(cleaned);
  if (!match) return null;
  try {
    const parsed: unknown = JSON.parse(match[0]);
    return parsed && typeof parsed === 'object' ? (parsed as Record<string, unknown>) : null;
  } catch {
    return null;
  }
}

export async function classifyEvent(item: {
  title: string;
  description: string;
}): Promise<Classification | null> {
  const result = await chatCompletion({
    system:
      'You classify calendar events for a content pipeline. Output strict JSON only with keys: ' +
      'topic (max 3 words, lowercase), pillar (one of: building_public, sales_confidence, privacy_security, other), ' +
      'confidence (0.0 to 1.0). ' +
      INJECTION_GUARD,
    user:
      'BEGIN EVENT DATA\nTITLE: ' +
      item.title.slice(0, 200) +
      '\nDESCRIPTION: ' +
      item.description.slice(0, 1500) +
      '\nEND EVENT DATA\n\nClassify.',
    json: true,
    maxTokens: 300,
    temperature: 0.2,
    model: ENV.groqKey ? ENV.groqClassifyModel : ENV.classifyModel,
  });
  if (!result) return null;
  const parsed = extractJson(result.text);
  if (!parsed) return null;
  const topic = typeof parsed.topic === 'string' ? parsed.topic.slice(0, 60) : '';
  const pillar = String(parsed.pillar ?? 'other');
  const confidence = Number(parsed.confidence);
  if (!topic) return null;
  const validPillars = ['building_public', 'sales_confidence', 'privacy_security', 'other'];
  return {
    topic,
    pillar: (validPillars.includes(pillar) ? pillar : 'other') as Classification['pillar'],
    confidence: Number.isFinite(confidence) ? confidence : 0,
  };
}

const REASONING_MARKERS = [
  "here's a thinking process",
  'here is a thinking process',
  'thinking process',
  'analyze the request',
  'step 1:',
  '1. **analyze',
] as const;

// The model may echo prompt-template text instead of writing a post.
const PLACEHOLDER_RE =
  /^(the post text|your post here|insert post here|write your post here|<post>|\[post\]|post goes here)[.!]*$/i;

function extractPost(result: LlmResult): string | null {
  // Two-pass: the finished JSON usually lands in `content`; reasoning models
  // sometimes leave content null and the planned JSON lives in `reasoning`.
  for (const text of [result.content, result.reasoning]) {
    if (!text) continue;
    const parsed = extractJson(text);
    const candidate = parsed?.post;
    if (typeof candidate === 'string') {
      const post = cleanPost(candidate);
      if (post.length >= 40 && !PLACEHOLDER_RE.test(post)) {
        return post;
      }
    }
  }
  // Plain-text tolerance: use the raw output only if it is not a ramble.
  const raw = result.text.trim();
  const lower = raw.toLowerCase();
  const rambled = REASONING_MARKERS.some((m) => lower.includes(m));
  if (rambled) return null;
  const post = cleanPost(raw);
  if (post.length >= 40 && !PLACEHOLDER_RE.test(post)) {
    return post;
  }
  return null;
}

export async function draftPost(item: {
  title: string;
  description: string;
  topic: string;
}): Promise<string | null> {
  const systemBase =
    'You write short social posts in a fixed brand voice. ' +
    VOICE_RULES +
    INJECTION_GUARD +
    '\nRespond with a JSON object that has one key "post". The value is the finished post, ' +
    'maximum 280 characters, no emoji. No hashtags unless the event data contains one. ' +
    'Do not echo this instruction. Do not write anything besides the JSON object.';
  const user =
    'BEGIN EVENT DATA\nTITLE: ' +
    item.title.slice(0, 200) +
    '\nDESCRIPTION: ' +
    item.description.slice(0, 1500) +
    '\nTOPIC: ' +
    item.topic.slice(0, 60) +
    '\nEND EVENT DATA\n\nWrite the post.';

  for (let attempt = 0; attempt < 2; attempt++) {
    const result = await chatCompletion({
      system:
        attempt === 0
          ? systemBase
          : systemBase + '\nRetry: output ONLY the JSON object now. No planning, no thinking out loud.',
      user,
      maxTokens: 3000,
      temperature: attempt === 0 ? 0.8 : 0.4,
      model: ENV.groqKey ? ENV.groqDraftModel : ENV.draftModel,
    });
    if (!result) return null; // LLM layer fully failed — caller falls back
    const post = extractPost(result);
    if (post) return post;
    if (result.truncated) {
      // Cut off mid-generation; one retry with a calmer temperature is worth it.
      continue;
    }
    if (attempt === 1) return null;
  }
  return null;
}

/** Voice rule enforced in code: no emoji, collapse whitespace, cap length. */
function cleanPost(text: string): string {
  return text
    .replace(/\p{Extended_Pictographic}/gu, '')
    .replace(/[\u200B-\u200F\uFEFF]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 280);
}

/** Deterministic template fallback — factual, no claims, no slop. Used only when
 *  the LLM is unavailable or the daily cost cap is hit. */
export function fallbackTemplate(item: { title: string; description: string }): string {
  const clean = item.title
    .replace(/^#(public|auto)\b/i, '')
    .replace(/^(content|launch):\s*/i, '')
    .trim();
  const subject = clean || item.description.split('\n')[0]?.trim() || 'Today';
  const date = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  return `${subject.slice(0, 260)}. ${date}.`.slice(0, 280);
}

