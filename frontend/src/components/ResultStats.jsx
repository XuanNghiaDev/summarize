function ResultStats({ stats }) {
  return (
    <section className="grid gap-5 lg:grid-cols-4">
      {[
        { label: 'Compression', value: `${stats.compression}%`, description: 'Reduced length' },
        { label: 'Original words', value: `${stats.originalWords}`, description: 'Source article' },
        { label: 'Summary words', value: `${stats.summaryWords}`, description: 'Generated summary' },
        { label: 'Latency', value: `${stats.timeMs} ms`, description: 'Processing time' },
      ].map((item) => (
        <div key={item.label} className="rounded-[1.75rem] border border-slate-200/70 bg-white/90 p-6 shadow-[0_18px_60px_rgba(15,23,42,0.06)] dark:border-slate-700/70 dark:bg-slate-950/80">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">{item.label}</p>
          <p className="mt-4 text-3xl font-semibold text-slate-950 dark:text-white">{item.value}</p>
          <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-400">{item.description}</p>
        </div>
      ))}
    </section>
  );
}

export default ResultStats;
