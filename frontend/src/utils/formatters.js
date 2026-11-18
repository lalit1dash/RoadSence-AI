// Utility formatter functions for RoadSense

export function formatDate(isoString) {
  if (!isoString) return 'N/A';
  const date = new Date(isoString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }).replace(',', '').replace(' at', ' at');
}

export function getSeverityColor(level) {
  const map = {
    Low: 'text-green-400',
    Medium: 'text-yellow-400',
    High: 'text-orange-400',
    Critical: 'text-red-500',
  };
  return map[level] || 'text-slate-400';
}

export function getSeverityBg(level) {
  const map = {
    Low: 'bg-green-500/20 text-green-400 border-green-500/40',
    Medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40',
    High: 'bg-orange-500/20 text-orange-400 border-orange-500/40',
    Critical: 'bg-red-500/20 text-red-400 border-red-500/40',
  };
  return map[level] || 'bg-slate-700 text-slate-400 border-slate-600';
}

export function getRiskColor(level) {
  const map = {
    Low: 'text-green-400',
    Moderate: 'text-yellow-400',
    High: 'text-orange-400',
    Critical: 'text-red-500',
  };
  return map[level] || 'text-slate-400';
}

export function formatConfidence(score) {
  if (score === null || score === undefined) return 'N/A';
  return `${(score * 100).toFixed(1)}%`;
}

export function getDamageDisplayName(key) {
  const map = {
    alligator_crack: 'Alligator Crack',
    longitudinal_crack: 'Longitudinal Crack',
    transverse_crack: 'Transverse Crack',
    pothole: 'Pothole',
    rutting: 'Rutting',
    raveling: 'Raveling',
    bleeding: 'Bleeding',
    edge_crack: 'Edge Crack',
    depression: 'Depression',
    patching: 'Patching',
  };
  if (map[key]) return map[key];
  // Fallback: capitalize and replace underscores
  return key
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}
