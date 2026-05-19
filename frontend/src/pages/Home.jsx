import { useMemo, useState } from 'react';
import { ArrowRight, Loader2 } from 'lucide-react';
import TextInput from '../components/TextInput';
import FileUpload from '../components/FileUpload';
import SummaryResult from '../components/SummaryResult';
import Toast from '../components/Toast';
import { summarize } from '../services/summaryService';
import { uploadDocument } from '../services/aiService';

const MODEL_OPTIONS = [
  { value: 'textrank', label: 'TextRank' },
  { value: 'bilstm', label: 'BiLSTM' },
  { value: 'seq2seq', label: 'Seq2Seq' },
];

const LANG_OPTIONS = [
  { value: 'en', label: 'English' },
  { value: 'vi', label: 'Vietnamese' },
];

function Home() {
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const [model, setModel] = useState('textrank');
  const [lang, setLang] = useState('en');
  const [length, setLength] = useState(40);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ message: '', type: 'info' });
  

  const originalWordCount = useMemo(() => text.trim().split(/\s+/).filter(Boolean).length, [text]);
  const summaryWordCount = useMemo(() => result?.summary?.trim().split(/\s+/).filter(Boolean).length || 0, [result]);
  const reductionPercent = originalWordCount && summaryWordCount
    ? Math.max(0, Math.round(((originalWordCount - summaryWordCount) / originalWordCount) * 100))
    : null;

  const handleToast = (message, type = 'info') => {
    setToast({ message, type });
    window.setTimeout(() => setToast({ message: '', type: 'info' }), 3200);
  };

  const handleSummarize = async () => {
    if (!file && (!text || text.trim().length < 20)) {
      handleToast('Please provide at least 20 characters or upload a file.', 'error');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        model,
        lang,
        summary_length: length,
      };

      const response = file
        ? await uploadDocument(file, payload)
        : await summarize({ text, ...payload });

      const summary = response.summary || response.summary_text || '';
      if (!summary) {
        throw new Error('Backend returned an unexpected summarization response.');
      }

      setResult({
        summary,
        model: response.model || model,
        lang: response.lang || lang,
        time_ms: response.time_ms,
        sourceFile: response.sourceFile,
      });

      handleToast('Summary generated successfully.', 'success');
    } catch (error) {
      const message = error?.response?.data?.error || error.message || 'Unable to summarize text.';
      handleToast(message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (selectedFile) => {
    setFile(selectedFile);
    setResult(null);
  };

  return (
    <div className="space-y-8 pb-16">
      <Toast message={toast.message} status={toast.type} />

      <section className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm shadow-slate-200/30">
        <div className="max-w-3xl space-y-4">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-sky-600">AI Text Summarizer</p>
          <h1 className="text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">Clean, fast summarization for content teams.</h1>
          <p className="max-w-2xl text-base leading-7 text-slate-600">
            Paste an article or upload a document, select a model, and generate a concise AI summary with one focused workflow.
          </p>
        </div>
      </section>

      <section id="workspace" className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm shadow-slate-200/30">
        <div className="space-y-6">
          <div className="grid gap-3 sm:grid-cols-[1fr_auto] sm:items-end">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-500">Summary workspace</p>
              <h2 className="mt-3 text-2xl font-semibold text-slate-950">Paste text or attach a file to summarize.</h2>
            </div>
            <div className="rounded-full bg-slate-100 px-4 py-2 text-sm text-slate-700">
              {file ? `File mode: ${file.name}` : 'Text mode'}
            </div>
          </div>
          

          <TextInput value={text} onChange={setText} />
          <FileUpload file={file} onFileChange={handleFileChange} />

          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <label className="text-sm font-medium text-slate-700">Language</label>
              <select
                value={lang}
                onChange={(event) => setLang(event.target.value)}
                className="mt-3 w-full rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
              >
                {LANG_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700">Model</label>
              <select
                value={model}
                onChange={(event) => setModel(event.target.value)}
                className="mt-3 w-full rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
              >
                {MODEL_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700">Summary length</label>
              <div className="mt-3">
                <input
                  type="range"
                  min="10"
                  max="100"
                  step="5"
                  value={length}
                  onChange={(event) => setLength(Number(event.target.value))}
                  className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-200 accent-sky-600"
                />
                <div className="mt-2 flex items-center justify-between text-sm text-slate-600">
                  <span>Short</span>
                  <span>{length}%</span>
                  <span>Long</span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-slate-500">Your summary appears below once the backend finishes processing.</p>
            <button
              type="button"
              onClick={handleSummarize}
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-full bg-sky-600 px-6 py-3 text-sm font-semibold text-white shadow-md shadow-sky-200/50 transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? <><Loader2 className="h-4 w-4 animate-spin" /> Processing...</> : <>Generate Summary <ArrowRight size={16} /></>}
            </button>
          </div>
        </div>
      </section>

      {result && (
        <SummaryResult
          summary={result.summary}
          model={result.model}
          lang={result.lang}
          timeMs={result.time_ms}
          reduction={reductionPercent}
          originalWords={originalWordCount}
          summaryWords={summaryWordCount}
          sourceFile={result.sourceFile}
        />
      )}
    </div>
  );
}

export default Home;
