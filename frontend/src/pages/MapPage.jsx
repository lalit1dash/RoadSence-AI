import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { Link } from 'react-router-dom';
import { Filter, Layers, Info, X } from 'lucide-react';
import SeverityBadge from '../components/SeverityBadge';
import { useFetch } from '../hooks/useApi';
import { formatDate } from '../utils/formatters';
import 'leaflet/dist/leaflet.css';

const SEV_COLORS = { Low: '#22c55e', Medium: '#eab308', High: '#f97316', Critical: '#ef4444' };

const ALL_SEVERITIES = ['Low', 'Medium', 'High', 'Critical'];
const ALL_RISKS = ['Low', 'Moderate', 'High', 'Critical'];

export default function MapPage() {
  const { data, loading, error } = useFetch('/api/dashboard/map-data');
  const markers = Array.isArray(data) ? data : [];

  const [sevFilter, setSevFilter] = useState(new Set(ALL_SEVERITIES));
  const [riskFilter, setRiskFilter] = useState(new Set(ALL_RISKS));
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const toggleSev = (s) =>
    setSevFilter((prev) => {
      const n = new Set(prev);
      n.has(s) ? n.delete(s) : n.add(s);
      return n;
    });

  const toggleRisk = (r) =>
    setRiskFilter((prev) => {
      const n = new Set(prev);
      n.has(r) ? n.delete(r) : n.add(r);
      return n;
    });

  const visible = markers.filter(
    (m) =>
      (m.latitude ?? m.lat) != null &&
      (m.longitude ?? m.lng) != null &&
      sevFilter.has(m.severity) &&
      riskFilter.has(m.risk_level)
  );

  return (
    <div className="flex" style={{ height: 'calc(100vh - 64px)' }}>
      {/* Sidebar */}
      <motion.aside
        initial={{ x: 0 }}
        animate={{ x: sidebarOpen ? 0 : -300 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className="relative z-10 w-72 shrink-0 border-r border-slate-700 bg-slate-900 overflow-y-auto"
      >
        <div className="flex items-center justify-between border-b border-slate-700 px-4 py-3">
          <h2 className="flex items-center gap-2 font-semibold text-slate-200">
            <Filter className="h-4 w-4 text-blue-400" /> Filters
          </h2>
          <button onClick={() => setSidebarOpen(false)} className="text-slate-400 hover:text-slate-100 transition-colors">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="p-4 space-y-5">
          {/* Count */}
          <div className="rounded-xl border border-slate-700 bg-slate-800 p-3 text-center">
            <p className="text-2xl font-bold text-blue-400">{visible.length}</p>
            <p className="text-xs text-slate-400">Visible Inspections</p>
          </div>

          {/* Severity filter */}
          <div>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">Severity</h3>
            {ALL_SEVERITIES.map((s) => (
              <label key={s} className="flex items-center gap-2 py-1 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={sevFilter.has(s)}
                  onChange={() => toggleSev(s)}
                  className="rounded border-slate-600 accent-blue-500"
                />
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ background: SEV_COLORS[s] }}
                />
                <span className="text-sm text-slate-300">{s}</span>
              </label>
            ))}
          </div>

          {/* Risk filter */}
          <div>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">Risk Level</h3>
            {ALL_RISKS.map((r) => (
              <label key={r} className="flex items-center gap-2 py-1 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={riskFilter.has(r)}
                  onChange={() => toggleRisk(r)}
                  className="rounded border-slate-600 accent-blue-500"
                />
                <span className="text-sm text-slate-300">{r}</span>
              </label>
            ))}
          </div>

          {/* Legend */}
          <div>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">Legend</h3>
            <div className="space-y-1.5">
              {ALL_SEVERITIES.map((s) => (
                <div key={s} className="flex items-center gap-2 text-sm text-slate-300">
                  <span
                    className="h-3 w-3 rounded-full border"
                    style={{ background: SEV_COLORS[s], borderColor: SEV_COLORS[s] }}
                  />
                  {s} Severity
                </div>
              ))}
            </div>
          </div>

          {error && (
            <p className="rounded-lg bg-red-500/10 border border-red-500/30 px-3 py-2 text-xs text-red-400">
              API Error: {error}
            </p>
          )}
        </div>
      </motion.aside>

      {/* Toggle sidebar when closed */}
      {!sidebarOpen && (
        <button
          onClick={() => setSidebarOpen(true)}
          className="absolute left-0 top-1/2 z-20 -translate-y-1/2 rounded-r-xl border border-l-0 border-slate-700 bg-slate-800 px-2 py-4 text-slate-300 hover:bg-slate-700 transition-colors"
        >
          <Layers className="h-4 w-4" />
        </button>
      )}

      {/* Map */}
      <div className="flex-1">
        <MapContainer
          center={[20.5937, 78.9629]}
          zoom={5}
          style={{ height: '100%', width: '100%', background: '#0f172a' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          />
          {visible.map((m) => (
            <CircleMarker
              key={m.id}
              center={[m.latitude ?? m.lat, m.longitude ?? m.lng]}
              radius={m.severity === 'Critical' ? 14 : m.severity === 'High' ? 12 : 10}
              pathOptions={{
                color: SEV_COLORS[m.severity] || '#64748b',
                fillColor: SEV_COLORS[m.severity] || '#64748b',
                fillOpacity: 0.7,
                weight: 2,
              }}
            >
              <Popup>
                <div className="min-w-48 text-sm">
                  <p className="mb-1 font-semibold text-slate-800">{m.address || 'Unknown Location'}</p>
                  <div className="mb-1 flex items-center gap-1">
                    <SeverityBadge level={m.severity} />
                    <span className="text-xs text-slate-500">· Risk: {m.risk_level}</span>
                  </div>
                  {m.damage_types?.length > 0 && (
                    <p className="text-xs text-slate-600 mb-1">{m.damage_types.join(', ')}</p>
                  )}
                  <p className="text-xs text-slate-500">{formatDate(m.timestamp)}</p>
                  <Link
                    to={`/history`}
                    className="mt-2 inline-block text-xs text-blue-600 hover:underline"
                  >
                    View Details →
                  </Link>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
