import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  FileImage,
  MapPin,
  Navigation,
  X,
  FileText,
  ChevronDown,
  ChevronUp,
  AlertOctagon,
} from 'lucide-react';
import DemoModeAlert from '../components/DemoModeAlert';
import SeverityBadge from '../components/SeverityBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { usePost } from '../hooks/useApi';
import api from '../config/api';
import { formatConfidence, getDamageDisplayName } from '../utils/formatters';

const SEVERITY_BAR_COLOR = { Low: 'bg-green-500', Medium: 'bg-yellow-500', High: 'bg-orange-500', Critical: 'bg-red-500' };

const SAMPLE_ROADS = [
  { name: 'Severe Pothole (NH-48)', file: 'pothole_severe_nh48.jpg', type: 'Pothole', location: { latitude: '28.4595', longitude: '77.0266', address: 'NH-48 Expressway', road_name: 'NH-48' } },
  { name: 'Alligator Cracks', file: 'alligator_crack_urban.jpg', type: 'Alligator Crack', location: { latitude: '12.9716', longitude: '77.5946', address: 'MG Road Junction', road_name: 'MG Road' } },
  { name: 'Longitudinal Fault', file: 'longitudinal_crack_highway.jpg', type: 'Longitudinal Crack', location: { latitude: '19.0760', longitude: '72.8777', address: 'Western Express Highway', road_name: 'WEH' } },
  { name: 'Transverse Crack', file: 'transverse_crack_suburb.jpg', type: 'Transverse Crack', location: { latitude: '13.0827', longitude: '80.2707', address: 'Anna Salai', road_name: 'Mount Road' } },
  { name: 'Surface Raveling', file: 'surface_damage_multi.jpg', type: 'Surface Damage', location: { latitude: '17.3850', longitude: '78.4867', address: 'Banjara Hills Rd 12', road_name: 'Road 12' } },
  { name: 'Critical Road Failure', file: 'heavy_damage_sector14.jpg', type: 'Multiple Critical', location: { latitude: '28.6139', longitude: '77.2090', address: 'Ring Road Sector 14', road_name: 'Ring Road' } },
];

export default function DetectPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [location, setLocation] = useState({ latitude: '', longitude: '', address: '', road_name: '' });
  const [results, setResults] = useState(null);
  const [report, setReport] = useState(null);
  const [openSection, setOpenSection] = useState(null);
  const [generating, setGenerating] = useState(false);
  const fileRef = useRef();
  const { mutate, loading, error } = usePost();

  const pickFile = useCallback((f) => {
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResults(null);
    setReport(null);
  }, []);

  const loadSampleImage = async (sample) => {
    try {
      const response = await fetch(`/sample_roads/${sample.file}`);
      const blob = await response.blob();
      const sampleFile = new File([blob], sample.file, { type: 'image/jpeg' });
      pickFile(sampleFile);
      if (sample.location) {
        setLocation(sample.location);
      }
    } catch (err) {
      console.error('Failed to load sample broken road image:', err);
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    pickFile(e.dataTransfer.files[0]);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    if (location.latitude) fd.append('latitude', location.latitude);
    if (location.longitude) fd.append('longitude', location.longitude);
    if (location.address) fd.append('address', location.address);
    if (location.road_name) fd.append('road_name', location.road_name);
    try {
      const data = await mutate('/api/detection/analyze', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResults(data);
    } catch (_) {}
  };

  const handleGenerateReport = async () => {
    if (!results?.id) return;
    setGenerating(true);
    try {
      const res = await api.post(`/api/reports/generate/${results.id}`);
      setReport(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setGenerating(false);
    }
  };

  const toggleSection = (s) => setOpenSection(openSection === s ? null : s);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="mx-auto max-w-6xl px-4 py-10">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <h1 className="mb-1 text-3xl font-bold text-slate-100">Road Damage Detection</h1>
          <p className="mb-8 text-slate-400">Upload a road image for AI-powered analysis</p>
        </motion.div>

        <DemoModeAlert />

        {/* Upload Zone */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mt-6 rounded-xl border border-slate-700 bg-slate-800 p-6"
        >
          <h2 className="mb-4 font-semibold text-slate-200">Upload Road Image</h2>

          {!preview ? (
            <div
              onDrop={onDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => fileRef.current?.click()}
              className="cursor-pointer rounded-xl border-2 border-dashed border-slate-600 hover:border-blue-500/60 transition-colors bg-slate-900/50 p-12 text-center"
            >
              <FileImage className="mx-auto mb-4 h-12 w-12 text-slate-500" />
              <p className="text-slate-300 font-medium">Drop image here or click to browse</p>
              <p className="mt-1 text-sm text-slate-500">JPEG, PNG up to 10 MB</p>
              <input
                ref={fileRef}
                type="file"
                accept="image/jpeg,image/png"
                className="hidden"
                onChange={(e) => pickFile(e.target.files[0])}
              />
            </div>
          ) : (
            <div className="relative rounded-xl overflow-hidden">
              <img src={preview} alt="preview" className="max-h-80 w-full object-contain bg-black rounded-xl" />
              <button
                onClick={() => { setFile(null); setPreview(null); setResults(null); setReport(null); }}
                className="absolute top-3 right-3 rounded-full bg-slate-900/80 p-1.5 text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          {/* Quick Sample Selector */}
          <div className="mt-5 border-t border-slate-700/60 pt-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center justify-between">
              <span>📸 Or Try Sample Broken Road Files</span>
              <span className="text-[10px] text-slate-500 font-normal">Click to load image + GPS coordinates</span>
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
              {SAMPLE_ROADS.map((sample) => (
                <button
                  key={sample.file}
                  type="button"
                  onClick={() => loadSampleImage(sample)}
                  className="group relative flex flex-col rounded-xl border border-slate-700 bg-slate-900/60 p-1.5 text-left hover:border-blue-500/80 hover:bg-slate-900 transition-all shadow-sm hover:shadow-md"
                >
                  <img
                    src={`/sample_roads/${sample.file}`}
                    alt={sample.name}
                    className="h-14 w-full rounded-lg object-cover mb-1.5 bg-black/60 border border-slate-800"
                  />
                  <span className="text-[11px] font-medium text-slate-200 group-hover:text-blue-400 line-clamp-1">
                    {sample.name}
                  </span>
                  <span className="text-[9px] text-slate-500 line-clamp-1">
                    {sample.type}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Optional location fields */}
          <details className="mt-5">
            <summary className="cursor-pointer text-sm text-slate-400 hover:text-slate-200 flex items-center gap-2 select-none">
              <MapPin className="h-4 w-4" /> Optional location info
            </summary>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              {[
                { key: 'latitude', label: 'Latitude', placeholder: '12.9716', icon: Navigation },
                { key: 'longitude', label: 'Longitude', placeholder: '77.5946', icon: Navigation },
                { key: 'address', label: 'Address', placeholder: 'MG Road, Bangalore' },
                { key: 'road_name', label: 'Road Name', placeholder: 'NH-48' },
              ].map(({ key, label, placeholder, icon: Icon }) => (
                <div key={key}>
                  <label className="mb-1 block text-xs text-slate-400">{label}</label>
                  <input
                    type="text"
                    placeholder={placeholder}
                    value={location[key]}
                    onChange={(e) => setLocation((l) => ({ ...l, [key]: e.target.value }))}
                    className="w-full rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:border-blue-500 focus:outline-none"
                  />
                </div>
              ))}
            </div>
          </details>

          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 py-3 font-semibold text-white shadow-lg shadow-blue-600/30 hover:bg-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Analyzing...
              </span>
            ) : (
              <>
                <Upload className="h-4 w-4" /> Analyze Road
              </>
            )}
          </button>

          {error && (
            <div className="mt-4 flex items-center gap-2 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-400">
              <AlertOctagon className="h-4 w-4 shrink-0" />
              {error}
            </div>
          )}
        </motion.div>

        {/* Loading */}
        {loading && (
          <div className="mt-8">
            <LoadingSpinner text="Running AI analysis" />
          </div>
        )}

        {/* Results Panel */}
        <AnimatePresence>
          {results && !loading && (
            <motion.div
              initial={{ opacity: 0, y: 32 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
              className="mt-8 space-y-6"
            >
              {/* Images side by side */}
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-xl border border-slate-700 bg-slate-800 p-4">
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">Original</p>
                  <img src={preview} alt="original" className="rounded-lg w-full object-contain max-h-64 bg-black" />
                </div>
                {(results.annotated_image || results.annotated_image_base64) ? (
                  <div className="rounded-xl border border-slate-700 bg-slate-800 p-4">
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">Annotated</p>
                    <img
                      src={`data:image/jpeg;base64,${results.annotated_image || results.annotated_image_base64}`}
                      alt="annotated"
                      className="rounded-lg w-full object-contain max-h-64 bg-black"
                    />
                  </div>
                ) : null}
              </div>

              {/* Detection Summary */}
              <div className="rounded-xl border border-slate-700 bg-slate-800 p-6">
                <h3 className="mb-5 font-semibold text-slate-200">Detection Summary</h3>
                <div className="mb-6 text-center">
                  <span className="text-6xl font-extrabold text-blue-400">
                    {results.total_detections ?? results.detection_count ?? results.detections?.length ?? 0}
                  </span>
                  <p className="text-sm text-slate-400 mt-1">Total Detections</p>
                </div>
                {results.detections?.length > 0 && (
                  <div className="space-y-3">
                    {results.detections.map((d, i) => (
                      <div key={i}>
                        <div className="mb-1 flex items-center justify-between text-sm">
                          <span className="text-slate-200">{getDamageDisplayName(d.class_name)}</span>
                          <span className="text-slate-400">{formatConfidence(d.confidence)}</span>
                        </div>
                        <div className="h-2 w-full overflow-hidden rounded-full bg-slate-700">
                          <div
                            className="h-2 rounded-full bg-blue-500"
                            style={{ width: `${(d.confidence * 100).toFixed(0)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Severity */}
              {results.severity && (
                <div className="rounded-xl border border-slate-700 bg-slate-800 p-6">
                  <h3 className="mb-4 font-semibold text-slate-200">Severity Assessment</h3>
                  <div className="flex items-center gap-4 mb-4">
                    <SeverityBadge level={results.severity.level} />
                    <span className="text-slate-400 text-sm">Score: {(results.severity.score * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-3 w-full overflow-hidden rounded-full bg-slate-700">
                    <div
                      className={`h-3 rounded-full transition-all ${SEVERITY_BAR_COLOR[results.severity.level] || 'bg-blue-500'}`}
                      style={{ width: `${(results.severity.score * 100).toFixed(0)}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Risk Assessment */}
              {(results.risk || results.risk_prediction) && (
                <div className="rounded-xl border border-slate-700 bg-slate-800 p-6">
                  <h3 className="mb-4 font-semibold text-slate-200">Risk Assessment</h3>
                  {(() => {
                    const r = results.risk || results.risk_prediction;
                    return (
                      <>
                        <div className="flex items-center gap-3 mb-3">
                          <span className="text-lg font-bold text-orange-400">{r.level}</span>
                          <span className="text-sm text-slate-400">Score: {(r.score * 100).toFixed(0)}%</span>
                        </div>
                        {r.factors?.length > 0 && (
                          <ul className="space-y-1">
                            {r.factors.map((f, i) => (
                              <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-orange-400" />
                                {f}
                              </li>
                            ))}
                          </ul>
                        )}
                      </>
                    );
                  })()}
                </div>
              )}

              {/* Repair Priority */}
              {(results.risk || results.risk_prediction) && (
                <div className="rounded-xl border border-slate-700 bg-slate-800 p-6">
                  <h3 className="mb-4 font-semibold text-slate-200">Repair Priority</h3>
                  {(() => {
                    const r = results.risk || results.risk_prediction;
                    return (
                      <div className="grid gap-4 sm:grid-cols-2">
                        <div>
                          <p className="text-xs text-slate-400 mb-1">Priority Level</p>
                          <p className="text-lg font-bold text-amber-400">{r.repair_priority || '—'}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-400 mb-1">Est. Repair Time</p>
                          <p className="text-lg font-bold text-slate-200">{r.estimated_repair_time || '—'}</p>
                        </div>
                      </div>
                    );
                  })()}
                </div>
              )}

              {/* Generate Report */}
              <div className="flex justify-center">
                <button
                  onClick={handleGenerateReport}
                  disabled={generating || !results?.id}
                  className="flex items-center gap-2 rounded-xl bg-green-600 px-8 py-3 font-semibold text-white shadow-lg shadow-green-600/30 hover:bg-green-500 transition-colors disabled:opacity-50"
                >
                  <FileText className="h-4 w-4" />
                  {generating ? 'Generating...' : 'Generate Report'}
                </button>
              </div>

              {/* Report accordion */}
              {report && (
                <div className="rounded-xl border border-slate-700 bg-slate-800 overflow-hidden">
                  <div className="border-b border-slate-700 px-6 py-4">
                    <h3 className="font-semibold text-slate-200">AI-Generated Report</h3>
                  </div>
                  {[
                    { key: 'executive_summary', label: '📋 Executive Summary' },
                    { key: 'damage_analysis', label: '🔍 Damage Analysis' },
                    { key: 'severity_assessment', label: '⚠️ Severity Assessment' },
                    { key: 'risk_assessment', label: '🚨 Risk Assessment' },
                    { key: 'recommendations', label: '🔧 Recommendations' },
                    { key: 'safety_warnings', label: '🛡️ Safety Warnings' },
                  ].map(({ key, label }) =>
                    report[key] ? (
                      <div key={key} className="border-b border-slate-700/50 last:border-0">
                        <button
                          onClick={() => toggleSection(key)}
                          className="flex w-full items-center justify-between px-6 py-4 text-left text-sm font-medium text-slate-200 hover:bg-slate-700/40 transition-colors"
                        >
                          {label}
                          {openSection === key ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
                        </button>
                        <AnimatePresence>
                          {openSection === key && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              transition={{ duration: 0.2 }}
                              className="overflow-hidden"
                            >
                              <div className="px-6 pb-4 text-sm leading-relaxed text-slate-300">
                                {typeof report[key] === 'string' ? (
                                  <p>{report[key]}</p>
                                ) : Array.isArray(report[key]) ? (
                                  <ul className="list-disc pl-5 space-y-1">
                                    {report[key].map((item, idx) => (
                                      <li key={idx}>{item}</li>
                                    ))}
                                  </ul>
                                ) : typeof report[key] === 'object' && report[key] !== null ? (
                                  report[key].explanation ? (
                                    <p>{report[key].explanation}</p>
                                  ) : (
                                    <pre className="text-xs bg-slate-900 p-3 rounded overflow-x-auto font-mono text-slate-400">
                                      {JSON.stringify(report[key], null, 2)}
                                    </pre>
                                  )
                                ) : (
                                  <p>{String(report[key])}</p>
                                )}
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    ) : null
                  )}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
