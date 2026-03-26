import { useState } from 'react';

export default function CallScript({ script, senatorName }) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(script).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <div className="space-y-3">
      <blockquote className="bg-gray-50 border-l-4 border-amber rounded p-4 text-gray-700 text-sm leading-relaxed whitespace-pre-line">
        {script}
      </blockquote>
      <button
        type="button"
        onClick={handleCopy}
        className="bg-navy hover:bg-navy-light text-white font-medium py-2 px-4 rounded text-sm transition-colors"
      >
        {copied ? 'Copied!' : 'Copy Script'}
      </button>
    </div>
  );
}
