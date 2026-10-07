// Server-side env access. Never export any of this to the client bundle.
// No NEXT_PUBLIC_ keys exist in this app by design.

export const ENV = {
  supabaseUrl: process.env.SUPABASE_URL ?? '',
  supabaseServiceRole: process.env.SUPABASE_SERVICE_ROLE ?? '',
  openrouterKey: process.env.OPENROUTER_API_KEY ?? '',
  groqKey: process.env.GROQ_API_KEY ?? '',
  resendKey: process.env.RESEND_API_KEY ?? '',
  notifyEmail: process.env.DISPATCH_NOTIFY_EMAIL ?? '',
  engineMode: process.env.ENGINE_MODE ?? 'draft',
  cronSecret: process.env.CRON_SECRET ?? '',
  gcalIcsUrl: process.env.GCAL_ICS_URL ?? '',
  classifyModel:
    process.env.CLASSIFY_MODEL ??
    'nvidia/nemotron-3-super-120b-a12b:free,google/gemma-4-26b-a4b-it:free,nvidia/nemotron-3.5-lightning:free',
  draftModel:
    process.env.DRAFT_MODEL ??
    'nvidia/nemotron-3-super-120b-a12b:free,google/gemma-4-31b-it:free,nvidia/nemotron-3.5-lightning:free',
  groqClassifyModel: process.env.GROQ_CLASSIFY_MODEL ?? 'qwen/qwen3.8-27b',
  groqDraftModel: process.env.GROQ_DRAFT_MODEL ?? 'openai/gpt-oss-120b',
  budgetUsd: Number(process.env.LLM_DAILY_BUDGET_USD ?? '0.50') || 0.5,
  maxItemsPerRun: Number(process.env.MAX_ITEMS_PER_RUN ?? '2') || 2,
  xApiKey: process.env.X_API_KEY ?? '',
  xApiSecret: process.env.X_API_SECRET ?? '',
  xAccessToken: process.env.X_ACCESS_TOKEN ?? '',
  xAccessSecret: process.env.X_ACCESS_SECRET ?? '',
} as const;

export function isConfigured(): boolean {
  return Boolean(ENV.supabaseUrl && ENV.supabaseServiceRole);
}
