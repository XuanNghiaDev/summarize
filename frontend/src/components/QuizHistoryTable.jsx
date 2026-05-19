import { Link } from 'react-router-dom';

export default function QuizHistoryTable({ quizzes = [] }) {
  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (quizzes.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">No quizzes attempted yet.</p>
        <Link to="/quiz" className="text-blue-600 hover:underline mt-2">
          Take your first quiz
        </Link>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b-2 border-gray-200">
            <th className="text-left py-3 px-4 font-semibold text-gray-700">Article</th>
            <th className="text-left py-3 px-4 font-semibold text-gray-700">Category</th>
            <th className="text-center py-3 px-4 font-semibold text-gray-700">Difficulty</th>
            <th className="text-center py-3 px-4 font-semibold text-gray-700">Score</th>
            <th className="text-center py-3 px-4 font-semibold text-gray-700">Time</th>
            <th className="text-left py-3 px-4 font-semibold text-gray-700">Date</th>
            <th className="text-center py-3 px-4 font-semibold text-gray-700">Action</th>
          </tr>
        </thead>
        <tbody>
          {quizzes.map((quiz) => (
            <tr key={quiz.id} className="border-b border-gray-100 hover:bg-gray-50 transition">
              <td className="py-4 px-4 truncate max-w-xs">
                <span className="text-gray-900 font-medium">
                  {quiz.article_title || 'Untitled'}
                </span>
              </td>
              <td className="py-4 px-4 text-gray-700">
                {quiz.category || '—'}
              </td>
              <td className="py-4 px-4 text-center">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold capitalize ${getDifficultyColor(quiz.difficulty)}`}>
                  {quiz.difficulty}
                </span>
              </td>
              <td className={`py-4 px-4 text-center font-bold ${getScoreColor(quiz.percentage_score)}`}>
                {quiz.score}/{quiz.total_questions}
                <br />
                <span className="text-sm">{quiz.percentage_score.toFixed(1)}%</span>
              </td>
              <td className="py-4 px-4 text-center text-gray-700">
                {Math.round(quiz.time_taken_seconds / 60)} min
              </td>
              <td className="py-4 px-4 text-gray-700 text-sm">
                {new Date(quiz.created_at).toLocaleDateString()}
              </td>
              <td className="py-4 px-4 text-center">
                <Link
                  to={`/quiz/${quiz.id}`}
                  className="text-blue-600 hover:text-blue-800 font-semibold text-sm"
                >
                  View
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
