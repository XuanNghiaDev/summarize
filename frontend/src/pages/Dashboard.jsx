import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../services/useAuth';
import { analyticsAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';
import DashboardStats from '../components/DashboardStats';
import PerformanceChart from '../components/PerformanceChart';
import QuizHistoryTable from '../components/QuizHistoryTable';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await analyticsAPI.getDashboard();
      setDashboard(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load dashboard');
      console.error('Dashboard error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!dashboard) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Toast message={error || 'Failed to load dashboard'} type="error" />
      </div>
    );
  }

  const { user_profile, analytics, recent_quizzes, category_performance, daily_progress } = dashboard;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome, {user_profile.full_name || user_profile.email}! 👋
            </h1>
            <p className="text-gray-600 mt-1">Your learning dashboard</p>
          </div>
          <button
            onClick={logout}
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Stats Cards */}
        <DashboardStats analytics={analytics} />

        {/* Charts and Performance */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Daily Progress Chart */}
          <PerformanceChart
            title="Daily Progress"
            data={daily_progress}
            type="line"
          />

          {/* Category Performance */}
          <PerformanceChart
            title="Category Performance"
            data={category_performance}
            type="bar"
          />
        </div>

        {/* Recent Quizzes */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Recent Quizzes</h2>
          <QuizHistoryTable quizzes={recent_quizzes} />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/quiz"
            className="bg-blue-600 hover:bg-blue-700 text-white p-6 rounded-lg text-center font-semibold transition"
          >
            Take Quiz
          </Link>
          <Link
            to="/summaries"
            className="bg-green-600 hover:bg-green-700 text-white p-6 rounded-lg text-center font-semibold transition"
          >
            View Summaries
          </Link>
          <Link
            to="/leaderboard"
            className="bg-purple-600 hover:bg-purple-700 text-white p-6 rounded-lg text-center font-semibold transition"
          >
            Global Leaderboard
          </Link>
        </div>
      </main>

      {error && <Toast message={error} type="error" />}
    </div>
  );
}
