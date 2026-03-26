export default function ScoreBar({ score, label = 'Impact Score' }) {
  const pct = Math.round(score * 100);

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium text-navy">{pct}%</span>
      </div>
      <div
        role="meter"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${label}: ${pct}%`}
        className="h-2 w-full bg-navy/20 rounded-full overflow-hidden"
      >
        <div
          className="h-full bg-amber rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
