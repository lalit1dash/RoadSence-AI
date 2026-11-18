import { motion } from 'framer-motion';

export default function LoadingSpinner({ text = 'Analyzing...' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12">
      {/* Spinner ring */}
      <div className="relative w-16 h-16">
        <div className="absolute inset-0 rounded-full border-4 border-slate-700" />
        <motion.div
          className="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-500"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
      </div>

      {/* Text + pulsing dots */}
      <div className="flex items-center gap-1 text-slate-300 font-medium">
        <span>{text}</span>
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            animate={{ opacity: [0.2, 1, 0.2] }}
            transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.3 }}
            className="text-blue-400 font-bold"
          >
            .
          </motion.span>
        ))}
      </div>
    </div>
  );
}
