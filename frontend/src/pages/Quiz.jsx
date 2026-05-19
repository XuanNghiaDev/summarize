import { useState } from 'react';
import QuizControls from '../components/QuizControls';
import QuizCard from '../components/QuizCard';
import LoadingSpinner from '../components/LoadingSpinner';
import FileUpload from '../components/FileUpload';
import { generateQuiz } from '../services/quizService';
import { uploadQuizFile } from '../services/aiService';

export default function Quiz() {
  const [text, setText] = useState('');
  const [quizType, setQuizType] = useState('mcq');
  const [numQuestions, setNumQuestions] = useState(5);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [previewText, setPreviewText] = useState('');
  const [answers, setAnswers] = useState({});
  const [score, setScore] = useState(null);
  const [showAnswers, setShowAnswers] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const handleGenerate = async () => {
    if (!text || text.trim().length < 20) {
      return alert('Please enter at least 20 characters to generate a quiz.');
    }

    setLoading(true);
    try {
      const response = await generateQuiz({
        text,
        quiz_type: quizType,
        num_questions: numQuestions,
        lang: 'vi',
        difficulty: 'medium',
      });

      const questionsPayload = Array.isArray(response)
        ? response
        : response.questions || [];

      setQuestions(questionsPayload);
      setAnswers({});
      setScore(null);
      setShowAnswers(false);
    } catch (error) {
      alert(error?.response?.data?.error || error.message || 'Failed to generate quiz.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (f) => {
    setFile(f);
    setPreviewText('');
  };

  const handleUploadGenerate = async () => {
    if (!file) return alert('Please select a file to upload.');

    setUploading(true);
    try {
      const response = await uploadQuizFile(file, {
        quiz_type: quizType,
        num_questions: numQuestions,
        summarize_first: false,
        summary_length: null,
        language: 'vi',
      });

      const questionsPayload = Array.isArray(response)
        ? response
        : response.questions || [];

      setQuestions(questionsPayload);
      setAnswers({});
      setScore(null);
      setShowAnswers(false);
      setPreviewText(response.extracted_text || response.text || response.summary || '');
    } catch (error) {
      alert(error?.response?.data?.error || error.message || 'Failed to upload file and generate quiz.');
    } finally {
      setUploading(false);
    }
  };

  const handleSelect = (idx, value) => {
    setAnswers((s) => ({ ...s, [idx]: value }));
  };

  const handleSubmit = () => {
    let correct = 0;
    questions.forEach((q, i) => {
      const given = answers[i];
      if (q.type === 'mcq' || q.type === 'short' || q.type === 'fill') {
        if (given && String(given).trim().toLowerCase() === String(q.correct_answer).trim().toLowerCase()) correct += 1;
      } else if (q.type === 'tf') {
        const expected = q.correct_answer === true || q.correct_answer === 'True';
        if ((given === true || given === 'True') === expected) correct += 1;
      }
    });
    setScore({ correct, total: questions.length });
    setShowAnswers(true);
  };

  return (
    <div className={darkMode ? 'space-y-8 pb-16 bg-slate-900 text-slate-100 min-h-[60vh] rounded-2xl p-6' : 'space-y-8 pb-16'}>
      <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm shadow-slate-200/30">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold">Generate Quiz</h2>
            <p className="text-sm text-slate-500">Create MCQ/TF/Fill/Short questions from article or summary.</p>
          </div>
          <div>
            <button
              type="button"
              onClick={() => setDarkMode((d) => !d)}
              className="rounded-full border bg-slate-50 px-3 py-2 text-sm"
            >
              {darkMode ? 'Light' : 'Dark'}
            </button>
          </div>
        </div>

        <div className="mt-4 grid gap-4 sm:grid-cols-3">
          <div className="col-span-3">
            <FileUpload file={file} onFileChange={handleFileChange} />
            <div className="mt-3 flex gap-2">
              <button onClick={handleUploadGenerate} disabled={uploading} className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white">
                {uploading ? 'Uploading...' : 'Upload & Generate Quiz'}
              </button>
              {file && (
                <button onClick={() => { setFile(null); setPreviewText(''); }} className="rounded-full border px-4 py-2 text-sm">Remove file</button>
              )}
            </div>
            {previewText && (
              <div className="mt-3 rounded-lg bg-slate-50 p-3 text-sm text-slate-700">
                <div className="font-medium">Extracted text preview</div>
                <div className="mt-1 max-h-40 overflow-auto text-xs">{previewText}</div>
              </div>
            )}
          </div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste article or summary here (min 20 chars)..."
            className="col-span-3 h-40 w-full rounded-xl border border-slate-200 p-4 text-sm outline-none"
          />

          <div className="col-span-3">
            <QuizControls
              quizType={quizType}
              setQuizType={setQuizType}
              numQuestions={numQuestions}
              setNumQuestions={setNumQuestions}
              onGenerate={handleGenerate}
              loading={loading}
            />
          </div>
        </div>
      </div>

      <div>
        {loading && <div className="flex items-center justify-center p-8"><LoadingSpinner /></div>}

        {!loading && questions.length > 0 && (
          <div className="space-y-4">
            {questions.map((q, idx) => (
              <QuizCard
                key={idx}
                index={idx}
                question={q}
                value={answers[idx]}
                onChange={handleSelect}
                showAnswer={showAnswers}
              />
            ))}

            <div className="flex items-center gap-4">
              <button
                type="button"
                onClick={handleSubmit}
                className="inline-flex items-center gap-2 rounded-full bg-sky-600 px-6 py-3 text-sm font-semibold text-white shadow-md hover:bg-sky-700"
              >
                Submit Quiz
              </button>

              {score && (
                <div className="text-sm text-slate-600">Score: {score.correct} / {score.total}</div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
