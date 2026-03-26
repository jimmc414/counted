import { useState, useRef, useEffect } from 'react';

export default function ZipInput({ onSubmit }) {
  const [zip, setZip] = useState('');
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  function handleChange(e) {
    const val = e.target.value.replace(/\D/g, '').slice(0, 5);
    setZip(val);
    if (error) setError('');
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (zip.length !== 5) {
      setError('Please enter a valid 5-digit ZIP code.');
      return;
    }
    onSubmit(zip);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <label htmlFor="zip-input" className="block text-navy font-medium mb-1">
          Your ZIP Code
        </label>
        <input
          ref={inputRef}
          id="zip-input"
          type="text"
          inputMode="numeric"
          pattern="[0-9]{5}"
          maxLength={5}
          value={zip}
          onChange={handleChange}
          placeholder="e.g. 20500"
          aria-describedby={error ? 'zip-error' : undefined}
          aria-invalid={error ? 'true' : undefined}
          className="w-full border border-gray-300 rounded px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-amber"
        />
        {error && (
          <p id="zip-error" role="alert" className="text-red-600 text-sm mt-1">
            {error}
          </p>
        )}
      </div>
      <button
        type="submit"
        className="w-full bg-amber hover:bg-amber-dark text-white font-semibold py-3 px-6 rounded text-lg transition-colors"
      >
        Find My Senators
      </button>
    </form>
  );
}
