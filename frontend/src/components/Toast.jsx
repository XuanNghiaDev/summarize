import { AnimatePresence, motion } from 'framer-motion';

function Toast({ message, status }) {
  const tone = status === 'error' ? 'bg-rose-500 text-white' : status === 'success' ? 'bg-emerald-500 text-white' : 'bg-slate-900 text-white';

  return (
    <AnimatePresence>
      {message && (
        <motion.div
          initial={{ opacity: 0, y: -14 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -14 }}
          transition={{ duration: 0.25 }}
          className={`pointer-events-none fixed right-6 top-6 z-50 rounded-3xl px-5 py-4 shadow-[0_25px_80px_rgba(15,23,42,0.14)] ${tone}`}
        >
          <p className="text-sm font-medium">{message}</p>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default Toast;
