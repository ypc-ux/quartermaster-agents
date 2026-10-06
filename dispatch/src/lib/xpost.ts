// X (Twitter) posting — OAuth 1.0a, X API v2.
// Only reachable when ENGINE_MODE=active AND all four X_* keys exist.
// Until then, publish logs "would post" rows in draft mode. Never enabled by default.

import crypto from 'node:crypto';
import { ENV } from './env';

function oauth1Header(method: string, url: string, bodyParams: Record<string, string>): string {
  const enc = encodeURIComponent;
  const oauthParams: Record<string, string> = {
    oauth_consumer_key: ENV.xApiKey,
    oauth_nonce: crypto.randomBytes(16).toString('hex'),
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: Math.floor(Date.now() / 1000).toString(),
    oauth_token: ENV.xAccessToken,
    oauth_version: '1.0',
  };
  const all = { ...oauthParams, ...bodyParams };
  const paramString = Object.keys(all)
    .sort()
    .map((k) => `${enc(k)}=${enc(all[k])}`)
    .join('&');
  const base = `${method.toUpperCase()}&${enc(url)}&${enc(paramString)}`;
  const signingKey = `${enc(ENV.xApiSecret)}&${enc(ENV.xAccessSecret)}`;
  const signature = crypto.createHmac('sha1', signingKey).update(base).digest('base64');
  oauthParams.oauth_signature = signature;
  return (
    'OAuth ' +
    Object.keys(oauthParams)
      .sort()
      .map((k) => `${enc(k)}="${enc(oauthParams[k])}"`)
      .join(', ')
  );
}

export function hasXKeys(): boolean {
  return Boolean(ENV.xApiKey && ENV.xApiSecret && ENV.xAccessToken && ENV.xAccessSecret);
}

export async function postToX(text: string): Promise<{ ok: boolean; id?: string; error?: string }> {
  try {
    const url = 'https://api.x.com/2/tweets';
    const authorization = oauth1Header('POST', url, { text });
    const res = await fetch(url, {
      method: 'POST',
      headers: { Authorization: authorization, 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
      signal: AbortSignal.timeout(20_000),
    });
    if (!res.ok) {
      return { ok: false, error: `HTTP ${res.status}: ${(await res.text()).slice(0, 200)}` };
    }
    const data = await res.json();
    return { ok: true, id: data?.data?.id as string | undefined };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : String(e) };
  }
}
