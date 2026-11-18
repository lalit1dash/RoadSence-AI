import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Download, ChevronDown, ChevronUp, AlertOctagon, RefreshCw, FileSearch } from 'lucide-react';
import SeverityBadge from '../components/SeverityBadge';
import { useFetch } from '../hooks/useApi';
import { formatDate } from '../utils/formatters';
import api from '../config/api';

const SECTION_STYLES = {
  executive_summary: 'border-blue-500/40 bg-blue-500/10',
  damage_analysis: 'border-orange-500/40 bg-orange-500/10',
  severity_assessment: 'border-yellow-500/40 bg-yellow-500/10',
  risk_assessment: 'border-red-500/40 bg-red-500/10',
  recommendations: 'border-green-500/40 bg-green-500/10',
  safety_warnings: 'border-red-500/40 bg-red-500/10',
};

const SECTIONS = [
  { key: 'executive_summary', label: '📋 Executive Summary' },
  { key: 'damage_analysis', label: '🔍 Damage Analysis' },
  { key: 'severity_assessment', label: '⚠️ Severity Assessment' },
  { key: 'risk_assessment', label: '🚨 Risk Assessment' },
  { key: 'recommendations', label: '🔧 Recommendations' },
  { key: 'safety_warnings', label: '🛡️ Safety Warnings' },
];

function ReportCard({ report }) {
  const [expanded, setExpanded] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const res = await api.get(`/api/reports/${report.id}/pdf`, { responseType: 'blob' });
      const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `report-${report.id}.pdf`;
      a.click();
    } catch (e) {
      // Fallback text download if backend PDF route is unavailable
      const summaryText = `RoadSense Inspection Report\nID: ${report.id}\nDetection: ${report.detection_id}\nDate: ${report.generated_at}\n\nExecutive Summary:\n${report.executive_summary || ''}\n\nDamage Analysis:\n${report.damage_analysis || ''}\n\nSeverity Assessment:\n${report.severity_assessment || ''}\n\nRisk Assessment:\n${report.risk_assessment || ''}\n\nRecommendations:\n${report.recommendations || ''}\n\nSafety Warnings:\n${report.safety_warnings || ''}`;
      const blob = new Blob([summaryText], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report-${report.id}.txt`;
      a.click();
    } finally {
      setDownloading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-slate-700 bg-slate-800 overflow-hidden"
    >
      {/* Card Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-5 py-4">
        <div className="flex items-start gap-3">
          <div className="rounded-lg bg-blue-500/20 p-2">
            <FileText className="h-5 w-5 text-blue-400" />
          </div>
          <div>
            <p className="font-semibold text-slate-200">Report #{report.id?.slice(-8) || report.id}</p>
            <p className="text-xs text-slate-400">Inspection: {report.detection_id}</p>
            <p className="text-xs text-slate-500 mt-0.5">{formatDate(report.generated_at)}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {report.severity && <SeverityBadge level={report.severity} />}
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="flex items-center gap-1.5 rounded-lg border border-slate-600 bg-slate-700 px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-600 transition-colors disabled:opacity-50"
          >
            <Download className="h-3.5 w-3.5" />
            {downloading ? 'Downloading...' : 'PDF'}
          </button>
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 rounded-lg border border-slate-600 bg-slate-700 px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-600 transition-colors"
          >
            {expanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
            {expanded ? 'Collapse' : 'View'}
          </button>
        </div>
      </div>

      {/* Preview */}
      {report.executive_summary && !expanded && (
        <div className="border-t border-slate-700/50 px-5 py-3">
          <p className="text-sm text-slate-400 line-clamp-2">{report.executive_summary}</p>
        </div>
      )}

      {/* Full Expanded Report */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden border-t border-slate-700"
          >
            <div className="p-5 space-y-4">
              {SECTIONS.map(({ key, label }) =>
                report[key] ? (
                  <div
                    key={key}
                    className={`rounded-xl border p-4 ${SECTION_STYLES[key] || 'border-slate-600 bg-slate-700/40'}`}
                  >
                    <h4 className="mb-2 text-sm font-semibold text-slate-200">{label}</h4>
                    <div className="text-sm leading-relaxed text-slate-300 whitespace-pre-line">
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
                          <pre className="text-xs bg-slate-900/60 p-3 rounded overflow-x-auto font-mono text-slate-400">
                            {JSON.stringify(report[key], null, 2)}
                          </pre>
                        )
                      ) : (
                        <p>{String(report[key])}</p>
                      )}
                    </div>
                  </div>
                ) : null
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function ReportsPage() {
  const { data, loading, error, refetch } = useFetch('/api/reports/');
  const items = data?.items || (Array.isArray(data) ? data : []);
  const reports = items;

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="mx-auto max-w-5xl px-4 py-10">
        {/* Header */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-100">AI Reports</h1>
            <p className="mt-1 text-slate-400">Auto-generated inspection reports</p>
          </div>
          <button
            onClick={refetch}
            disabled={loading}
            className="flex items-center gap-2 rounded-xl border border-slate-600 bg-slate-800 px-4 py-2 text-sm text-slate-200 hover:bg-slate-700 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {error && (
          <div className="mb-6 flex items-center gap-3 rounded-xl border border-yellow-500/40 bg-yellow-500/10 px-4 py-3 text-sm text-yellow-300">
            <AlertOctagon className="h-4 w-4" />
            {error}
            <button onClick={refetch} className="ml-auto underline">Retry</button>
          </div>
        )}

        {loading && (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 rounded-xl bg-slate-800 animate-pulse" />
            ))}
          </div>
        )}

        {!loading && reports.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center py-24 text-center"
          >
            <FileSearch className="mb-4 h-16 w-16 text-slate-600" />
            <h3 className="mb-2 text-xl font-semibold text-slate-300">No reports yet</h3>
            <p className="text-slate-500">Run a detection first to auto-generate reports.</p>
          </motion.div>
        )}

        {!loading && reports.length > 0 && (
          <div className="space-y-4">
            {reports.map((r) => (
              <ReportCard key={r.id} report={r} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
