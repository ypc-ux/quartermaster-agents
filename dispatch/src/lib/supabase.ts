import { createClient } from '@supabase/supabase-js';
import { ENV } from './env';

// Server-side singleton using the service-role key (bypasses RLS).
// Never imported from a client component.
let client: ReturnType<typeof createClient> | null = null;

export function getSupabase(): { from: (table: string) => any } {
  if (!client) {
    if (!ENV.supabaseUrl || !ENV.supabaseServiceRole) {
      throw new Error('Supabase not configured (SUPABASE_URL / SUPABASE_SERVICE_ROLE)');
    }
    client = createClient(ENV.supabaseUrl, ENV.supabaseServiceRole, {
      auth: { persistSession: false, autoRefreshToken: false },
    });
  }
  return client.schema('dispatch' as never) as unknown as { from: (table: string) => any };
}
