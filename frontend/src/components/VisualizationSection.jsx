import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

function VisualizationSection({ wordFrequency, keywords, sentenceImportance, performanceData }) {
  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Insights</p>
          <h3 className="mt-3 text-3xl font-semibold text-slate-950 dark:text-white">Realtime text analytics</h3>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-[2rem] border border-slate-200/70 bg-white/90 p-6 shadow-[0_15px_45px_rgba(15,23,42,0.08)] dark:border-slate-700/70 dark:bg-slate-950/80">
          <div className="mb-5 flex items-center justify-between">
            <h4 className="font-semibold text-slate-950 dark:text-white">Word frequency</h4>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-900 dark:text-slate-300">Top terms</span>
          </div>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={wordFrequency} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="word" tick={{ fill: '#64748b', fontSize: 12 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#0ea5e9" radius={[12, 12, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-[2rem] border border-slate-200/70 bg-white/90 p-6 shadow-[0_15px_45px_rgba(15,23,42,0.08)] dark:border-slate-700/70 dark:bg-slate-950/80">
          <div className="mb-5 flex items-center justify-between">
            <h4 className="font-semibold text-slate-950 dark:text-white">Keyword cloud</h4>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-900 dark:text-slate-300">AI tags</span>
          </div>
          <div className="flex flex-wrap gap-3">
            {keywords.length > 0 ? (
              keywords.map((keyword) => (
                <span key={keyword} className="rounded-full bg-sky-100 px-4 py-2 text-sm text-sky-700 dark:bg-cyan-500/15 dark:text-cyan-200">
                  {keyword}
                </span>
              ))
            ) : (
              <p className="text-sm text-slate-500 dark:text-slate-400">No keywords available yet.</p>
            )}
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="rounded-[2rem] border border-slate-200/70 bg-white/90 p-6 shadow-[0_15px_45px_rgba(15,23,42,0.08)] dark:border-slate-700/70 dark:bg-slate-950/80">
          <h4 className="font-semibold text-slate-950 dark:text-white">Sentence importance</h4>
          <div className="mt-5 h-[240px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={sentenceImportance} outerRadius="80%">
                <PolarGrid />
                <PolarAngleAxis dataKey="sentence" tick={{ fill: '#64748b', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} />
                <Radar dataKey="importance" fill="#6366f1" fillOpacity={0.3} stroke="#6366f1" />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-[2rem] border border-slate-200/70 bg-white/90 p-6 shadow-[0_15px_45px_rgba(15,23,42,0.08)] dark:border-slate-700/70 dark:bg-slate-950/80">
          <h4 className="font-semibold text-slate-950 dark:text-white">Model performance</h4>
          <div className="mt-5 h-[240px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={performanceData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="model" tick={{ fill: '#64748b', fontSize: 12 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="score" fill="#7c3aed" radius={[12, 12, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </section>
  );
}

export default VisualizationSection;
