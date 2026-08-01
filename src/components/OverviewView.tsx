import React from 'react';
import { modulesData } from '../data/curriculumData';
import { UserProgress } from '../types';
import { Rocket, Cpu, Sliders, Play, CheckCircle2, Award, Zap, Flame, Code2, HelpCircle } from 'lucide-react';

interface OverviewViewProps {
  progress: UserProgress;
  onSelectModule: (id: number) => void;
  onOpenSimulators: () => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({ progress, onSelectModule, onOpenSimulators }) => {
  const completedCount = progress.completedModules.length;

  return (
    <div className="space-y-8">
      {/* Hero Banner with Sleek Interface aesthetic */}
      <div className="bg-white border border-slate-200 rounded-3xl p-8 md:p-10 shadow-sm relative overflow-hidden">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
          <div className="max-w-2xl space-y-3">
            <span className="inline-block px-3 py-1 bg-emerald-100 text-emerald-700 rounded-lg text-xs font-bold uppercase tracking-wider">
              Advanced Level
            </span>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-slate-900">
              Scaling Autonomous AI Engineering Architectures
            </h1>
            <p className="text-slate-500 text-sm leading-relaxed">
              Mastering Chinchilla laws, FlashAttention-3 GPU kernels, DeepSeek MLA, PagedAttention vLLM, Anthropic MCP, and type-safe agentic orchestration.
            </p>

            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={() => onSelectModule(1)}
                className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-indigo-200 transition-all flex items-center gap-2"
              >
                <Play className="w-4 h-4 fill-current" />
                <span>{completedCount > 0 ? 'Continue Lesson' : 'Start Module 01'}</span>
              </button>

              <button
                onClick={onOpenSimulators}
                className="px-5 py-3 bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 font-bold text-xs rounded-xl transition-all flex items-center gap-2"
              >
                <Sliders className="w-4 h-4 text-indigo-600" />
                <span>Launch Compute Sandbox</span>
              </button>
            </div>
          </div>

          {/* Quick Stats & Streak Panel from Sleek Theme */}
          <div className="w-full lg:w-72 bg-slate-50 p-5 rounded-2xl border border-slate-200 space-y-4 shrink-0">
            <div className="flex justify-between items-center pb-3 border-b border-slate-200">
              <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                <Flame className="w-4 h-4 text-amber-500" /> Weekly Streak
              </span>
              <span className="text-2xl font-black text-slate-900">4 <span className="text-xs font-normal text-slate-500">days</span></span>
            </div>
            <div className="flex justify-between gap-1">
              <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center text-[10px] text-white font-bold">M</div>
              <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center text-[10px] text-white font-bold">T</div>
              <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center text-[10px] text-white font-bold">W</div>
              <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center text-[10px] text-white font-bold">T</div>
              <div className="w-7 h-7 rounded-lg bg-slate-200 flex items-center justify-center text-[10px] text-slate-400 font-bold">F</div>
              <div className="w-7 h-7 rounded-lg bg-slate-200 flex items-center justify-center text-[10px] text-slate-400 font-bold">S</div>
              <div className="w-7 h-7 rounded-lg bg-slate-200 flex items-center justify-center text-[10px] text-slate-400 font-bold">S</div>
            </div>
          </div>
        </div>
      </div>

      {/* Program Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <div className="flex justify-between items-center text-slate-400 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider">Curriculum Progress</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-black text-slate-900">{completedCount} / 5 Modules</div>
          <div className="text-[11px] text-slate-500 mt-1">{Math.round((completedCount / 5) * 100)}% Complete</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <div className="flex justify-between items-center text-slate-400 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider">Code Simulations</span>
            <Cpu className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">{progress.codeRunHistory} Executions</div>
          <div className="text-[11px] text-slate-500 mt-1">Compute Sandbox Runs</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <div className="flex justify-between items-center text-slate-400 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider">Mastered Concepts</span>
            <Zap className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-black text-slate-900">{progress.learnedFlashcards.length} Flashcards</div>
          <div className="text-[11px] text-slate-500 mt-1">FlashAttention-3, MLA, MCP, vLLM</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
          <div className="flex justify-between items-center text-slate-400 mb-1">
            <span className="text-xs font-bold uppercase tracking-wider">Mastery Certificate</span>
            <Award className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">
            {completedCount === 5 ? 'Unlocked' : 'In Progress'}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            {completedCount === 5 ? 'Ready to Claim' : `${5 - completedCount} modules remaining`}
          </div>
        </div>
      </div>

      {/* Quick Access Labs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          onClick={onOpenSimulators}
          className="bg-white p-5 rounded-2xl border border-slate-200 hover:border-indigo-300 transition-all cursor-pointer flex items-center gap-4 shadow-sm"
        >
          <div className="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center shrink-0">
            <Code2 className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-800">Compute Lab</p>
            <p className="text-xs text-slate-500">vLLM PagedAttention & ReAct Agent Simulator</p>
          </div>
        </div>

        <div
          onClick={() => onSelectModule(2)}
          className="bg-white p-5 rounded-2xl border border-slate-200 hover:border-indigo-300 transition-all cursor-pointer flex items-center gap-4 shadow-sm"
        >
          <div className="w-12 h-12 rounded-xl bg-orange-100 text-orange-600 flex items-center justify-center shrink-0">
            <HelpCircle className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-800">Interactive Quiz</p>
            <p className="text-xs text-slate-500">DeepSeek MLA & KV Cache Compression</p>
          </div>
        </div>
      </div>

      {/* Module Roadmap Grid */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Training Modules Roadmap</h2>
            <p className="text-xs text-slate-500">Master production-grade AI engineering step by step.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modulesData.map((m) => {
            const isCompleted = progress.completedModules.includes(m.id);

            return (
              <div
                key={m.id}
                onClick={() => onSelectModule(m.id)}
                className={`bg-white border rounded-3xl p-6 shadow-sm hover:shadow-md transition-all cursor-pointer flex flex-col justify-between group ${
                  isCompleted ? 'border-emerald-300 bg-emerald-50/20' : 'border-slate-200 hover:border-indigo-300'
                }`}
              >
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 font-mono">
                      {m.tag}
                    </span>
                    {isCompleted ? (
                      <span className="px-2.5 py-0.5 bg-emerald-100 text-emerald-700 text-[10px] font-bold rounded-full flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> Completed
                      </span>
                    ) : (
                      <span className="text-xs text-slate-400 font-mono">{m.estimatedHours} Hours</span>
                    )}
                  </div>

                  <h3 className="text-lg font-bold text-slate-900 group-hover:text-indigo-600 transition-colors mb-1">
                    {m.title}
                  </h3>
                  <p className="text-xs text-slate-500 line-clamp-2 mb-4 leading-relaxed">
                    {m.subtitle}
                  </p>

                  <div className="space-y-1.5 mb-6">
                    {m.objectives.slice(0, 2).map((obj, i) => (
                      <div key={i} className="flex items-center gap-2 text-[11px] text-slate-600">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-600 shrink-0"></span>
                        <span className="truncate">{obj}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-xs font-bold text-indigo-600 group-hover:text-indigo-700">
                  <span>Explore Module</span>
                  <span className="text-base group-hover:translate-x-1 transition-transform">→</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
