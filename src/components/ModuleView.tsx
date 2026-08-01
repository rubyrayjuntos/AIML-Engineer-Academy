import React, { useState } from 'react';
import { ModuleData, UserProgress } from '../types';
import { CodeBlock } from './CodeBlock';
import { BookOpen, Code2, FlaskConical, CheckSquare, CheckCircle2, Play, ArrowRight, ArrowLeft } from 'lucide-react';

interface ModuleViewProps {
  module: ModuleData;
  progress: UserProgress;
  onToggleComplete: (id: number) => void;
  onCodeRun: () => void;
  onNavigateNext?: () => void;
  onNavigatePrev?: () => void;
}

export const ModuleView: React.FC<ModuleViewProps> = ({
  module,
  progress,
  onToggleComplete,
  onCodeRun,
  onNavigateNext,
  onNavigatePrev
}) => {
  const [activeTab, setActiveTab] = useState<'theory' | 'code' | 'lab' | 'quiz'>('theory');
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({});
  const [showQuizResults, setShowQuizResults] = useState<boolean>(false);
  const [labOutput, setLabOutput] = useState<string | null>(null);
  const [isLabRunning, setIsLabRunning] = useState<boolean>(false);

  const isCompleted = progress.completedModules.length ? progress.completedModules.includes(module.id) : false;

  const handleSelectQuizOption = (quizId: string, optionIdx: number) => {
    setSelectedAnswers(prev => ({ ...prev, [quizId]: optionIdx }));
  };

  const handleRunLab = async () => {
    setIsLabRunning(true);
    setLabOutput(null);
    try {
      const res = await fetch('/api/simulate-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: module.lab.starterCode.code,
          language: module.lab.starterCode.language,
          title: module.lab.title
        })
      });
      const data = await res.json();
      setLabOutput(data.output);
      onCodeRun();
    } catch {
      setLabOutput('[ERROR] Lab execution failed.');
    } finally {
      setIsLabRunning(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Module Header */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4 pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 font-mono">
                {module.tag}
              </span>
              <span className="text-xs text-slate-400 font-mono">Est. {module.estimatedHours} Hours</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-black text-slate-900 tracking-tight">
              {module.title}
            </h1>
            <p className="text-sm md:text-base text-slate-500 mt-1 font-medium">
              {module.subtitle}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => onToggleComplete(module.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold text-xs transition-all ${
                isCompleted
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-sm'
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-200'
              }`}
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>{isCompleted ? 'Module Completed' : 'Mark as Complete'}</span>
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-100">
          <button
            onClick={() => setActiveTab('theory')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'theory' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200' : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" /> Core Theory ({module.sections.length})
          </button>

          <button
            onClick={() => setActiveTab('code')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'code' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200' : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Code2 className="w-3.5 h-3.5" /> Reference Implementations ({module.codeExamples.length})
          </button>

          <button
            onClick={() => setActiveTab('lab')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'lab' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200' : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <FlaskConical className="w-3.5 h-3.5" /> Hands-on Lab
          </button>

          <button
            onClick={() => setActiveTab('quiz')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'quiz' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200' : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <CheckSquare className="w-3.5 h-3.5" /> Knowledge Check ({module.quizzes.length})
          </button>
        </div>
      </div>

      {/* Tab Content Rendering */}
      {activeTab === 'theory' && (
        <div className="space-y-8">
          {module.sections.map((sec, i) => (
            <div key={i} className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm space-y-4">
              <h2 className="text-xl font-extrabold text-slate-900 border-b border-slate-100 pb-3">
                {sec.title}
              </h2>

              <div className="prose prose-slate max-w-none text-xs md:text-sm text-slate-700 leading-relaxed space-y-3 whitespace-pre-line">
                {sec.content}
              </div>

              {sec.keyFormula && (
                <div className="p-4 bg-slate-950 text-indigo-300 rounded-2xl font-mono text-xs border border-slate-800">
                  <span className="text-slate-400 font-sans font-bold text-[10px] uppercase block mb-1">Mathematical Formula</span>
                  <div>{sec.keyFormula}</div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {activeTab === 'code' && (
        <div className="space-y-6">
          {module.codeExamples.map((ex) => (
            <div key={ex.id} className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm">
              <h3 className="text-lg font-bold text-slate-900 mb-1">{ex.title}</h3>
              <p className="text-xs text-slate-500 mb-4">{ex.explanation}</p>
              <CodeBlock example={ex} onCodeRun={onCodeRun} />
            </div>
          ))}
        </div>
      )}

      {activeTab === 'lab' && (
        <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 font-mono">
                Environment: {module.lab.environment}
              </span>
              <h2 className="text-2xl font-extrabold text-slate-900 mt-2">🧪 {module.lab.title}</h2>
            </div>

            <button
              onClick={handleRunLab}
              disabled={isLabRunning}
              className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl shadow-md transition-all flex items-center gap-2 self-start"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>{isLabRunning ? 'Executing Lab...' : 'Execute Lab Sandbox'}</span>
            </button>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Lab Execution Tasks:</h4>
            <ul className="space-y-2">
              {module.lab.instructions.map((inst, idx) => (
                <li key={idx} className="flex items-start gap-3 p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs font-medium text-slate-700">
                  <span className="font-mono font-bold text-indigo-600">0{idx + 1}.</span>
                  <span>{inst}</span>
                </li>
              ))}
            </ul>
          </div>

          <CodeBlock example={module.lab.starterCode} onCodeRun={onCodeRun} />

          {labOutput && (
            <div className="p-4 bg-slate-950 text-emerald-400 font-mono text-xs rounded-2xl border border-slate-800">
              <span className="text-slate-400 font-sans font-bold text-[10px] uppercase block mb-1">Lab Validation Output</span>
              <pre className="whitespace-pre-wrap">{labOutput}</pre>
            </div>
          )}
        </div>
      )}

      {activeTab === 'quiz' && (
        <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm space-y-8">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Module Knowledge Check</h2>
              <p className="text-xs text-slate-500">Test your mastery of key architectural concepts.</p>
            </div>

            <button
              onClick={() => setShowQuizResults(true)}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-md shadow-indigo-200 transition-all"
            >
              Submit & Check Answers
            </button>
          </div>

          <div className="space-y-6">
            {module.quizzes.map((q, idx) => {
              const selectedOpt = selectedAnswers[q.id];
              const isCorrect = selectedOpt === q.answerIndex;

              return (
                <div key={q.id} className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-4">
                  <div className="flex justify-between items-start gap-2">
                    <h3 className="text-sm font-bold text-slate-900">
                      Q0{idx + 1}: {q.question}
                    </h3>
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-800">
                      {q.concept}
                    </span>
                  </div>

                  <div className="space-y-2">
                    {q.options.map((opt, optIdx) => {
                      const isSelected = selectedOpt === optIdx;

                      return (
                        <button
                          key={optIdx}
                          onClick={() => handleSelectQuizOption(q.id, optIdx)}
                          className={`w-full text-left p-3 rounded-xl text-xs font-medium transition-all border ${
                            isSelected
                              ? 'bg-indigo-600 text-white border-indigo-600 font-bold'
                              : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                          }`}
                        >
                          {opt}
                        </button>
                      );
                    })}
                  </div>

                  {showQuizResults && selectedOpt !== undefined && (
                    <div className={`p-3 rounded-xl text-xs border ${isCorrect ? 'bg-emerald-50 text-emerald-900 border-emerald-200' : 'bg-rose-50 text-rose-900 border-rose-200'}`}>
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
        </div>
      )}

      {/* Module Footer Controls */}
      <div className="flex justify-between items-center pt-4 border-t border-slate-200">
        <button
          onClick={onNavigatePrev}
          disabled={!onNavigatePrev}
          className="flex items-center gap-2 px-4 py-2.5 text-xs font-bold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 disabled:opacity-40 rounded-xl transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Previous Module</span>
        </button>

        <button
          onClick={onNavigateNext}
          disabled={!onNavigateNext}
          className="flex items-center gap-2 px-4 py-2.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 rounded-xl shadow-md shadow-indigo-200 transition-all"
        >
          <span>Next Module</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
