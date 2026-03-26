/** Build a Twitter/X intent URL with pre-filled text and link. */
export function twitterIntent(text, url) {
  const params = new URLSearchParams({ text, url });
  return `https://twitter.com/intent/tweet?${params}`;
}

/** Build an sms: URI with an encoded body. */
export function smsBody(text) {
  return `sms:?body=${encodeURIComponent(text)}`;
}

/** Copy text to the clipboard (async, returns a promise). */
export async function copyToClipboard(text) {
  return navigator.clipboard.writeText(text);
}
