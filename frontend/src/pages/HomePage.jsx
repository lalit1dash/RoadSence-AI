import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Search,
  BarChart2,
  AlertTriangle,
  Map,
  FileText,
  Wrench,
  ArrowRight,
  Upload,
  Brain,
  ClipboardList,
} from 'lucide-react';

const FEATURES = [
  {
    icon: Search,
    title: 'Smart Detection',
    desc: 'YOLO-based real-time detection of 5 road damage types including potholes, cracks, and rutting.',
    color: 'text-blue-400',
    bg: 'bg-blue-500/10',
  },
  {
    icon: BarChart2,
    title: 'Severity Analysis',
    desc: 'ML classification pipeline assigns Low / Medium / High / Critical severity scores instantly.',
    color: 'text-purple-400',
    bg: 'bg-purple-500/10',
  },
  {
    icon: AlertTriangle,
    title: 'Risk Prediction',
    desc: 'Random Forest model predicts infrastructure risk and urgency based on damage patterns.',
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
  },
  {
    icon: Map,
    title: 'Interactive Map',
    desc: 'Leaflet-powered geospatial view of all inspections colour-coded by severity.',
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10',
  },
  {
    icon: FileText,
    title: 'AI Reports',
    desc: 'Auto-generated PDF reports with executive summaries, findings, and actionable insights.',
    color: 'text-green-400',
    bg: 'bg-green-500/10',
  },
  {
    icon: Wrench,
    title: 'Repair Priority',
    desc: 'Smart recommendations ranking repair urgency to help allocate maintenance budgets.',
    color: 'text-red-400',
    bg: 'bg-red-500/10',
  },
];

const STEPS = [
  { num: 1, icon: Upload, label: 'Upload Road Image', desc: 'JPEG or PNG from any camera/drone' },
  { num: 2, icon: Search, label: 'AI Detection (YOLO)', desc: 'Locates and classifies damage types' },
  { num: 3, icon: Brain, label: 'Risk Analysis (ML)', desc: 'Severity & risk score computed' },
  { num: 4, icon: ClipboardList, label: 'Get Report', desc: 'PDF report with recommendations' },
];

const STATS = [
  { value: '500+', label: 'Roads Analyzed' },
  { value: '95%', label: 'Detection Accuracy (Demo)' },
  { value: '5', label: 'Damage Types' },
  { value: 'Real-time', label: 'Analysis Speed' },
];

const TECH = ['⚛️ React', '🐍 FastAPI', '🔥 PyTorch', '🍃 MongoDB', '👁️ OpenCV'];

const container = { hidden: {}, show: { transition: { staggerChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0 } };

export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      {/* ── Hero ── */}
      <section className="relative overflow-hidden px-4 py-28 text-center">
        {/* Animated gradient blobs */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <motion.div
            animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
            transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
            className="absolute -top-32 -left-32 h-96 w-96 rounded-full bg-blue-600/20 blur-3xl"
          />
          <motion.div
            animate={{ scale: [1, 1.15, 1], opacity: [0.2, 0.4, 0.2] }}
            transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
            className="absolute -bottom-32 -right-32 h-96 w-96 rounded-full bg-cyan-600/20 blur-3xl"
          />
          {/* Subtle grid */}
          <div
            className="absolute inset-0 opacity-[0.03]"
            style={{
              backgroundImage:
                'linear-gradient(rgba(255,255,255,1) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,1) 1px,transparent 1px)',
              backgroundSize: '48px 48px',
            }}
          />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="relative z-10 mx-auto max-w-4xl"
        >
          <span className="mb-4 inline-block rounded-full bg-blue-500/20 border border-blue-500/40 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-blue-400">
            University Project · CSE AIML
          </span>
          <h1 className="mb-6 text-5xl font-extrabold leading-tight md:text-7xl">
            <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-300 bg-clip-text text-transparent">
              AI-Powered
            </span>
            <br />
            Road Damage Detection
          </h1>
          <p className="mx-auto mb-10 max-w-2xl text-lg text-slate-400 leading-relaxed">
            Upload any road image and get instant YOLO-based damage detection, severity
            classification, risk prediction, and repair recommendations — all in seconds.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              to="/detect"
              className="flex items-center gap-2 rounded-xl bg-blue-600 px-7 py-3.5 font-semibold text-white shadow-lg shadow-blue-600/30 hover:bg-blue-500 transition-colors"
            >
              Start Detection <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/dashboard"
              className="flex items-center gap-2 rounded-xl border border-slate-600 bg-slate-800 px-7 py-3.5 font-semibold text-slate-200 hover:border-slate-500 hover:bg-slate-700 transition-colors"
            >
              View Dashboard <BarChart2 className="h-4 w-4" />
            </Link>
          </div>
        </motion.div>
      </section>

      {/* ── Stats Banner ── */}
      <section className="border-y border-slate-700 bg-slate-800/60 px-4 py-10">
        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          className="mx-auto grid max-w-5xl grid-cols-2 gap-6 md:grid-cols-4"
        >
          {STATS.map((s) => (
            <motion.div key={s.label} variants={item} className="text-center">
              <p className="text-3xl font-extrabold text-blue-400">{s.value}</p>
              <p className="mt-1 text-sm text-slate-400">{s.label}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* ── Features ── */}
      <section className="px-4 py-20">
        <div className="mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-12 text-center"
          >
            <h2 className="text-3xl font-bold text-slate-100 md:text-4xl">Powerful Features</h2>
            <p className="mt-3 text-slate-400">Everything you need for road infrastructure analysis</p>
          </motion.div>
          <motion.div
            variants={container}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3"
          >
            {FEATURES.map(({ icon: Icon, title, desc, color, bg }) => (
              <motion.div
                key={title}
                variants={item}
                whileHover={{ scale: 1.03, y: -4 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                className="rounded-xl border border-slate-700 bg-slate-800 p-6 shadow-lg"
              >
                <div className={`mb-4 inline-flex rounded-xl p-3 ${bg}`}>
                  <Icon className={`h-6 w-6 ${color}`} />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-slate-100">{title}</h3>
                <p className="text-sm leading-relaxed text-slate-400">{desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section className="bg-slate-800/40 px-4 py-20 border-y border-slate-700">
        <div className="mx-auto max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-12 text-center"
          >
            <h2 className="text-3xl font-bold text-slate-100 md:text-4xl">How It Works</h2>
            <p className="mt-3 text-slate-400">Four simple steps from photo to insight</p>
          </motion.div>
          <div className="relative grid gap-6 md:grid-cols-4">
            {/* connector line */}
            <div className="absolute top-8 left-0 right-0 hidden md:block h-px bg-gradient-to-r from-transparent via-blue-500/40 to-transparent mx-16" />
            {STEPS.map(({ num, icon: Icon, label, desc }, i) => (
              <motion.div
                key={num}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                className="relative flex flex-col items-center text-center"
              >
                <div className="relative mb-4 flex h-16 w-16 items-center justify-center rounded-full border-2 border-blue-500/60 bg-slate-800 shadow-lg shadow-blue-500/20">
                  <Icon className="h-7 w-7 text-blue-400" />
                  <span className="absolute -top-2 -right-2 flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">
                    {num}
                  </span>
                </div>
                <h3 className="mb-1 font-semibold text-slate-100">{label}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Tech Stack ── */}
      <section className="px-4 py-20">
        <div className="mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="mb-3 text-3xl font-bold text-slate-100">Technology Stack</h2>
            <p className="mb-10 text-slate-400">Built on industry-proven open-source tools</p>
            <div className="flex flex-wrap justify-center gap-4">
              {TECH.map((t) => (
                <span
                  key={t}
                  className="rounded-xl border border-slate-700 bg-slate-800 px-5 py-3 text-sm font-medium text-slate-200 shadow hover:border-blue-500/50 transition-colors"
                >
                  {t}
                </span>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="px-4 pb-20">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mx-auto max-w-2xl rounded-2xl border border-blue-500/30 bg-gradient-to-br from-blue-600/20 to-cyan-600/10 p-10 text-center shadow-xl"
        >
          <h2 className="mb-3 text-2xl font-bold text-slate-100">Ready to Detect Road Damage?</h2>
          <p className="mb-8 text-slate-400">
            Upload a road image now and see our AI pipeline in action.
          </p>
          <Link
            to="/detect"
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-8 py-3.5 font-semibold text-white shadow-lg shadow-blue-600/30 hover:bg-blue-500 transition-colors"
          >
            Start Detection <ArrowRight className="h-4 w-4" />
          </Link>
        </motion.div>
      </section>
    </div>
  );
}
