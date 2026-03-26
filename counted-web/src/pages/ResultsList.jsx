import { useState, useRef, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import Layout from '../components/Layout';
import SenatorCard from '../components/SenatorCard';
import ZipInput from '../components/ZipInput';
import { useSenatorLookup } from '../hooks/useSenatorLookup';
import { senators as allSenatorsList } from '../lib/senators';

export default function ResultsList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const zip = searchParams.get('zip');
  const [showAll, setShowAll] = useState(false);
  const headingRef = useRef(null);

  const lookup = useSenatorLookup(zip);

  useEffect(() => {
    if (zip && headingRef.current) {
      headingRef.current.focus();
    }
  }, [zip]);

  if (!zip) {
    return (
      <Layout>
        <div className="max-w-lg mx-auto px-4 py-12 text-center">
          <h1 className="text-2xl font-bold text-navy mb-6">
            Find Your Senators
          </h1>
          <ZipInput onSubmit={(z) => setSearchParams({ zip: z })} />
        </div>
      </Layout>
    );
  }

  const { state, mySenators, topTargets, noVotingSenators } = lookup;

  const mySenatorSlugs = new Set(mySenators.map((s) => s.slug));
  const top10 = topTargets
    .filter((s) => !mySenatorSlugs.has(s.slug))
    .slice(0, 10);

  const allSorted = [...allSenatorsList].sort((a, b) => a.rank - b.rank);

  return (
    <Layout>
      <div className="max-w-lg mx-auto px-4 py-8">
        {noVotingSenators && (
          <div className="mb-6 rounded-lg bg-amber/10 border border-amber/30 p-4 text-navy/90 text-sm">
            Your area (DC/territory) doesn't have voting senators, but you can
            still make an impact by calling the most persuadable senators below.
          </div>
        )}

        {mySenators.length > 0 && (
          <section className="mb-10">
            <h2
              ref={headingRef}
              tabIndex={-1}
              className="text-xl font-bold text-navy mb-4 outline-none"
            >
              Your Senators
            </h2>
            <div className="space-y-3">
              {mySenators.map((s) => (
                <SenatorCard
                  key={s.slug}
                  senator={s}
                  isMySenator
                  rank={s.rank}
                />
              ))}
            </div>
          </section>
        )}

        <section className="mb-10">
          <h2
            ref={mySenators.length === 0 ? headingRef : undefined}
            tabIndex={mySenators.length === 0 ? -1 : undefined}
            className="text-xl font-bold text-navy mb-4 outline-none"
          >
            Top National Targets
          </h2>
          <div className="space-y-3">
            {top10.map((s) => (
              <SenatorCard key={s.slug} senator={s} rank={s.rank} />
            ))}
          </div>
        </section>

        <div className="text-center">
          <button
            onClick={() => setShowAll((v) => !v)}
            className="text-amber font-medium hover:text-amber-dark underline"
          >
            {showAll ? 'Hide Full List' : 'Show All 100 Senators'}
          </button>
        </div>

        {showAll && (
          <section className="mt-6">
            <h2 className="text-xl font-bold text-navy mb-4">All Senators</h2>
            <div className="space-y-3">
              {allSorted.map((s) => (
                <SenatorCard
                  key={s.slug}
                  senator={s}
                  isMySenator={mySenatorSlugs.has(s.slug)}
                  rank={s.rank}
                />
              ))}
            </div>
          </section>
        )}
      </div>
    </Layout>
  );
}
