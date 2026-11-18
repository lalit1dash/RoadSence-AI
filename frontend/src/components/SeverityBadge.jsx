const CONFIG = {
  Low: {
    dot: 'bg-green-400',
    badge: 'bg-green-500/20 text-green-400 border border-green-500/40',
  },
  Medium: {
    dot: 'bg-yellow-400',
    badge: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/40',
  },
  High: {
    dot: 'bg-orange-400',
    badge: 'bg-orange-500/20 text-orange-400 border border-orange-500/40',
  },
  Critical: {
    dot: 'bg-red-500',
    badge: 'bg-red-500/20 text-red-400 border border-red-500/40',
  },
};

export default function SeverityBadge({ level }) {
  const cfg = CONFIG[level] || {
    dot: 'bg-slate-500',
    badge: 'bg-slate-700 text-slate-300 border border-slate-600',
  };

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold ${cfg.badge}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${cfg.dot}`} />
      {level || 'Unknown'}
    </span>
  );
}
