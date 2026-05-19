import React from 'react';

export default function QuizControls({ quizType, setQuizType, numQuestions, setNumQuestions, onGenerate, loading }) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-3">
        <label className="text-sm font-medium">Type</label>
        <select value={quizType} onChange={(e) => setQuizType(e.target.value)} className="rounded-3xl border border-slate-200 px-3 py-2 text-sm">
          <option value="mcq">MCQ</option>
          <option value="tf">True / False</option>
          <option value="fill">Fill in the blank</option>
          <option value="short">Short answer</option>
        </select>

        <label className="text-sm font-medium">Count</label>
        <input type="number" min={1} max={50} value={numQuestions} onChange={(e) => setNumQuestions(Number(e.target.value))} className="w-20 rounded-3xl border border-slate-200 px-3 py-2 text-sm" />
      </div>

      <div>
        <button
          type="button"
          onClick={onGenerate}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
        >
          {loading ? 'Generating...' : 'Generate Quiz'}
        </button>
      </div>
    </div>
  );
}
