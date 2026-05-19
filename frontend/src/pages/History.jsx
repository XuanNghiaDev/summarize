import { useState, useEffect } from 'react';
import { quizAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';
import QuizHistoryTable from '../components/QuizHistoryTable';

export default function History() {
  const [quizzes, setQuizzes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchHistory();
  }, [page]);

  const fetchHistory = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await quizAPI.getHistory(page, 10);
      setQuizzes(response.data.items || []);
      setTotalPages(Math.max(1, Math.ceil((response.data.total || 0) / 10)));
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load quiz history');
      console.error('History error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200 py-10">
      <div className="mx-auto max-w-7xl rounded-[2rem] bg-white/95 p-8 shadow-2xl shadow-slate-200 backdrop-blur-xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Quiz History</h1>
          <p className="mt-2 text-slate-600">Review your previous quizzes and progress.</p>
        </div>

        {quizzes.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center text-slate-600">
            No quiz history found yet.
          </div>
        ) : (
          <QuizHistoryTable quizzes={quizzes} />
        )}

        {totalPages > 1 && (
          <div className="mt-6 flex items-center justify-center gap-3">
            <button
              onClick={() => setPage((prev) => Math.max(1, prev - 1))}
              disabled={page === 1}
              className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm transition hover:bg-slate-50 disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-sm text-slate-700">Page {page} of {totalPages}</span>
            <button
              onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
              disabled={page === totalPages}
              className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm transition hover:bg-slate-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
      {error && <Toast message={error} type="error" />}
    </div>
  );
}
