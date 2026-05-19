export default function DashboardStats({ analytics }) {
  const stats = [
    {
      label: 'Total Quizzes',
      value: analytics.total_quizzes,
      icon: '📝',
      color: 'blue',
    },
    {
      label: 'Average Score',
      value: `${analytics.average_score.toFixed(1)}%`,
      icon: '⭐',
      color: 'green',
    },
    {
      label: 'Reading Time',
      value: `${Math.round(analytics.total_reading_time_seconds / 60)} min`,
      icon: '⏱️',
      color: 'purple',
    },
    {
      label: 'Summaries Generated',
      value: analytics.total_summaries_generated,
      icon: '✍️',
      color: 'orange',
    },
  ];

  const colorClasses = {
    blue: 'bg-blue-100 text-blue-800',
    green: 'bg-green-100 text-green-800',
    purple: 'bg-purple-100 text-purple-800',
    orange: 'bg-orange-100 text-orange-800',
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, idx) => (
        <div key={idx} className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">{stat.label}</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
            </div>
            <div className={`text-4xl ${colorClasses[stat.color]} p-3 rounded-lg`}>
              {stat.icon}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
