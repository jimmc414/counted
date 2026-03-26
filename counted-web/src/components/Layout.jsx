import { Link, Outlet } from 'react-router-dom';

export default function Layout({ children }) {
  return (
    <>
      <a href="#main-content" className="skip-link">
        Skip to content
      </a>

      <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
        <div className="max-w-lg mx-auto px-4 py-3">
          <Link to="/" className="text-navy text-2xl font-bold no-underline">
            Counted.
          </Link>
        </div>
      </header>

      <main id="main-content" className="max-w-lg mx-auto px-4 py-6">
        {children || <Outlet />}
      </main>

      <footer className="border-t border-gray-200 mt-12">
        <div className="max-w-lg mx-auto px-4 py-6 text-center text-sm text-gray-500">
          <nav className="flex justify-center gap-6 mb-3" aria-label="Footer">
            <Link to="/about" className="text-gray-500 hover:text-navy">
              About
            </Link>
            <Link to="/faq" className="text-gray-500 hover:text-navy">
              FAQ
            </Link>
          </nav>
          <p>Not affiliated with any political party</p>
        </div>
      </footer>
    </>
  );
}
