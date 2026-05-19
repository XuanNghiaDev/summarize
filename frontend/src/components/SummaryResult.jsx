import { useState } from 'react';
import { Copy, DownloadCloud } from 'lucide-react';

function SummaryResult({ summary, model, lang, timeMs, reduction, originalWords, summaryWords, sourceFile }) {
  const [copied, setCopied] = useState(false);

  if (!summary) {
    return null;
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(summary);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error(error);
    }
  };

  const handleDownload = () => {
    const file = new Blob([summary], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(file);
    link.download = 'summary.txt';
    link.click();
    URL.revokeObjectURL(link.href);
  };

  return (
    <section className="space-y-6 rounded-[1.75rem] border border-slate-200 bg-white p-6 shadow-sm shadow-slate-200/30">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Summary output</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">Generated summary</h2>
          <p className="mt-2 text-sm text-slate-600">{sourceFile ? `Source: ${sourceFile}` : 'Text input summary.'}</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handleCopy}
            className="inline-flex items-center gap-2 rounded-full bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
          >
            <Copy size={16} /> {copied ? 'Copied' : 'Copy'}
          </button>
          <button
            type="button"
            onClick={handleDownload}
            className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-50"
          >
            <DownloadCloud size={16} /> Download
          </button>
        </div>
      </div>

      <div className="rounded-[1.5rem] border border-slate-200 bg-slate-50 p-6 text-sm leading-7 text-slate-700">
        <p>{summary}</p>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-3xl bg-slate-100 p-4 text-center">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Model</p>
          <p className="mt-3 text-base font-semibold text-slate-950">{model}</p>
        </div>
        <div className="rounded-3xl bg-slate-100 p-4 text-center">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Time</p>
          <p className="mt-3 text-base font-semibold text-slate-950">{timeMs} ms</p>
        </div>
        <div className="rounded-3xl bg-slate-100 p-4 text-center">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Reduction</p>
          <p className="mt-3 text-base font-semibold text-slate-950">{reduction != null ? `${reduction}%` : '—'}</p>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-3xl bg-slate-50 p-4 text-center text-sm text-slate-600">
          Original words
          <p className="mt-2 font-semibold text-slate-950">{originalWords || '—'}</p>
        </div>
        <div className="rounded-3xl bg-slate-50 p-4 text-center text-sm text-slate-600">
          Summary words
          <p className="mt-2 font-semibold text-slate-950">{summaryWords}</p>
        </div>
      </div>
    </section>
  );
}

export default SummaryResult;
