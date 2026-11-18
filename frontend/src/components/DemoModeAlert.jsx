import { motion } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';

export default function DemoModeAlert() {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="flex items-start gap-3 rounded-xl border border-yellow-500/40 bg-yellow-500/10 px-4 py-3 text-sm text-yellow-300"
    >
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-yellow-400" />
      <span>
        <strong>DEMO MODE:</strong> Detections are simulated for demonstration purposes. Real ML
        model weights are not loaded.
      </span>
    </motion.div>
  );
}
