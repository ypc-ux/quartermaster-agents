// Sanitize hostile calendar input. Strips control/zero-width chars,
// normalizes whitespace, caps length.

export function sanitizeText(input: string, maxLen = 4000): string {
  return input
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F\u200B-\u200F\uFEFF]/g, '')
    .replace(/\r\n?/g, '\n')
    .replace(/[ \t]+/g, ' ')
    .trim()
    .slice(0, maxLen);
}
