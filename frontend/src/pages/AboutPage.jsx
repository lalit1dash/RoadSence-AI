import { motion } from 'framer-motion';
import { Github, ExternalLink, BookOpen, Brain, Shield, FileText, AlertTriangle } from 'lucide-react';

const TECH = [
  { emoji: '⚛️', name: 'React + Vite', purpose: 'Frontend SPA framework with fast build tooling' },
  { emoji: '🎨', name: 'Tailwind CSS', purpose: 'Utility-first CSS for rapid dark-theme UI' },
  { emoji: '🐍', name: 'FastAPI', purpose: 'High-performance async REST API backend' },
  { emoji: '🔥', name: 'PyTorch / YOLO', purpose: 'Deep learning model for damage detection' },
  { emoji: '🌳', name: 'Scikit-learn', purpose: 'Random Forest for risk/severity prediction' },
  { emoji: '🍃', name: 'MongoDB', purpose: 'NoSQL database for inspection records' },
  { emoji: '👁️', name: 'OpenCV', purpose: 'Image processing and annotation pipeline' },
  { emoji: '🗺️', name: 'Leaflet', purpose: 'Interactive geospatial map visualization' },
];

const ML_MODULES = [
  {
    id: 'A',
    icon: Brain,
    name: 'Module A — YOLO Detection',
    desc: 'YOLOv8 object detection model fine-tuned on road damage datasets. Identifies bounding boxes and classes for potholes, cracks, rutting, and more in real time.',
    color: 'text-blue-400',
    bg: 'bg-blue-500/10 border-blue-500/30',
  },
  {
    id: 'B',
    icon: AlertTriangle,
    name: 'Module B — Severity Classification',
    desc: 'Post-detection pipeline that aggregates detection confidence, count, bounding-box area, and damage type to assign Low / Medium / High / Critical severity.',
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/10 border-yellow-500/30',
  },
  {
    id: 'C',
    icon: Shield,
    name: 'Module C — Risk Prediction',
    desc: 'Random Forest classifier trained on road condition features to predict infrastructure risk level and generate repair priority recommendations.',
    color: 'text-orange-400',
    bg: 'bg-orange-500/10 border-orange-500/30',
  },
  {
    id: 'D',
    icon: FileText,
    name: 'Module D — Report Generation',
    desc: 'Automated report writer that synthesizes detection results, severity, and risk into human-readable PDF reports with executive summaries and actionable recommendations.',
    color: 'text-green-400',
    bg: 'bg-green-500/10 border-green-500/30',
  },
];

const ARCH_STEPS = [
  { label: 'User', node: 'Upload Image', color: 'bg-blue-600' },
  { label: 'API', node: 'FastAPI Backend', color: 'bg-purple-600' },
  { label: 'ML', node: 'YOLO + RF Models', color: 'bg-orange-600' },
  { label: 'DB', node: 'MongoDB', color: 'bg-green-600' },
  { label: 'UI', node: 'React Dashboard', color: 'bg-cyan-600' },
];

const container = { hidden: {}, show: { transition: { staggerChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="mx-auto max-w-5xl px-4 py-12 space-y-16">

        {/* Title */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center">
          <span className="mb-4 inline-block rounded-full bg-blue-500/20 border border-blue-500/40 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-blue-400">
            University Project · CSE AIML
          </span>
          <h1 className="mb-4 text-4xl font-extrabold">
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              🛣️ RoadSense
            </span>
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
            An AI-powered road damage detection and risk prediction system designed to help
            municipalities and infrastructure teams make data-driven maintenance decisions.
          </p>
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className="mt-6 inline-flex items-center gap-2 rounded-xl border border-slate-600 bg-slate-800 px-5 py-2.5 text-sm text-slate-200 hover:border-blue-500/50 hover:bg-slate-700 transition-colors"
          >
            <Github className="h-4 w-4" /> View on GitHub <ExternalLink className="h-3 w-3" />
          </a>
        </motion.div>

        {/* Objectives */}
        <section>
          <h2 className="mb-6 text-2xl font-bold text-slate-100">Project Objectives</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              'Automate road damage detection using computer vision (YOLO)',
              'Classify damage severity using ML classification pipeline',
              'Predict infrastructure risk with Random Forest model',
              'Provide geospatial visualization of damage hotspots',
              'Generate actionable AI reports for maintenance teams',
              'Build a scalable, real-time web platform for field engineers',
            ].map((obj, i) => (
              <div
                key={i}
                className="flex items-start gap-3 rounded-xl border border-slate-700 bg-slate-800 p-4"
              >
                <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-500/20 text-xs font-bold text-blue-400">
                  {i + 1}
                </span>
                <p className="text-sm text-slate-300 leading-relaxed">{obj}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ML Modules */}
        <section>
          <h2 className="mb-6 text-2xl font-bold text-slate-100">ML Pipeline Modules</h2>
          <motion.div
            variants={container}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            className="grid gap-5 sm:grid-cols-2"
          >
            {ML_MODULES.map(({ id, icon: Icon, name, desc, color, bg }) => (
              <motion.div
                key={id}
                variants={item}
                className={`rounded-xl border p-5 ${bg}`}
              >
                <div className="mb-3 flex items-center gap-3">
                  <div className={`rounded-xl bg-slate-900/50 p-2`}>
                    <Icon className={`h-5 w-5 ${color}`} />
                  </div>
                  <h3 className="font-semibold text-slate-200">{name}</h3>
                </div>
                <p className="text-sm leading-relaxed text-slate-400">{desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* Architecture */}
        <section>
          <h2 className="mb-6 text-2xl font-bold text-slate-100">System Architecture</h2>
          <div className="rounded-xl border border-slate-700 bg-slate-800 p-6">
            <div className="flex flex-col sm:flex-row items-center justify-center gap-2">
              {ARCH_STEPS.map(({ label, node, color }, i) => (
                <>
                  <div key={node} className="flex flex-col items-center gap-1">
                    <span className="text-xs text-slate-500">{label}</span>
                    <span className={`rounded-xl px-4 py-2 text-sm font-semibold text-white ${color}`}>
                      {node}
                    </span>
                  </div>
                  {i < ARCH_STEPS.length - 1 && (
                    <span key={`arrow-${i}`} className="text-slate-500 text-xl sm:block hidden">→</span>
                  )}
                  {i < ARCH_STEPS.length - 1 && (
                    <span key={`arrow-m-${i}`} className="text-slate-500 text-xl sm:hidden">↓</span>
                  )}
                </>
              ))}
            </div>
            <p className="mt-6 text-center text-xs text-slate-500">
              Images flow from the React frontend → FastAPI REST API → ML pipeline (YOLO + Random Forest) → MongoDB storage → Dashboard & reports
            </p>
          </div>
        </section>

        {/* Tech Stack */}
        <section>
          <h2 className="mb-6 text-2xl font-bold text-slate-100">Technology Stack</h2>
          <motion.div
            variants={container}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
          >
            {TECH.map(({ emoji, name, purpose }) => (
              <motion.div
                key={name}
                variants={item}
                whileHover={{ scale: 1.03 }}
                className="rounded-xl border border-slate-700 bg-slate-800 p-4"
              >
                <div className="mb-2 text-3xl">{emoji}</div>
                <h3 className="mb-1 font-semibold text-slate-200">{name}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{purpose}</p>
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* Team */}
        <section>
          <h2 className="mb-6 text-2xl font-bold text-slate-100">Team</h2>
          <div className="rounded-xl border border-slate-700 bg-slate-800 p-6 text-center">
            <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-blue-500/20 text-4xl">
              👤
            </div>
            <h3 className="text-lg font-semibold text-slate-200">Student Developer</h3>
            <p className="text-sm text-slate-400">CSE (Artificial Intelligence & Machine Learning)</p>
            <p className="mt-1 text-sm text-slate-500">University Project · 2024</p>
          </div>
        </section>

        {/* Demo Mode notice */}
        <section>
          <div className="rounded-xl border border-yellow-500/40 bg-yellow-500/10 p-5">
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-yellow-400" />
              <div>
                <h3 className="mb-1 font-semibold text-yellow-300">Demo Mode</h3>
                <p className="text-sm leading-relaxed text-yellow-200/80">
                  This application runs in demo mode when real ML model weights are not loaded.
                  All detections, severity scores, and risk predictions are simulated using
                  realistic random data to demonstrate the full UI and API pipeline. Load actual
                  YOLO/RF model weights in <code className="text-xs bg-yellow-500/20 rounded px-1">backend/ml/weights/</code> to enable real inference.
                </p>
              </div>
            </div>
          </div>
        </section>

      </div>
    </div>
  );
}
