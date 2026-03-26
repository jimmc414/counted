import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import ZipInput from '../components/ZipInput';
import CounterPlaceholder from '../components/CounterPlaceholder';

const steps = [
  { num: '1', text: 'Enter your zip code' },
  { num: '2', text: 'Call your senators with our script' },
  { num: '3', text: 'Be counted among Americans who spoke up' },
];

export default function Landing() {
  const navigate = useNavigate();

  return (
    <Layout>
      <div className="max-w-lg mx-auto px-4 py-12 text-center">
        <h1 className="text-3xl font-bold text-navy leading-tight sm:text-4xl">
          Your senators need to hear from you.
        </h1>

        <p className="mt-4 text-lg text-navy/80">
          62% of Americans oppose the $200B Iran war supplemental. Congress
          votes soon. Enter your zip code, call your senators, and be counted.
        </p>

        <div className="mt-8">
          <ZipInput onSubmit={(zip) => navigate(`/results?zip=${zip}`)} />
        </div>

        <div className="mt-6">
          <CounterPlaceholder />
        </div>

        <section className="mt-16 text-left">
          <h2 className="text-xl font-semibold text-navy mb-6 text-center">
            How it works
          </h2>
          <ol className="space-y-4">
            {steps.map((s) => (
              <li key={s.num} className="flex items-start gap-4">
                <span className="flex-shrink-0 w-8 h-8 rounded-full bg-navy text-white flex items-center justify-center font-bold text-sm">
                  {s.num}
                </span>
                <span className="text-navy/90 pt-1">{s.text}</span>
              </li>
            ))}
          </ol>
        </section>
      </div>
    </Layout>
  );
}
