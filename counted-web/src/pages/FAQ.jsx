import { Link } from 'react-router-dom';
import Layout from '../components/Layout';

const faqs = [
  {
    q: 'Does calling actually work?',
    a: 'Yes. Congressional staffers track every call. When call volume spikes on an issue, it gets flagged to the senator directly. Studies show constituent calls are the single most effective form of contact \u2014 more than emails, tweets, or petitions. A personal phone call from a constituent cannot be ignored the way a form letter can.',
  },
  {
    q: 'How are the target senators ranked?',
    a: 'We score each senator on 10 factors including committee assignments (do they control war funding?), electoral vulnerability (are they up for reelection?), demonstrated ambivalence (have they expressed doubts?), and signal value (would their opposition change the political calculus?). The full methodology is public.',
  },
  {
    q: "I'm not in a target senator's state. Can I still help?",
    a: 'Absolutely. Call your own senators first \u2014 they represent you. Then share this tool. The most effective thing you can do beyond calling is get someone in a target state to call their senator.',
  },
  {
    q: 'Who built this?',
    a: 'Counted was built by Americans who believe that a 62% majority should be able to stop a war they oppose. We are not affiliated with any political party, campaign, or lobbying organization. The code is open source.',
  },
  {
    q: 'Is my data collected?',
    a: "No. Your zip code is processed entirely in your browser \u2014 it never hits a server. If you choose to log that you contacted a senator, that's stored in your browser's local storage. We don't have accounts, cookies, or tracking.",
  },
];

export default function FAQ() {
  return (
    <Layout>
      <div className="max-w-lg mx-auto px-4 py-10">
        <h1 className="text-2xl font-bold text-navy sm:text-3xl">
          Frequently Asked Questions
        </h1>

        <dl className="mt-8 space-y-6">
          {faqs.map((item) => (
            <div key={item.q}>
              <dt className="font-semibold text-navy">{item.q}</dt>
              <dd className="mt-1 text-navy/80 leading-relaxed">{item.a}</dd>
            </div>
          ))}
        </dl>

        <div className="mt-10">
          <Link
            to="/"
            className="text-amber font-medium hover:text-amber-dark underline"
          >
            &larr; Back to home
          </Link>
        </div>
      </div>
    </Layout>
  );
}
