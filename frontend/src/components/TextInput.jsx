function TextInput({ value, onChange }) {
  const count = value ? value.length : 0;

  return (
    <div className="space-y-3">
      <label htmlFor="source-text" className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-700">
        Paste your article or upload a document
      </label>
      <textarea
        id="source-text"
        className="min-h-[260px] w-full rounded-[1.75rem] border border-slate-200 bg-white px-5 py-5 text-sm leading-7 text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Paste your article or upload a document..."
      />
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>Supports PDF, DOCX and TXT content.</span>
        <span>{count.toLocaleString()} characters</span>
      </div>
    </div>
  );
}

export default TextInput;
