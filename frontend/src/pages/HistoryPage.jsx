import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Filter, ChevronDown, ChevronUp, ChevronLeft, ChevronRight, AlertOctagon, ClipboardList } from 'lucide-react';
import SeverityBadge from '../components/SeverityBadge';
import { useFetch } from '../hooks/useApi';
import { formatDate, getDamageDisplayName } from '../utils/formatters';

const SEVERITY_OPTIONS = ['All', 'Low', 'Medium', 'High', 'Critical'];
const RISK_OPTIONS = ['All', 'Low', 'Moderate', 'High', 'Critical'];

export default function HistoryPage() {
  const [page, setPage] = useState(1);
  const [severityFilter, setSeverityFilter] = useState('All');
  const [riskFilter, setRiskFilter] = useState('All');
  const [search, setSearch] = useState('');
  const [expandedRow, setExpandedRow] = useState(null);
  const PAGE_SIZE = 10;

  const params = new URLSearchParams({ skip: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE });
  if (severityFilter !== 'All') params.append('severity', severityFilter);
  if (riskFilter !== 'All') params.append('risk_level', riskFilter);

  const { data, loading, error, refetch } = useFetch(`/api/inspections/?${params}`);

  const inspections = data?.items || data || [];
  const total = data?.total || inspections.length;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const filtered = search
    ? inspections.filter(
        (ins) =>
          (ins.address || '').toLowerCase().includes(search.toLowerCase()) ||
          (ins.road_name || '').toLowerCase().includes(search.toLowerCase())
      )
    : inspections;

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="mx-auto max-w-7xl px-4 py-10">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-100">Inspection History</h1>
          <p className="mt-1 text-slate-400">Browse all past road damage inspections</p>
        </div>

        {/* Filters */}
        <div className="mb-6 flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search by road or address..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-800 py-2.5 pl-10 pr-4 text-sm text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-slate-400" />
            <select
              value={severityFilter}
              onChange={(e) => { setSeverityFilter(e.target.value); setPage(1); }}
              className="rounded-xl border border-slate-700 bg-slate-800 px-3 py-2.5 text-sm text-slate-200 focus:border-blue-500 focus:outline-none"
            >
              {SEVERITY_OPTIONS.map((o) => <option key={o} value={o}>{o === 'All' ? 'All Severities' : o}</option>)}
            </select>
            <select
              value={riskFilter}
              onChange={(e) => { setRiskFilter(e.target.value); setPage(1); }}
              className="rounded-xl border border-slate-700 bg-slate-800 px-3 py-2.5 text-sm text-slate-200 focus:border-blue-500 focus:outline-none"
            >
              {RISK_OPTIONS.map((o) => <option key={o} value={o}>{o === 'All' ? 'All Risk Levels' : o}</option>)}
            </select>
          </div>
        </div>

        {error && (
          <div className="mb-6 flex items-center gap-3 rounded-xl border border-yellow-500/40 bg-yellow-500/10 px-4 py-3 text-sm text-yellow-300">
            <AlertOctagon className="h-4 w-4" /> {error}
            <button onClick={refetch} className="ml-auto underline">Retry</button>
          </div>
        )}

        {loading && (
          <div className="rounded-xl border border-slate-700 bg-slate-800 overflow-hidden animate-pulse">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="border-b border-slate-700/50 px-5 py-4">
                <div className="h-4 w-48 rounded bg-slate-700" />
              </div>
            ))}
          </div>
        )}

        {!loading && filtered.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center py-24 text-center"
          >
            <ClipboardList className="mb-4 h-16 w-16 text-slate-600" />
            <h3 className="mb-2 text-xl font-semibold text-slate-300">No inspections found</h3>
            <p className="text-slate-500">Try adjusting filters or run a detection first.</p>
          </motion.div>
        )}

        {!loading && filtered.length > 0 && (
          <div className="rounded-xl border border-slate-700 bg-slate-800 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700 text-left text-xs uppercase tracking-wider text-slate-500">
                    <th className="px-4 py-3">#</th>
                    <th className="px-4 py-3">Date</th>
                    <th className="px-4 py-3">Road / Address</th>
                    <th className="px-4 py-3">Damage Types</th>
                    <th className="px-4 py-3">Count</th>
                    <th className="px-4 py-3">Severity</th>
                    <th className="px-4 py-3">Risk</th>
                    <th className="px-4 py-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((ins, i) => (
                    <>
                      <tr
                        key={ins.id || i}
                        onClick={() => setExpandedRow(expandedRow === i ? null : i)}
                        className="cursor-pointer border-b border-slate-700/50 hover:bg-slate-700/40 transition-colors"
                      >
                        <td className="px-4 py-3 text-slate-500">{(page - 1) * PAGE_SIZE + i + 1}</td>
                        <td className="px-4 py-3 text-slate-400 whitespace-nowrap">{formatDate(ins.timestamp)}</td>
                        <td className="px-4 py-3 text-slate-200">{ins.address || ins.road_name || '—'}</td>
                        <td className="px-4 py-3">
                          <div className="flex flex-wrap gap-1">
                            {(ins.damage_types || []).slice(0, 2).map((d) => (
                              <span key={d} className="rounded-full bg-slate-700 px-2 py-0.5 text-xs text-slate-300">
                                {getDamageDisplayName(d)}
                              </span>
                            ))}
                            {(ins.damage_types || []).length > 2 && (
                              <span className="text-xs text-slate-500">+{ins.damage_types.length - 2}</span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3 font-semibold text-blue-400">
                          {ins.damage_count ?? ins.detection_count ?? (ins.detections ? ins.detections.length : '—')}
                        </td>
                        <td className="px-4 py-3">
                          <SeverityBadge level={ins.severity?.level || ins.severity} />
                        </td>
                        <td className="px-4 py-3 text-slate-300">
                          {ins.risk_prediction?.level || ins.risk_level || '—'}
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-blue-400 hover:underline cursor-pointer">
                            {expandedRow === i ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                          </span>
                        </td>
                      </tr>
                      <AnimatePresence>
                        {expandedRow === i && (
                          <motion.tr
                            key={`exp-${i}`}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                          >
                            <td colSpan={8} className="bg-slate-900/50 px-6 py-4">
                              <div className="grid gap-4 sm:grid-cols-3 text-sm">
                                <div>
                                  <p className="text-xs text-slate-500 mb-1">Inspection ID</p>
                                  <p className="font-mono text-slate-300 text-xs">{ins.id || '—'}</p>
                                </div>
                                <div>
                                  <p className="text-xs text-slate-500 mb-1">All Damage Types</p>
                                  <p className="text-slate-300">{(ins.damage_types || []).map(getDamageDisplayName).join(', ') || '—'}</p>
                                </div>
                                <div>
                                  <p className="text-xs text-slate-500 mb-1">Repair Priority</p>
                                  <p className="text-slate-300">
                                    {ins.risk_prediction?.repair_priority || ins.repair_priority || '—'}
                                  </p>
                                </div>
                              </div>
                            </td>
                          </motion.tr>
                        )}
                      </AnimatePresence>
                    </>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between border-t border-slate-700 px-5 py-3">
              <p className="text-xs text-slate-400">
                Page {page} of {totalPages} · {total} total
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="flex items-center gap-1 rounded-lg border border-slate-600 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-700 transition-colors disabled:opacity-40"
                >
                  <ChevronLeft className="h-3.5 w-3.5" /> Prev
                </button>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="flex items-center gap-1 rounded-lg border border-slate-600 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-700 transition-colors disabled:opacity-40"
                >
                  Next <ChevronRight className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
