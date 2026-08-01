import React, { useState } from 'react';
import { modulesData } from '../data/curriculumData';
import { CheckSquare, CheckCircle2 } from 'lucide-react';

export const QuizView: React.FC = () => {
  const allQuizzes = modulesData.flatMap(m => m.quizzes);
  const [userAnswers, setUserAnswers] = useState<Record<string, number>>({});
  const [isSubmitted, setIsSubmitted] = useState<boolean>(false);

  const totalQuestions = allQuizzes.length;
  const correctCount = Object.entries(userAnswers).filter(
    ([qId, idx]) => allQuizzes.find(q => q.id === qId)?.answerIndex === idx
  ).length;

  const scorePercent = Math.round((correctCount / totalQuestions) * 100);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-50 text-emerald-800 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
          <CheckSquare className="w-3.5 h-3.5 text-emerald-600" />
          Program Knowledge Assessment Engine
        </div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">
          Comprehensive Program Knowledge Checks
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Validate your mastery across all 5 curriculum modules.
        </p>

        {isSubmitted && (
          <div className="mt-4 p-4 bg-slate-950 text-white rounded-2xl flex items-center justify-between border border-slate-800">
            <div>
              <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Assessment Score</span>
              <div className="text-2xl font-black">{scorePercent}% Score ({correctCount}/{totalQuestions} Correct)</div>
            </div>
            <button
              onClick={() => { setIsSubmitted(false); setUserAnswers({}); }}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-bold rounded-xl border border-slate-700"
            >
              Reset Quiz
            </button>
          </div>
        )}
      </div>

      {/* Questions List */}
      <div className="space-y-6">
        {allQuizzes.map((q, idx) => {
          const selectedOpt = userAnswers[q.id];
          const isCorrect = selectedOpt === q.answerIndex;

          return (
            <div key={q.id} className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm space-y-4">
              <div className="flex justify-between items-start gap-2">
                <h3 className="text-sm font-bold text-slate-900">
                  Q{idx + 1}: {q.question}
                </h3>
                <span className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700">
                  {q.concept}
                </span>
              </div>

              <div className="space-y-2">
                {q.options.map((opt, optIdx) => {
                  const isSelected = selectedOpt === optIdx;

                  return (
                    <button
                      key={optIdx}
                      onClick={() => setUserAnswers(prev => ({ ...prev, [q.id]: optIdx }))}
                      className={`w-full text-left p-3.5 rounded-xl text-xs font-medium transition-all border ${
                        isSelected
                          ? 'bg-indigo-600 text-white border-indigo-600 font-bold shadow-md shadow-indigo-200'
                          : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                      }`}
                    >
                      {opt}
                    </button>
                  );
                })}
              </div>

              {isSubmitted && selectedOpt !== undefined && (
                <div className={`p-3.5 rounded-2xl text-xs border ${isCorrect ? 'bg-emerald-50 text-emerald-900 border-emerald-200' : 'bg-rose-50 text-rose-900 border-rose-200'}`}>
                  <strong className="block font-bold mb-1">
                    {isCorrect ? '✓ Correct Answer' : '✗ Incorrect'}
                  </strong>
                  <p>{q.explanation}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {!isSubmitted && (
        <div className="flex justify-end pt-4">
          <button
            onClick={() => setIsSubmitted(true)}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-indigo-200 transition-all flex items-center gap-2"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Submit Full Program Assessment</span>
          </button>
        </div>
      )}
    </div>
  );
};
