import React, { useState, useEffect, useCallback } from 'react';
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
import { DiffusionSimulator } from './components/Simulators/DiffusionSimulator';
import { SystemDesignCanvas } from './components/SystemDesignCanvas';
import { FlashcardsView } from './components/FlashcardsView';
import { QuizView } from './components/QuizView';
import { AiMentorModal } from './components/AiMentorModal';
import { CertificateModal } from './components/CertificateModal';
import { SearchResultsView } from './components/SearchResultsView';
import { Sliders } from 'lucide-react';

const defaultProgress = (): UserProgress => ({
  completedModules: [],
  labCompletions: {},
  quizScores: {},
  learnedFlashcards: [],
  codeRunHistory: 0,
  certificateGranted: false,
  userLevel: 'Junior ML Dev'
});

export default function App() {
  const [activeView, setActiveView] = useState<string>('overview');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isAiMentorOpen, setIsAiMentorOpen] = useState<boolean>(false);
  const [isCertificateOpen, setIsCertificateOpen] = useState<boolean>(false);

  const [progress, setProgress] = useState<UserProgress>(() => {
    const saved = localStorage.getItem('ai_academy_progress');
    if (saved) {
      try {
        return { ...defaultProgress(), ...JSON.parse(saved) };
      } catch {
        /* ignore corrupt localStorage */
      }
    }
    return defaultProgress();
  });

  useEffect(() => {
    localStorage.setItem('ai_academy_progress', JSON.stringify(progress));
  }, [progress]);

  useEffect(() => {
    const count = progress.completedModules.length;
    let level: UserProgress['userLevel'] = 'Junior ML Dev';
    if (count >= 5) level = 'Principal AI Engineer';
    else if (count >= 3) level = 'Senior Systems Architect';
    else if (count >= 1) level = 'AI Engineer';

    if (level !== progress.userLevel) {
      setProgress(prev => ({ ...prev, userLevel: level }));
    }
  }, [progress.completedModules, progress.userLevel]);

  const toggleModuleComplete = (id: number) => {
    setProgress(prev => {
      const exists = prev.completedModules.includes(id);
      const nextCompleted = exists
        ? prev.completedModules.filter(mId => mId !== id)
        : [...prev.completedModules, id];
      return { ...prev, completedModules: nextCompleted, certificateGranted: false };
    });
  };

  const handleCodeRunCount = () => {
    setProgress(prev => ({ ...prev, codeRunHistory: prev.codeRunHistory + 1 }));
  };

  const recordQuizScore = useCallback((moduleId: number, scorePercent: number) => {
    setProgress(prev => ({
      ...prev,
      quizScores: { ...prev.quizScores, [String(moduleId)]: scorePercent },
      certificateGranted: false
    }));
  }, []);

  const recordProgramQuizScore = useCallback((scorePercent: number) => {
    setProgress(prev => ({
      ...prev,
      quizScores: { ...prev.quizScores, program: scorePercent },
      certificateGranted: false
    }));
  }, []);

  const confirmLabEvidence = useCallback((labId: string) => {
    setProgress(prev => ({
      ...prev,
      labCompletions: { ...prev.labCompletions, [labId]: true },
      certificateGranted: false
    }));
  }, []);

  const grantCertificate = useCallback(() => {
    setProgress(prev => ({ ...prev, certificateGranted: true }));
  }, []);

  const toggleMasteredFlashcard = (id: string) => {
    setProgress(prev => {
      const exists = prev.learnedFlashcards.includes(id);
      const nextCards = exists
        ? prev.learnedFlashcards.filter(fId => fId !== id)
        : [...prev.learnedFlashcards, id];
      return { ...prev, learnedFlashcards: nextCards };
    });
  };

  const currentModuleId = activeView.startsWith('module-')
    ? parseInt(activeView.replace('module-', ''), 10)
    : null;

  const currentModule = currentModuleId
    ? modulesData.find(m => m.id === currentModuleId)
    : null;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex flex-col">
      <Navbar
        progress={progress}
        onOpenAiMentor={() => setIsAiMentorOpen(true)}
        onOpenCertificate={() => setIsCertificateOpen(true)}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
      />

      <div className="flex-1 flex flex-col md:flex-row">
        <Sidebar
          activeView={activeView}
          setActiveView={setActiveView}
          progress={progress}
        />

        <main className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full">
          {searchQuery.trim() ? (
            <SearchResultsView
              query={searchQuery}
              onNavigate={(view) => {
                setActiveView(view);
                setSearchQuery('');
              }}
              onClear={() => {
                setSearchQuery('');
                setActiveView('overview');
              }}
            />
          ) : (
            <>
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
              onRecordQuizScore={recordQuizScore}
              onConfirmLabEvidence={confirmLabEvidence}
              onNavigateNext={
                currentModule.id < modulesData.length
                  ? () => setActiveView(`module-${currentModule.id + 1}`)
                  : undefined
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
                  Test vLLM PagedAttention, diffusion forward noising, ReAct cognitive loops, Model Context Protocol (MCP), RAG vs Fine-tuning matrix, and Indirect Prompt Injection firewalls.
                </p>
              </div>

              <VllmSimulator />
              <DiffusionSimulator />
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

          {activeView === 'quizzes' && <QuizView onRecordProgramScore={recordProgramQuizScore} />}
            </>
          )}
        </main>
      </div>

      <AiMentorModal
        isOpen={isAiMentorOpen}
        onClose={() => setIsAiMentorOpen(false)}
        currentContext={currentModule ? currentModule.title : 'General AI Engineering'}
      />

      <CertificateModal
        isOpen={isCertificateOpen}
        onClose={() => setIsCertificateOpen(false)}
        progress={progress}
        onGrantCertificate={grantCertificate}
      />
    </div>
  );
}
