import { useRef, useEffect } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import Layout from '../components/Layout';
import CallScript from '../components/CallScript';
import ContactChannels from '../components/ContactChannels';
import ActionLogger from '../components/ActionLogger';
import SharePrompt from '../components/SharePrompt';
import ScoreBar from '../components/ScoreBar';
import EmailCapture from '../components/EmailCapture';
import { getBySlug, getScript } from '../lib/senators';

const partyColor = { R: 'bg-rep', D: 'bg-dem', I: 'bg-ind' };
const partyLabel = { R: 'Republican', D: 'Democrat', I: 'Independent' };

export default function SenatorDetail() {
  const { slug } = useParams();
  const [searchParams] = useSearchParams();
  const zip = searchParams.get('zip') || '';
  const headingRef = useRef(null);

  const senator = getBySlug(slug);

  useEffect(() => {
    if (headingRef.current) {
      headingRef.current.focus();
    }
  }, [slug]);

  if (!senator) {
    return (
      <Layout>
        <div className="max-w-lg mx-auto px-4 py-16 text-center">
          <h1 className="text-2xl font-bold text-navy mb-4">
            Senator Not Found
          </h1>
          <p className="text-navy/70 mb-6">
            We couldn't find a senator with that identifier.
          </p>
          <Link
            to="/"
            className="text-amber font-medium hover:text-amber-dark underline"
          >
            &larr; Back to home
          </Link>
        </div>
      </Layout>
    );
  }

  const script = getScript(slug);

  return (
    <Layout>
      <div className="max-w-lg mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <h1
            ref={headingRef}
            tabIndex={-1}
            className="text-2xl font-bold text-navy outline-none sm:text-3xl"
          >
            {senator.name}
          </h1>
          <div className="mt-2 flex items-center gap-3 text-sm text-navy/70">
            <span className="flex items-center gap-1.5">
              <span
                className={`inline-block w-3 h-3 rounded-full ${partyColor[senator.party] || 'bg-gray-400'}`}
              />
              {partyLabel[senator.party] || senator.party}
            </span>
            <span>&middot;</span>
            <span>{senator.state}</span>
            {senator.up_2026 && (
              <>
                <span>&middot;</span>
                <span className="text-amber font-medium">Up in 2026</span>
              </>
            )}
          </div>
          <span className="inline-block mt-3 px-3 py-1 rounded-full bg-navy text-white text-xs font-semibold">
            Rank #{senator.rank}
          </span>
        </header>

        {/* Why they matter */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-navy mb-2">
            Why they matter
          </h2>
          <p className="text-navy/80 leading-relaxed mb-4">
            {senator.key_factor_long}
          </p>
          <ScoreBar
            score={senator.expected_impact}
            label="Expected Impact"
          />
        </section>

        {/* Call script */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-navy mb-2">
            Call script
          </h2>
          <CallScript script={script} senatorName={senator.name} />
        </section>

        {/* Contact info */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-navy mb-2">
            Contact info
          </h2>
          <ContactChannels contact={senator.contact} />
        </section>

        {/* Action */}
        <section className="mb-8">
          <ActionLogger senatorSlug={senator.slug} zip={zip} />
        </section>

        {/* Share */}
        <section className="mb-8">
          <SharePrompt
            senatorName={senator.name}
            senatorSlug={senator.slug}
          />
        </section>

        {/* Phase 3 placeholder */}
        <p className="text-sm text-navy/50 text-center mb-8">
          Be the first from {senator.state} to be Counted
        </p>

        {/* Email capture */}
        <section className="mb-8">
          <EmailCapture />
        </section>
      </div>
    </Layout>
  );
}
