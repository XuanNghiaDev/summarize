import React from 'react';

export default function QuizCard({ index, question, value, onChange, showAnswer }) {
  const handleSelect = (v) => onChange(index, v);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-sm text-slate-500">Question {index + 1}</div>
          <div className="mt-2 text-base font-medium text-slate-900">{question.question}</div>
        </div>
      </div>

      <div className="mt-3">
        {question.type === 'mcq' && (
          <div className="grid gap-2 sm:grid-cols-2">
            {question.options.map((opt, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleSelect(opt)}
                disabled={showAnswer}
                className={`text-left rounded-lg border px-3 py-2 text-sm ${value === opt ? 'border-sky-600 bg-sky-50' : 'border-slate-200 bg-white'}`}
              >
                {opt}
              </button>
            ))}
          </div>
        )}

        {question.type === 'tf' && (
          <div className="flex gap-3">
            <button onClick={() => handleSelect(true)} disabled={showAnswer} className={`rounded-full px-3 py-1 ${value === true ? 'bg-sky-600 text-white' : 'bg-slate-100'}`}>True</button>
            <button onClick={() => handleSelect(false)} disabled={showAnswer} className={`rounded-full px-3 py-1 ${value === false ? 'bg-sky-600 text-white' : 'bg-slate-100'}`}>False</button>
          </div>
        )}

        {(question.type === 'fill' || question.type === 'short') && (
          <input type="text" value={value || ''} onChange={(e) => handleSelect(e.target.value)} disabled={showAnswer} className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" />
        )}
      </div>

      {showAnswer && (
        <div className="mt-3 rounded-md bg-slate-50 p-3 text-sm text-slate-700">
          <div><strong>Answer:</strong> {String(question.correct_answer)}</div>
          <div className="mt-1 text-xs text-slate-500">{question.explanation}</div>
        </div>
      )}
    </div>
  );
}
