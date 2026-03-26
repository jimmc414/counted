import { Link } from 'react-router-dom';
import Layout from '../components/Layout';

export default function About() {
  return (
    <Layout>
      <div className="max-w-lg mx-auto px-4 py-10">
        <h1 className="text-2xl font-bold text-navy sm:text-3xl">
          What is Counted?
        </h1>

        <div className="mt-6 space-y-5 text-navy/85 leading-relaxed">
          <p>
            Counted is a non-partisan tool that helps Americans contact their
            senators about the $200 billion Iran war supplemental funding. 62%
            of Americans oppose this war, but that opposition is invisible and
            uncoordinated. We make it visible.
          </p>

          <p>
            We use a public, transparent algorithm to rank all 100 senators by
            how likely they are to respond to constituent pressure. The ranking
            combines committee assignments, electoral vulnerability, stated
            positions, and strategic value. Every factor and weight is published
            openly.
          </p>

          <p>
            This is not about left or right. It's about whether Congress
            authorizes wars before funding them. The Constitution gives that
            power to Congress, not the executive. We believe the 62% majority
            deserves to be heard.
          </p>

          <p>
            Counted doesn't send messages on your behalf or collect personal
            data beyond what you choose to store locally. Your zip code never
            leaves your browser. We help you find the right number, give you
            the words, and count that you showed up.
          </p>
        </div>

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
