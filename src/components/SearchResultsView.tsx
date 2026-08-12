import React, { useMemo } from 'react';
import { modulesData, allFlashcards } from '../data/curriculumData';
import { Search, BookOpen, Layers, CheckSquare, FlaskConical, ArrowRight } from 'lucide-react';

export interface SearchHit {
  id: string;
  kind: 'module' | 'section' | 'flashcard' | 'quiz' | 'lab' | 'tool';
  title: string;
  subtitle: string;
  view: string;
}

export function buildSearchIndex(): SearchHit[] {
  const hits: SearchHit[] = [
    {
      id: 'tool-simulators',
      kind: 'tool',
      title: 'Systems & Architecture Simulators',
      subtitle: 'vLLM, ReAct, MCP, RAG vs FT, prompt-injection sandbox',
      view: 'simulators'
    },
    {
      id: 'tool-system-design',
      kind: 'tool',
      title: 'System Design Canvas',
      subtitle: 'Architecture blueprints and topology walkthroughs',
      view: 'system-design'
    },
    {
      id: 'tool-flashcards',
      kind: 'tool',
      title: 'Flashcard Mastery',
      subtitle: 'Concept definitions and takeaways',
      view: 'flashcards'
    },
    {
      id: 'tool-quizzes',
      kind: 'tool',
      title: 'Program Knowledge Checks',
      subtitle: 'Cross-module assessment',
      view: 'quizzes'
    }
  ];

  for (const module of modulesData) {
    hits.push({
      id: `module-${module.id}`,
      kind: 'module',
      title: module.title,
      subtitle: `${module.tag} · ${module.subtitle}`,
      view: `module-${module.id}`
    });

    hits.push({
      id: `lab-${module.lab.id}`,
      kind: 'lab',
      title: module.lab.title,
      subtitle: `${module.tag} lab · ${module.lab.workspacePath || module.lab.environment}`,
      view: `module-${module.id}`
    });

    module.sections.forEach((section, index) => {
      hits.push({
        id: `section-${module.id}-${index}`,
        kind: 'section',
        title: section.title,
        subtitle: `${module.tag} theory`,
        view: `module-${module.id}`
      });
    });

    module.quizzes.forEach(quiz => {
      hits.push({
        id: quiz.id,
        kind: 'quiz',
        title: quiz.question,
        subtitle: `${module.tag} · ${quiz.concept}`,
        view: `module-${module.id}`
      });
    });
  }

  for (const card of allFlashcards) {
    hits.push({
      id: card.id,
      kind: 'flashcard',
      title: card.term,
      subtitle: `${card.category} · ${card.keyTakeaway}`,
      view: 'flashcards'
    });
  }

  return hits;
}

const KIND_ICON = {
  module: BookOpen,
  section: BookOpen,
  flashcard: Layers,
  quiz: CheckSquare,
  lab: FlaskConical,
  tool: Search
} as const;

interface SearchResultsViewProps {
  query: string;
  onNavigate: (view: string) => void;
  onClear: () => void;
}

export const SearchResultsView: React.FC<SearchResultsViewProps> = ({ query, onNavigate, onClear }) => {
  const index = useMemo(() => buildSearchIndex(), []);
  const normalized = query.trim().toLowerCase();

  const results = useMemo(() => {
    if (!normalized) return [];
    return index
      .map(hit => {
        const haystack = `${hit.title} ${hit.subtitle}`.toLowerCase();
        const score = haystack.includes(normalized)
          ? 2
          : normalized.split(/\s+/).filter(Boolean).every(token => haystack.includes(token))
            ? 1
            : 0;
        return { hit, score };
      })
      .filter(row => row.score > 0)
      .sort((a, b) => b.score - a.score || a.hit.title.localeCompare(b.hit.title))
      .map(row => row.hit);
  }, [index, normalized]);

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
          <Search className="w-3.5 h-3.5" />
          Curriculum Search
        </div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">
          Results for “{query.trim()}”
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          {results.length} match{results.length === 1 ? '' : 'es'} across modules, labs, quizzes, flashcards, and tools.
        </p>
        <button
          onClick={onClear}
          className="mt-4 text-xs font-bold text-indigo-700 hover:text-indigo-500"
        >
          Clear search and return to dashboard
        </button>
      </div>

      {results.length === 0 ? (
        <div className="bg-slate-50 border border-slate-200 rounded-3xl p-8 text-sm text-slate-600">
          No matches. Try terms like <span className="font-mono">FlashAttention</span>, <span className="font-mono">MCP</span>, or <span className="font-mono">PagedAttention</span>.
        </div>
      ) : (
        <div className="space-y-3">
          {results.map(hit => {
            const Icon = KIND_ICON[hit.kind];
            return (
              <button
                key={hit.id}
                onClick={() => onNavigate(hit.view)}
                className="w-full text-left bg-white border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/40 rounded-2xl p-4 shadow-sm transition-all flex items-start gap-3"
              >
                <div className="w-9 h-9 rounded-xl bg-slate-900 text-indigo-300 flex items-center justify-center shrink-0">
                  <Icon className="w-4 h-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full">
                      {hit.kind}
                    </span>
                  </div>
                  <h2 className="text-sm font-bold text-slate-900 truncate">{hit.title}</h2>
                  <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{hit.subtitle}</p>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400 shrink-0 mt-2" />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
