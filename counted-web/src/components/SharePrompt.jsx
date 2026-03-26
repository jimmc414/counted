import { useState } from 'react';
import { twitterIntent, smsBody, copyToClipboard } from '../lib/shareUrls';

export default function SharePrompt({ senatorName, senatorSlug }) {
  const [copied, setCopied] = useState(false);
  const siteUrl = window.location.origin;
  const shareText = `I just called Senator ${senatorName} to oppose the $200B war supplemental. Find your senators and be counted: ${siteUrl}`;

  function handleCopy() {
    copyToClipboard(shareText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <div className="space-y-3">
      <p className="text-navy font-medium text-sm text-center">
        Spread the word
      </p>
      <div className="flex gap-3">
        <a
          href={twitterIntent(shareText, siteUrl)}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 text-center bg-navy hover:bg-navy-light text-white font-medium py-2 px-3 rounded text-sm transition-colors"
        >
          Share on X
        </a>
        <a
          href={smsBody(shareText)}
          className="flex-1 text-center bg-navy hover:bg-navy-light text-white font-medium py-2 px-3 rounded text-sm transition-colors"
        >
          Text a Friend
        </a>
        <button
          type="button"
          onClick={handleCopy}
          className="flex-1 bg-navy hover:bg-navy-light text-white font-medium py-2 px-3 rounded text-sm transition-colors"
        >
          {copied ? 'Copied!' : 'Copy Link'}
        </button>
      </div>
    </div>
  );
}
