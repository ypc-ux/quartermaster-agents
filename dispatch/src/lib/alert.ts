// Phone alerts via ntfy — zero keys, best-effort, never blocks the pipeline.

import { ENV } from './env';

export async function alert(title: string, message: string): Promise<void> {
  if (!ENV.ntfyTopic) return;
  try {
    await fetch(`https://ntfy.sh/${ENV.ntfyTopic}`, {
      method: 'POST',
      headers: { Title: title, Priority: 'default' },
      body: message,
      signal: AbortSignal.timeout(10_000),
    });
  } catch (e) {
    console.error('[alert] failed:', e);
  }
}
