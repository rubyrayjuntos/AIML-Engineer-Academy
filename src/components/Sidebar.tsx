import React from 'react';
import { modulesData } from '../data/curriculumData';
import { LayoutDashboard, Sliders, Network, Layers, CheckSquare, Cpu } from 'lucide-react';

interface SidebarProps {
  activeView: string;
  setActiveView: (view: string) => void;
  completedModules: number[];
}

export const Sidebar: React.FC<SidebarProps> = ({ activeView, setActiveView, completedModules }) => {
  return (
    <aside className="w-full md:w-64 bg-white border-r border-slate-200 shrink-0 md:h-[calc(100vh-61px)] md:sticky md:top-[61px] overflow-y-auto p-4 flex flex-col justify-between">
      <div className="space-y-6">
        {/* Main Navigation */}
        <div>
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-3 block mb-2">
            Main Portal
          </span>
          <nav className="space-y-1">
            <button
              onClick={() => setActiveView('overview')}
              className={`w-full flex items-center gap-3 px-3.5 py-3 rounded-xl text-xs font-semibold transition-all ${
                activeView === 'overview'
                  ? 'bg-indigo-50 text-indigo-700 font-bold'
                  : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <LayoutDashboard className="w-4 h-4 text-indigo-600" />
              <span>Dashboard</span>
            </button>
          </nav>
        </div>

        {/* Modules Section */}
        <div>
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-3 block mb-2">
            Learning Tracks
          </span>
          <nav className="space-y-1">
            {modulesData.map((m) => {
              const isDone = completedModules.includes(m.id);
              const isActive = activeView === `module-${m.id}`;

              return (
                <button
                  key={m.id}
                  onClick={() => setActiveView(`module-${m.id}`)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs transition-all ${
                    isActive
                      ? 'bg-indigo-50 text-indigo-700 font-bold'
                      : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900 font-medium'
                  }`}
                >
                  <div className="flex items-center gap-2.5 overflow-hidden">
                    <span className="font-mono text-[10px] text-slate-400 font-bold shrink-0">
                      0{m.id}
                    </span>
                    <span className="truncate">{m.title}</span>
                  </div>
                  {isDone && (
                    <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0"></span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Hands-On Tools & Simulators */}
        <div>
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-3 block mb-2">
            Compute & Practice Sandbox
          </span>
          <nav className="space-y-1">
            <button
              onClick={() => setActiveView('simulators')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs transition-all ${
                activeView === 'simulators'
                  ? 'bg-indigo-50 text-indigo-700 font-bold'
                  : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900 font-medium'
              }`}
            >
              <Sliders className="w-4 h-4 text-indigo-600" />
              <span>Simulators Hub</span>
            </button>

            <button
              onClick={() => setActiveView('system-design')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs transition-all ${
                activeView === 'system-design'
                  ? 'bg-indigo-50 text-indigo-700 font-bold'
                  : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900 font-medium'
              }`}
            >
              <Network className="w-4 h-4 text-violet-600" />
              <span>System Design</span>
            </button>

            <button
              onClick={() => setActiveView('flashcards')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs transition-all ${
                activeView === 'flashcards'
                  ? 'bg-indigo-50 text-indigo-700 font-bold'
                  : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900 font-medium'
              }`}
            >
              <Layers className="w-4 h-4 text-amber-600" />
              <span>Flashcard Mastery</span>
            </button>

            <button
              onClick={() => setActiveView('quizzes')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs transition-all ${
                activeView === 'quizzes'
                  ? 'bg-indigo-50 text-indigo-700 font-bold'
                  : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900 font-medium'
              }`}
            >
              <CheckSquare className="w-4 h-4 text-emerald-600" />
              <span>Knowledge Checks</span>
            </button>
          </nav>
        </div>
      </div>

      {/* Available Compute Resources Widget from Sleek Theme */}
      <div className="space-y-4 pt-4">
        <div className="bg-indigo-600 rounded-2xl p-4 text-white shadow-md shadow-indigo-100">
          <div className="flex items-center justify-between mb-1">
            <p className="text-[10px] font-semibold uppercase tracking-wider opacity-80">Available Resources</p>
            <Cpu className="w-3.5 h-3.5 opacity-80" />
          </div>
          <p className="text-base font-bold">142 GPU Hours</p>
          <div className="mt-2.5 w-full bg-indigo-400/50 h-1.5 rounded-full overflow-hidden">
            <div className="bg-white h-full rounded-full w-3/4"></div>
          </div>
        </div>

        {/* Footer Status */}
        <div className="pt-2 border-t border-slate-100 text-[11px] text-slate-400 font-mono flex items-center justify-between px-1">
          <span>AI STUDIO V3.1</span>
          <span className="text-emerald-600 font-bold flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block animate-pulse"></span>
            ONLINE
          </span>
        </div>
      </div>
    </aside>
  );
};
