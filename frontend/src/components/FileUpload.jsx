import { useState } from 'react';

function FileUpload({ file, onFileChange }) {
  const [dragActive, setDragActive] = useState(false);

  const handleDrop = (event) => {
    event.preventDefault();
    setDragActive(false);
    const droppedFile = event.dataTransfer.files?.[0];
    if (droppedFile) {
      onFileChange(droppedFile);
    }
  };

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault();
        setDragActive(true);
      }}
      onDragLeave={() => setDragActive(false)}
      onDrop={handleDrop}
      className={`space-y-4 rounded-[1.75rem] border border-dashed px-5 py-6 transition ${dragActive ? 'border-sky-500 bg-sky-50' : 'border-slate-300 bg-white'}`}
    >
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-slate-900">Upload document</p>
          <p className="mt-1 text-xs text-slate-500">Drag & drop PDF, DOCX, or TXT files.</p>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">Document</span>
      </div>

      <input
        type="file"
        accept=".pdf,.docx,.txt"
        className="w-full cursor-pointer rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition hover:border-slate-400"
        onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
      />

      {file ? (
        <div className="rounded-3xl bg-slate-100 px-4 py-3 text-sm text-slate-700">
          <p className="font-medium">{file.name}</p>
          <p>{(file.size / 1024).toFixed(1)} KB</p>
        </div>
      ) : (
        <p className="text-sm text-slate-500">Drop a file here or click to choose one.</p>
      )}
    </div>
  );
}

export default FileUpload;
