import { useState, useEffect } from 'react';
import { summaryAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';

export default function SavedSummaries() {
  const [summaries, setSummaries] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [filters, setFilters] = useState({
    language: '',
    algorithm: '',
    isFavorite: false,
  });

  useEffect(() => {
    fetchSummaries();
  }, [page, filters]);

  const fetchSummaries = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const filterParams = {};
      if (filters.language) filterParams.language = filters.language;
      if (filters.algorithm) filterParams.algorithm = filters.algorithm;
      if (filters.isFavorite) filterParams.is_favorite = true;

      const response = await summaryAPI.getList(page, 10, filterParams);
      setSummaries(response.data.items);
      setTotalPages(Math.ceil(response.data.total / 10));
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load summaries');
      console.error('Summaries error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleFavorite = async (summaryId, currentFavorite) => {
    try {
      await summaryAPI.toggleFavorite(summaryId);
      setSummaries((prev) =>
        prev.map((s) =>
          s.id === summaryId ? { ...s, is_favorite: !currentFavorite } : s
        )
      );
    } catch (err) {
      setError('Failed to update favorite status');
    }
  };

  const handleDeleteSummary = async (summaryId) => {
    if (window.confirm('Are you sure you want to delete this summary?')) {
      try {
        await summaryAPI.delete(summaryId);
        setSummaries((prev) => prev.filter((s) => s.id !== summaryId));
      } catch (err) {
        setError('Failed to delete summary');
      }
    }
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">✍️ Saved Summaries</h1>
          <p className="text-gray-600 mt-1">Manage your article summaries</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6 space-y-4">
          <h2 className="font-semibold text-gray-900">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Language
              </label>
              <select
                value={filters.language}
                onChange={(e) => {
                  setFilters({ ...filters, language: e.target.value });
                  setPage(1);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">All Languages</option>
                <option value="vi">Vietnamese</option>
                <option value="en">English</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Algorithm
              </label>
              <select
                value={filters.algorithm}
                onChange={(e) => {
                  setFilters({ ...filters, algorithm: e.target.value });
                  setPage(1);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">All Algorithms</option>
                <option value="textrank">TextRank</option>
                <option value="bilstm">BiLSTM</option>
              </select>
            </div>

            <div className="flex items-end">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.isFavorite}
                  onChange={(e) => {
                    setFilters({ ...filters, isFavorite: e.target.checked });
                    setPage(1);
                  }}
                  className="w-4 h-4"
                />
                <span className="text-sm font-medium text-gray-700">
                  Favorites Only ⭐
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Summaries Grid */}
        {summaries.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 text-lg">No summaries found.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {summaries.map((summary) => (
              <div
                key={summary.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition p-6 flex flex-col"
              >
                {/* Title */}
                <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2">
                  {summary.article_title || 'Untitled'}
                </h3>

                {/* Summary Preview */}
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {summary.summary_text}
                </p>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-2 mb-4 text-xs text-gray-600">
                  <div>
                    <p className="font-semibold">Algorithm</p>
                    <p className="text-gray-500">{summary.algorithm_used}</p>
                  </div>
                  <div>
                    <p className="font-semibold">Compression</p>
                    <p className="text-gray-500">
                      {(summary.compression_ratio * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 mt-auto">
                  <button
                    onClick={() => handleToggleFavorite(summary.id, summary.is_favorite)}
                    className={`flex-1 py-2 rounded-lg font-semibold transition ${
                      summary.is_favorite
                        ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {summary.is_favorite ? '⭐ Favorited' : '☆ Favorite'}
                  </button>
                  <button
                    onClick={() => handleDeleteSummary(summary.id)}
                    className="flex-1 bg-red-100 hover:bg-red-200 text-red-700 py-2 rounded-lg font-semibold transition"
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center gap-2 mt-8">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
            >
              ← Previous
            </button>
            <span className="px-4 py-2 text-gray-700">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50"
            >
              Next →
            </button>
          </div>
        )}
      </main>

      {error && <Toast message={error} type="error" />}
    </div>
  );
}
