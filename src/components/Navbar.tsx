import React from 'react';
import { Sparkles, Award, Search, BookOpen } from 'lucide-react';
import { UserProgress } from '../types';

interface NavbarProps {
  progress: UserProgress;
  onOpenAiMentor: () => void;
  onOpenCertificate: () => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  progress,
  onOpenAiMentor,
  onOpenCertificate,
  searchQuery,
  setSearchQuery
}) => {
  const completedCount = progress.completedModules.length;
  const progressPercent = Math.round((completedCount / 5) * 100);

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40 px-4 md:px-8 py-3.5 flex items-center justify-between gap-4">
      {/* Brand & Level Badge */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center text-white shadow-md shadow-indigo-200">
          <div className="w-4 h-4 bg-white rounded-full"></div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-extrabold text-lg tracking-tight italic text-slate-900">
              NEURAL<span className="text-indigo-600">ACADEMY</span>
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100">
              {progress.userLevel}
            </span>
          </div>
          <span className="text-[10px] text-slate-400 font-medium hidden sm:inline">
            Path: AI Engineering & Autonomous Systems
          </span>
        </div>
      </div>

      {/* Center Search Bar */}
      <div className="hidden lg:flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 w-80 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:bg-white transition-all">
        <Search className="w-4 h-4 text-slate-400" />
        <input
          type="text"
          placeholder="Search FlashAttention, MCP, vLLM..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="bg-transparent text-xs font-medium text-slate-800 focus:outline-none w-full placeholder:text-slate-400"
        />
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Progress Tracker Pill */}
        <div className="hidden sm:flex items-center gap-2 px-3.5 py-1.5 bg-slate-50 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700">
          <BookOpen className="w-4 h-4 text-indigo-600" />
          <span>{completedCount}/5 Modules</span>
          <div className="w-16 h-1.5 bg-slate-200 rounded-full overflow-hidden ml-1">
            <div
              className="h-full bg-indigo-600 transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
        </div>

        {/* AI Mentor Button */}
        <button
          onClick={onOpenAiMentor}
          className="flex items-center gap-2 px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl shadow-lg shadow-indigo-200 transition-all"
        >
          <Sparkles className="w-4 h-4" />
          <span className="hidden sm:inline">Ask AI Mentor</span>
        </button>

        {/* Certificate Button */}
        <button
          onClick={onOpenCertificate}
          className={`flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-xl transition-all border ${
            progressPercent === 100
              ? 'bg-amber-500 text-slate-950 border-amber-400 shadow-md shadow-amber-200'
              : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
          }`}
        >
          <Award className="w-4 h-4 text-amber-600" />
          <span className="hidden sm:inline">Certificate</span>
        </button>
      </div>
    </header>
  );
};
