import { useState, useEffect } from 'react';
import { leaderboardAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';

export default function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState(null);
  const [sortBy, setSortBy] = useState('score'); // 'score' or 'quizzes'
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLeaderboard();
  }, [sortBy]);

  const fetchLeaderboard = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      let response;
      if (sortBy === 'score') {
        response = await leaderboardAPI.getByScore();
      } else {
        response = await leaderboardAPI.getByQuizzes();
      }
      
      setLeaderboard(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load leaderboard');
      console.error('Leaderboard error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!leaderboard) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Toast message={error || 'Failed to load leaderboard'} type="error" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">🏆 Global Leaderboard</h1>
          <p className="text-gray-600 mt-1">See how you rank against other learners</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Sort Options */}
        <div className="bg-white rounded-lg shadow p-4 mb-6 flex gap-4">
          <button
            onClick={() => setSortBy('score')}
            className={`px-4 py-2 rounded-lg font-semibold transition ${
              sortBy === 'score'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
            }`}
          >
            📊 By Average Score
          </button>
          <button
            onClick={() => setSortBy('quizzes')}
            className={`px-4 py-2 rounded-lg font-semibold transition ${
              sortBy === 'quizzes'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
            }`}
          >
            📈 By Quiz Count
          </button>
        </div>

        {/* User's Rank */}
        {leaderboard.user_rank && (
          <div className="bg-blue-50 border-l-4 border-blue-600 p-4 mb-6 rounded">
            <p className="text-blue-900 font-semibold">
              Your Rank: <span className="text-2xl">#{leaderboard.user_rank}</span> out of{' '}
              <span className="font-bold">{leaderboard.total_users}</span> users
            </p>
          </div>
        )}

        {/* Leaderboard Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
                <th className="text-center py-4 px-4 font-semibold">Rank</th>
                <th className="text-left py-4 px-4 font-semibold">User</th>
                <th className="text-center py-4 px-4 font-semibold">Avg. Score</th>
                <th className="text-center py-4 px-4 font-semibold">Quizzes</th>
                <th className="text-center py-4 px-4 font-semibold">Summaries</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.entries.map((entry) => {
                const isTopThree = entry.rank <= 3;
                const medalEmoji = ['🥇', '🥈', '🥉'][entry.rank - 1];

                return (
                  <tr
                    key={entry.rank}
                    className={`border-b transition ${
                      isTopThree
                        ? 'bg-gradient-to-r from-yellow-50 to-orange-50 hover:from-yellow-100 hover:to-orange-100'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <td className="text-center py-4 px-4 font-bold text-lg">
                      {isTopThree ? medalEmoji : `#${entry.rank}`}
                    </td>
                    <td className="text-left py-4 px-4">
                      <div className="flex items-center gap-3">
                        {entry.avatar_url ? (
                          <img
                            src={entry.avatar_url}
                            alt={entry.full_name || entry.email}
                            className="w-10 h-10 rounded-full"
                          />
                        ) : (
                          <div className="w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">
                            {(entry.full_name || entry.email).charAt(0).toUpperCase()}
                          </div>
                        )}
                        <div>
                          <p className="font-semibold text-gray-900">
                            {entry.full_name || entry.email}
                          </p>
                          <p className="text-sm text-gray-600">{entry.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="text-center py-4 px-4">
                      <span className="text-lg font-bold text-blue-600">
                        {entry.average_score.toFixed(1)}%
                      </span>
                    </td>
                    <td className="text-center py-4 px-4 text-gray-700">
                      <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                        {entry.total_quizzes}
                      </span>
                    </td>
                    <td className="text-center py-4 px-4 text-gray-700">
                      <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full">
                        {entry.total_summaries}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Footer Stats */}
        <div className="mt-6 text-center text-gray-600">
          <p className="text-sm">Showing top 50 users • Updates daily</p>
        </div>
      </main>

      {error && <Toast message={error} type="error" />}
    </div>
  );
}
