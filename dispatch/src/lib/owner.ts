// Owner mode — the one-pager's action buttons are gated behind a cookie set
// via /api/owner with the ADMIN_KEY. When ADMIN_KEY is unset (local dev),
// everything is treated as owner. Server actions enforce the same check.

import { cookies } from 'next/headers';
import { ENV } from './env';

export const OWNER_COOKIE = 'dispatch_admin';

export async function isOwner(): Promise<boolean> {
  if (!ENV.adminKey) return true; // local dev without a key configured
  const store = await cookies();
  const value = store.get(OWNER_COOKIE)?.value ?? '';
  // Constant-time-ish comparison to avoid trivial timing leaks.
  if (value.length !== ENV.adminKey.length) return false;
  let diff = 0;
  for (let i = 0; i < value.length; i++) {
    diff |= value.charCodeAt(i) ^ ENV.adminKey.charCodeAt(i);
  }
  return diff === 0;
}
