import { useLocalActions } from '../hooks/useLocalActions';

export default function ActionLogger({ senatorSlug, zip = '' }) {
  const { logAction, hasContacted } = useLocalActions();
  const contacted = hasContacted(senatorSlug);

  function handleClick() {
    logAction(senatorSlug, 'called', zip);
  }

  if (contacted) {
    return (
      <div
        aria-live="polite"
        className="bg-green-50 border border-green-300 rounded-lg p-4 text-center"
      >
        <span className="text-green-700 font-semibold text-lg">
          &#10003; You've Been Counted
        </span>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className="w-full bg-amber hover:bg-amber-dark text-white font-semibold py-3 px-6 rounded-lg text-lg transition-colors"
    >
      I Contacted This Senator
    </button>
  );
}
