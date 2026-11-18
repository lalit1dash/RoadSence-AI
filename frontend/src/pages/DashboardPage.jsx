import { useState } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Clock, Activity, AlertOctagon, TrendingUp, Construction } from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import StatCard from '../components/StatCard';
import SeverityBadge from '../components/SeverityBadge';
import { useFetch } from '../hooks/useApi';
import { formatDate } from '../utils/formatters';

const SEV_COLORS = { Low: '#22c55e', Medium: '#eab308', High: '#f97316', Critical: '#ef4444' };
const DAMAGE_COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#f59e0b', '#ec4899'];

const EMPTY_STATS = {
  total_inspections: 0,
  critical_count: 0,
  high_risk_count: 0,
  pending_repairs: 0,
};

const container = { hidden: {}, show: { transition: { staggerChildren: 0.1 } } };
const card = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

function SkeletonCard() {
  return (
    <div className="rounded-xl bg-slate-800 border border-slate-700 p-5 animate-pulse">
      <div className="h-4 w-24 rounded bg-slate-700 mb-3" />
      <div className="h-8 w-16 rounded bg-slate-700" />
    </div>
  );
}

export default function DashboardPage() {
  const { data, loading, error, refetch } = useFetch('/api/dashboard/stats');
  const stats = data || EMPTY_STATS;

  // Normalize live severity from API into an array for Recharts
  const rawSeverity = data?.severity_distribution || {};
  const severity = Array.isArray(rawSeverity)
    ? rawSeverity
    : Object.entries(rawSeverity).map(([name, value]) => ({ name, value }));

  const monthly = Array.isArray(data?.monthly_trend) ? data.monthly_trend : [];

  // Normalize live damage types from API into an array for Recharts
  const rawDamage = data?.damage_type_distribution || {};
  const damageTypes = Array.isArray(rawDamage)
    ? rawDamage
    : Object.entries(rawDamage).map(([name, value]) => ({
        name: name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
        value,
      }));

  const recent = Array.isArray(data?.recent_inspections) ? data.recent_inspections : [];

  const [now] = useState(new Date());

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="mx-auto max-w-7xl px-4 py-8">
        {/* Header */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-100">Analytics Dashboard</h1>
            <p className="mt-1 flex items-center gap-2 text-sm text-slate-400">
              <Clock className="h-4 w-4" />
              {now.toLocaleString('en-US', { dateStyle: 'full', timeStyle: 'short' })}
            </p>
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
          <div className="mb-6 flex items-center gap-3 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            <AlertOctagon className="h-4 w-4" />
            <span>Unable to connect to live API: {error}</span>
            <button onClick={refetch} className="ml-auto underline hover:no-underline">
              Retry
            </button>
          </div>
        )}

        {/* KPI Cards */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="mb-8 grid gap-5 sm:grid-cols-2 xl:grid-cols-4"
        >
          {loading ? (
            Array(4).fill(0).map((_, i) => <SkeletonCard key={i} />)
          ) : (
            <>
              <motion.div variants={card}>
                <StatCard title="Total Inspections" value={stats.total_inspections ?? 0} icon={Activity} color="blue" change={12} />
              </motion.div>
              <motion.div variants={card}>
                <StatCard title="Critical Alerts" value={stats.critical_alerts ?? stats.critical_count ?? 0} icon={AlertOctagon} color="red" change={-5} />
              </motion.div>
              <motion.div variants={card}>
                <StatCard title="High Risk Roads" value={stats.high_risk_roads ?? stats.high_risk_count ?? 0} icon={TrendingUp} color="orange" change={8} />
              </motion.div>
              <motion.div variants={card}>
                <StatCard title="Pending Repairs" value={stats.pending_repairs ?? 0} icon={Construction} color="yellow" />
              </motion.div>
            </>
          )}
        </motion.div>

        {/* Charts Row */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="mb-8 grid gap-5 md:grid-cols-2 xl:grid-cols-4"
        >
          {/* Severity Pie */}
          <motion.div variants={card} className="col-span-1 rounded-xl border border-slate-700 bg-slate-800 p-5">
            <h3 className="mb-4 font-semibold text-slate-200">Severity Distribution</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={severity} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} paddingAngle={3}>
                  {severity.map((entry) => (
                    <Cell key={entry.name} fill={SEV_COLORS[entry.name] || '#64748b'} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }} />
                <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Monthly Bar */}
          <motion.div variants={card} className="col-span-1 rounded-xl border border-slate-700 bg-slate-800 p-5 md:col-span-1 xl:col-span-2">
            <h3 className="mb-4 font-semibold text-slate-200">Monthly Inspection Trend</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={monthly} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="month" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }} />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Inspections" />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Damage Type Pie */}
          <motion.div variants={card} className="col-span-1 rounded-xl border border-slate-700 bg-slate-800 p-5">
            <h3 className="mb-4 font-semibold text-slate-200">Damage Types</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={damageTypes} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} paddingAngle={3}>
                  {damageTypes.map((_, idx) => (
                    <Cell key={idx} fill={DAMAGE_COLORS[idx % DAMAGE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }} />
                <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>
        </motion.div>

        {/* Recent Inspections Table */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="rounded-xl border border-slate-700 bg-slate-800 overflow-hidden"
        >
          <div className="border-b border-slate-700 px-5 py-4">
            <h3 className="font-semibold text-slate-200">Recent Inspections</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700 text-left text-xs uppercase tracking-wider text-slate-500">
                  <th className="px-5 py-3">ID</th>
                  <th className="px-5 py-3">Location</th>
                  <th className="px-5 py-3">Severity</th>
                  <th className="px-5 py-3">Risk</th>
                  <th className="px-5 py-3">Detections</th>
                  <th className="px-5 py-3">Date</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((r, i) => (
                  <tr
                    key={r.id || i}
                    className="border-b border-slate-700/50 hover:bg-slate-700/40 transition-colors"
                  >
                    <td className="px-5 py-3 font-mono text-xs text-slate-400">{r.id || `#${i + 1}`}</td>
                    <td className="px-5 py-3 text-slate-200">{r.address || r.road_name || '—'}</td>
                    <td className="px-5 py-3"><SeverityBadge level={r.severity} /></td>
                    <td className="px-5 py-3 text-slate-300">{r.risk_level || '—'}</td>
                    <td className="px-5 py-3 text-blue-400 font-semibold">{r.damage_count ?? '—'}</td>
                    <td className="px-5 py-3 text-slate-400 whitespace-nowrap">{formatDate(r.timestamp)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
