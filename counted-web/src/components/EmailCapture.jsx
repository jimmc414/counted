import { useState } from 'react';

const STORAGE_KEY = 'counted_email';

function getSavedEmail() {
  try {
    return localStorage.getItem(STORAGE_KEY) || '';
  } catch {
    return '';
  }
}

export default function EmailCapture() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(() => !!getSavedEmail());

  function handleSubmit(e) {
    e.preventDefault();
    if (!email) return;
    localStorage.setItem(STORAGE_KEY, email);
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <p className="text-green-700 text-sm text-center font-medium">
        &#10003; You're signed up
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <div className="flex gap-2">
        <label htmlFor="email-capture" className="sr-only">
          Email address
        </label>
        <input
          id="email-capture"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber"
        />
        <button
          type="submit"
          className="bg-amber hover:bg-amber-dark text-white font-medium py-2 px-4 rounded text-sm transition-colors"
        >
          Keep Me Updated
        </button>
      </div>
      <p className="text-gray-400 text-xs text-center">
        We'll notify you when the vote happens. No spam.
      </p>
    </form>
  );
}
