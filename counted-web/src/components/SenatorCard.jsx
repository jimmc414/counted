import { Link } from 'react-router-dom';
import ScoreBar from './ScoreBar';

const partyStyle = {
  R: { dot: 'bg-rep', label: 'R' },
  D: { dot: 'bg-dem', label: 'D' },
  I: { dot: 'bg-ind', label: 'I' },
};

export default function SenatorCard({ senator, isMySenator, rank }) {
  const party = partyStyle[senator.party] || partyStyle.I;

  return (
    <Link
      to={`/senator/${senator.slug}`}
      className="block border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-gray-300 transition-all no-underline"
    >
      <div className="flex items-start gap-3">
        <span className="text-gray-400 font-medium text-sm mt-1 w-6 text-right shrink-0">
          {rank}
        </span>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-navy font-semibold text-lg leading-tight">
              {senator.name}
            </h3>
            <span className="flex items-center gap-1 text-sm text-gray-600">
              <span
                className={`inline-block w-2.5 h-2.5 rounded-full ${party.dot}`}
                aria-hidden="true"
              />
              {party.label}
            </span>
            <span className="text-sm text-gray-500">{senator.state}</span>
            {isMySenator && (
              <span className="bg-amber text-white text-xs font-semibold px-2 py-0.5 rounded">
                Your Senator
              </span>
            )}
          </div>

          {senator.key_factor_short && (
            <p className="text-gray-600 text-sm mt-1">
              {senator.key_factor_short}
            </p>
          )}

          <div className="mt-2">
            <ScoreBar score={senator.expected_impact} />
          </div>
        </div>
      </div>
    </Link>
  );
}
