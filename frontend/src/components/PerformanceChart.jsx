import { useMemo } from 'react';

export default function PerformanceChart({ title, data, type = 'line' }) {
  const chartData = useMemo(() => {
    if (type === 'line' && Array.isArray(data)) {
      // Daily progress data
      return data.map((item) => ({
        date: new Date(item.date).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        }),
        score: item.average_score,
        quizzes: item.quiz_count,
      }));
    } else if (type === 'bar' && Array.isArray(data)) {
      // Category performance data
      return data.map((item) => ({
        category: item.category || 'Unknown',
        score: item.average_score,
        quizzes: item.total_quizzes,
      }));
    }
    return [];
  }, [data, type]);

  if (chartData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">{title}</h2>
        <div className="h-64 flex items-center justify-center text-gray-500">
          No data available yet
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">{title}</h2>

      {type === 'line' ? (
        // Simple line chart using ASCII visualization
        <div className="h-64 flex flex-col justify-between">
          <div className="flex items-end justify-around gap-2 h-full">
            {chartData.map((item, idx) => {
              const height = (item.score / 100) * 100 || 5;
              return (
                <div key={idx} className="flex flex-col items-center gap-2 flex-1">
                  <div
                    className="bg-blue-500 rounded-t-lg w-full hover:bg-blue-600 transition"
                    style={{ height: `${height}%`, minHeight: '20px' }}
                    title={`${item.score.toFixed(1)}%`}
                  />
                  <span className="text-xs text-gray-600 text-center w-full whitespace-nowrap overflow-hidden text-ellipsis">
                    {item.date}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        // Simple bar chart
        <div className="space-y-4">
          {chartData.map((item, idx) => (
            <div key={idx} className="flex items-center gap-4">
              <span className="text-sm font-medium text-gray-700 w-24 truncate">
                {item.category}
              </span>
              <div className="flex-1 bg-gray-200 rounded-full h-8 overflow-hidden">
                <div
                  className="bg-green-500 h-full flex items-center justify-center text-white text-xs font-semibold transition"
                  style={{ width: `${Math.min(item.score, 100)}%` }}
                >
                  {item.score > 50 && `${item.score.toFixed(1)}%`}
                </div>
              </div>
              <span className="text-sm text-gray-600 w-12 text-right">
                ({item.quizzes})
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
