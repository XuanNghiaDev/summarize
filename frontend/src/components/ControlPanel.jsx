function ControlPanel({ lang, model, mode, length, setLang, setModel, setMode, setLength }) {
  return (
    <section className="glass-card rounded-[2rem] border border-slate-200/70 bg-white/80 p-8 shadow-[0_30px_80px_rgba(15,23,42,0.08)] dark:border-slate-700/70 dark:bg-slate-950/80">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Control panel</p>
          <h3 className="mt-3 text-3xl font-semibold text-slate-950 dark:text-white">Model & summary settings</h3>
        </div>
        <div className="rounded-3xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700 dark:bg-slate-900 dark:text-slate-200">
          Live preview enabled
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1fr_0.65fr]">
        <div className="grid gap-4">
          <label className="text-sm font-medium text-slate-700 dark:text-slate-200">Language</label>
          <select
            className="rounded-[1.5rem] border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-200 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-cyan-400 dark:focus:ring-cyan-500/20"
            value={lang}
            onChange={(event) => setLang(event.target.value)}
          >
            <option value="vi">Vietnamese</option>
            <option value="en">English</option>
          </select>

          <label className="text-sm font-medium text-slate-700 dark:text-slate-200">Model</label>
          <select
            className="rounded-[1.5rem] border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-200 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-cyan-400 dark:focus:ring-cyan-500/20"
            value={model}
            onChange={(event) => setModel(event.target.value)}
          >
            <option value="textrank">TextRank</option>
            <option value="bilstm">BiLSTM</option>
            <option value="seq2seq">Seq2Seq</option>
            <option value="transformer">Transformer</option>
          </select>
        </div>

        <div className="grid gap-4">
          <label className="text-sm font-medium text-slate-700 dark:text-slate-200">Mode</label>
          <div className="grid gap-3 rounded-[1.75rem] border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-950/70">
            <button
              type="button"
              onClick={() => setMode('extractive')}
              className={`rounded-3xl px-4 py-3 text-sm font-semibold transition ${mode === 'extractive' ? 'bg-slate-950 text-white dark:bg-cyan-400 dark:text-slate-950' : 'bg-white text-slate-800 dark:bg-slate-900 dark:text-slate-200'}`}
            >
              Extractive
            </button>
            <button
              type="button"
              onClick={() => setMode('abstractive')}
              className={`rounded-3xl px-4 py-3 text-sm font-semibold transition ${mode === 'abstractive' ? 'bg-slate-950 text-white dark:bg-cyan-400 dark:text-slate-950' : 'bg-white text-slate-800 dark:bg-slate-900 dark:text-slate-200'}`}
            >
              Abstractive
            </button>
          </div>

          <label className="text-sm font-medium text-slate-700 dark:text-slate-200">Summary length</label>
          <input
            type="range"
            min="10"
            max="120"
            step="5"
            value={length}
            onChange={(event) => setLength(Number(event.target.value))}
            className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-200 accent-sky-500"
          />
          <div className="flex items-center justify-between text-sm text-slate-600 dark:text-slate-300">
            <span>Length</span>
            <span>{length}%</span>
          </div>
        </div>
      </div>
    </section>
  );
}

export default ControlPanel;
