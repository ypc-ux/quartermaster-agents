# ENGINE_RULES.md — hard constraints for the Boardroom Engine (TASK-060)

1. **Draft mode default.** Nothing publishes unless tier routing says so. T0 auto / T1 one-tap / T2 manual. Unknown → T2. Never auto-post raw calendar text.
2. **Humanizer gate.** Every draft scores >6.0 and passes the banned-word scan before it enters any queue.
3. **Compliance before content.** The screen (deny-list → PII → materiality → sanitize) runs BEFORE classification. Deny-list hits are never stored.
4. **Secrets.** GitHub repo secrets / Vercel env only. Never `NEXT_PUBLIC_`. Never commit a credential. New credential → `SECRETS_LEDGER.md` row (local checkout) the same turn.
5. **Calendar text is untrusted input** (prompt-injection surface): sanitize first, strict JSON schema on the classifier, event content never triggers tool calls.
6. **Idempotency.** Unique `(insight_id, platform)` + post-hash dedupe. Zero double-posts, ever.
7. **No deploy on Fridays.** No dashboard — email + repo queues are the UI.
8. **Verification honesty.** A cloud agent cannot run GitHub Actions or send real email. If you can't run a check, flag it for the local pass. Never claim verification you didn't perform.
9. **This repo is PUBLIC.** Everything committed is world-readable: no credentials, no client names, no private business notes. Milestone reports go to `M0_REPORT.md` (public-safe summary only).
