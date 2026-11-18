import { Link } from 'react-router-dom';
import { Github, MapPin } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-700 bg-slate-900 mt-auto">
      <div className="mx-auto max-w-7xl px-4 py-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">🛣️</span>
              <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent font-bold text-xl">
                RoadSense
              </span>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed">
              AI-Powered Road Damage Detection & Risk Prediction system built for smarter
              infrastructure maintenance.
            </p>
          </div>

          {/* Quick links */}
          <div>
            <h4 className="text-slate-200 font-semibold mb-3">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              {[
                { label: 'Home', path: '/' },
                { label: 'Detect Damage', path: '/detect' },
                { label: 'Dashboard', path: '/dashboard' },
                { label: 'Map View', path: '/map' },
                { label: 'Reports', path: '/reports' },
                { label: 'About', path: '/about' },
              ].map(({ label, path }) => (
                <li key={path}>
                  <Link
                    to={path}
                    className="text-slate-400 hover:text-blue-400 transition-colors"
                  >
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Tech credits */}
          <div>
            <h4 className="text-slate-200 font-semibold mb-3">Built With</h4>
            <div className="flex flex-wrap gap-2">
              {['React', 'FastAPI', 'PyTorch', 'MongoDB', 'Tailwind CSS', 'Leaflet', 'Recharts'].map(
                (tech) => (
                  <span
                    key={tech}
                    className="rounded-full bg-slate-800 border border-slate-700 px-2.5 py-0.5 text-xs text-slate-300"
                  >
                    {tech}
                  </span>
                )
              )}
            </div>
            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="mt-4 inline-flex items-center gap-2 text-sm text-slate-400 hover:text-slate-100 transition-colors"
            >
              <Github className="h-4 w-4" />
              View on GitHub
            </a>
          </div>
        </div>

        <div className="mt-8 border-t border-slate-800 pt-6 flex flex-col md:flex-row items-center justify-between gap-2 text-xs text-slate-500">
          <p>© 2024 RoadSense. University Project – CSE AIML</p>
          <p className="flex items-center gap-1">
            <MapPin className="h-3 w-3" /> Made with ❤️ for smarter roads
          </p>
        </div>
      </div>
    </footer>
  );
}
