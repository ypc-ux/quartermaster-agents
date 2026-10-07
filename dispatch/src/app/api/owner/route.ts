// Owner mode gate: POST with the ADMIN_KEY sets an httpOnly cookie that
// unlocks the one-pager's action buttons. GET ?logout=1 clears it.
// When ADMIN_KEY is unset (local dev), the page is open anyway.

import { NextRequest } from 'next/server';
import { ENV } from '@/lib/env';
import { OWNER_COOKIE } from '@/lib/owner';

export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest): Promise<Response> {
  const form = await req.formData();
  const key = String(form.get('key') ?? '');
  if (!ENV.adminKey || key !== ENV.adminKey) {
    return new Response('Wrong key.', { status: 403 });
  }
  const res = new Response(null, { status: 302, headers: { location: '/' } });
  res.headers.append(
    'set-cookie',
    `${OWNER_COOKIE}=${ENV.adminKey}; Path=/; HttpOnly; Max-Age=2592000; SameSite=Lax`
  );
  return res;
}

export async function GET(req: NextRequest): Promise<Response> {
  if (req.nextUrl.searchParams.get('logout') === '1') {
    const res = new Response(null, { status: 302, headers: { location: '/' } });
    res.headers.append('set-cookie', `${OWNER_COOKIE}=; Path=/; HttpOnly; Max-Age=0`);
    return res;
  }
  return new Response('Owner mode: POST the ADMIN_KEY as form field "key".', { status: 405 });
}
