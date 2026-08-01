import React, { useState, useEffect } from 'react';
import { modulesData } from './data/curriculumData';
import { UserProgress } from './types';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { OverviewView } from './components/OverviewView';
import { ModuleView } from './components/ModuleView';
import { VllmSimulator } from './components/Simulators/VllmSimulator';
import { ReactAgentSimulator } from './components/Simulators/ReactAgentSimulator';
import { McpSandbox } from './components/Simulators/McpSandbox';
import { RagVsFtEngine } from './components/Simulators/RagVsFtEngine';
import { PromptInjectionSandbox } from './components/Simulators/PromptInjectionSandbox';
import { SystemDesignCanvas } from './components/SystemDesignCanvas';
import { FlashcardsView } from './components/FlashcardsView';
import { QuizView } from './components/QuizView';
import { AiMentorModal } from './components/AiMentorModal';
import { CertificateModal } from './components/CertificateModal';
import { Sliders } from 'lucide-react';

export default function App() {
  const [activeView, setActiveView] = useState<string>('overview');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isAiMentorOpen, setIsAiMentorOpen] = useState<boolean>(false);
  const [isCertificateOpen, setIsCertificateOpen] = useState<boolean>(false);

  // User Progress Persistence
  const [progress, setProgress] = useState<UserProgress>(() => {
    const saved = localStorage.getItem('ai_academy_progress');
    if (saved) {
      try { return JSON.parse(saved); } catch {}
    }
    return {
      completedModules: [1],
      labCompletions: {},
      quizScores: {},
      learnedFlashcards: ['fc1_1', 'fc2_1', 'fc3_1', 'fc4_1'],
      codeRunHistory: 5,
      certificateGranted: false,
      userLevel: 'AI Engineer'
    };
  });

  useEffect(() => {
    localStorage.setItem('ai_academy_progress', JSON.stringify(progress));
  }, [progress]);

  // Update user level based on completed modules
  useEffect(() => {
    const count = progress.completedModules.length;
    let level: UserProgress['userLevel'] = 'Junior ML Dev';
    if (count >= 5) level = 'Principal AI Engineer';
    else if (count >= 3) level = 'Senior Systems Architect';
    else if (count >= 1) level = 'AI Engineer';

    if (level !== progress.userLevel) {
      setProgress(prev => ({ ...prev, userLevel: level }));
    }
  }, [progress.completedModules]);

  const toggleModuleComplete = (id: number) => {
    setProgress(prev => {
      const exists = prev.completedModules.includes(id);
      const nextCompleted = exists
        ? prev.completedModules.filter(mId => mId !== id)
        : [...prev.completedModules, id];
      return { ...prev, completedModules: nextCompleted };
    });
  };

  const handleCodeRunCount = () => {
    setProgress(prev => ({ ...prev, codeRunHistory: prev.codeRunHistory + 1 }));
  };

  const toggleMasteredFlashcard = (id: string) => {
    setProgress(prev => {
      const exists = prev.learnedFlashcards.includes(id);
      const nextCards = exists
        ? prev.learnedFlashcards.filter(fId => fId !== id)
        : [...prev.learnedFlashcards, id];
      return { ...prev, learnedFlashcards: nextCards };
    });
  };

  // Determine active view content
  const currentModuleId = activeView.startsWith('module-')
    ? parseInt(activeView.replace('module-', ''), 10)
    : null;

  const currentModule = currentModuleId
    ? modulesData.find(m => m.id === currentModuleId)
    : null;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex flex-col">
      {/* Main Navbar */}
      <Navbar
        progress={progress}
        onOpenAiMentor={() => setIsAiMentorOpen(true)}
        onOpenCertificate={() => setIsCertificateOpen(true)}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
      />

      {/* Body Area */}
      <div className="flex-1 flex flex-col md:flex-row">
        {/* Navigation Sidebar */}
        <Sidebar
          activeView={activeView}
          setActiveView={setActiveView}
          completedModules={progress.completedModules}
        />

        {/* Main Content View Mount */}
        <main className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full">
          {activeView === 'overview' && (
            <OverviewView
              progress={progress}
              onSelectModule={(id) => setActiveView(`module-${id}`)}
              onOpenSimulators={() => setActiveView('simulators')}
            />
          )}

          {currentModule && (
            <ModuleView
              module={currentModule}
              progress={progress}
              onToggleComplete={toggleModuleComplete}
              onCodeRun={handleCodeRunCount}
              onNavigateNext={
                currentModule.id < 5 ? () => setActiveView(`module-${currentModule.id + 1}`) : undefined
              }
              onNavigatePrev={
                currentModule.id > 1 ? () => setActiveView(`module-${currentModule.id - 1}`) : undefined
              }
            />
          )}

          {activeView === 'simulators' && (
            <div className="space-y-8">
              <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
                  <Sliders className="w-3.5 h-3.5 text-indigo-600" />
                  Interactive Engineering Simulators Hub
                </div>
                <h1 className="text-3xl font-black text-slate-900 tracking-tight">
                  Systems & Architecture Simulators
                </h1>
                <p className="text-sm text-slate-500 mt-1">
                  Test vLLM PagedAttention, ReAct cognitive loops, Model Context Protocol (MCP), RAG vs Fine-tuning matrix, and Indirect Prompt Injection firewalls.
                </p>
              </div>

              <VllmSimulator />
              <ReactAgentSimulator />
              <McpSandbox />
              <RagVsFtEngine />
              <PromptInjectionSandbox />
            </div>
          )}

          {activeView === 'system-design' && <SystemDesignCanvas />}

          {activeView === 'flashcards' && (
            <FlashcardsView
              learnedFlashcards={progress.learnedFlashcards}
              onToggleMastered={toggleMasteredFlashcard}
            />
          )}

          {activeView === 'quizzes' && <QuizView />}
        </main>
      </div>

      {/* AI Mentor Dialog Modal */}
      <AiMentorModal
        isOpen={isAiMentorOpen}
        onClose={() => setIsAiMentorOpen(false)}
        currentContext={currentModule ? currentModule.title : 'General AI Engineering'}
      />

      {/* Certificate Modal */}
      <CertificateModal
        isOpen={isCertificateOpen}
        onClose={() => setIsCertificateOpen(false)}
        userLevel={progress.userLevel}
      />
    </div>
  );
}
