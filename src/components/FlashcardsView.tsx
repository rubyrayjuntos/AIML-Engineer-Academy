import React, { useState } from 'react';
import { allFlashcards } from '../data/curriculumData';
import { Layers, RotateCcw, CheckCircle2, ChevronRight, ChevronLeft } from 'lucide-react';

interface FlashcardsViewProps {
  learnedFlashcards: string[];
  onToggleMastered: (id: string) => void;
}

export const FlashcardsView: React.FC<FlashcardsViewProps> = ({ learnedFlashcards, onToggleMastered }) => {
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [isFlipped, setIsFlipped] = useState<boolean>(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const categories = ['ALL', ...Array.from(new Set(allFlashcards.map(f => f.category)))];

  const filteredCards = selectedCategory === 'ALL'
    ? allFlashcards
    : allFlashcards.filter(f => f.category === selectedCategory);

  const currentCard = filteredCards[currentIndex] || filteredCards[0];
  const isMastered = learnedFlashcards.includes(currentCard.id);

  const handleNext = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => (prev + 1) % filteredCards.length);
  };

  const handlePrev = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => (prev - 1 + filteredCards.length) % filteredCards.length);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-50 text-amber-800 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
          <Layers className="w-3.5 h-3.5 text-amber-600" />
          Interactive Flashcard Mastery Engine
        </div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">
          Concept Flashcards ({learnedFlashcards.length} / {allFlashcards.length} Mastered)
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Review key definitions, mathematical formulations, and engineering principles.
        </p>

        {/* Category Filters */}
        <div className="flex flex-wrap gap-2 mt-6 pt-4 border-t border-slate-100">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => { setSelectedCategory(cat); setCurrentIndex(0); setIsFlipped(false); }}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
                selectedCategory === cat
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200'
                  : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Main Flashcard Card */}
      {currentCard && (
        <div className="max-w-2xl mx-auto space-y-6">
          <div
            onClick={() => setIsFlipped(!isFlipped)}
            className="cursor-pointer min-h-[320px] bg-white border border-slate-200 rounded-3xl p-8 shadow-sm hover:shadow-md transition-all flex flex-col justify-between relative group"
          >
            <div className="flex justify-between items-center mb-4">
              <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 font-mono">
                {currentCard.category}
              </span>
              <span className="text-xs font-mono font-bold text-slate-400">
                {currentIndex + 1} / {filteredCards.length}
              </span>
            </div>

            {/* Front vs Back Content */}
            <div className="my-auto text-center space-y-4">
              {!isFlipped ? (
                <div>
                  <h2 className="text-2xl md:text-3xl font-black text-slate-900 tracking-tight">
                    {currentCard.term}
                  </h2>
                  <p className="text-xs text-slate-400 mt-4 italic">
                    Click anywhere on the card to flip
                  </p>
                </div>
              ) : (
                <div className="space-y-4 text-left">
                  <p className="text-sm text-slate-800 leading-relaxed font-medium">
                    {currentCard.definition}
                  </p>

                  <div className="p-3 bg-slate-950 text-amber-300 rounded-2xl font-mono text-xs border border-slate-800">
                    <strong className="text-slate-400 font-sans text-[10px] uppercase block mb-1">Key Takeaway</strong>
                    <div>{currentCard.keyTakeaway}</div>
                  </div>
                </div>
              )}
            </div>

            {/* Bottom Footer */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-100 text-xs font-semibold text-slate-400">
              <span className="flex items-center gap-1">
                <RotateCcw className="w-3.5 h-3.5" /> Flip Card
              </span>
              <span>{isMastered ? '✓ Mastered' : 'Unmastered'}</span>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between gap-4">
            <button
              onClick={handlePrev}
              className="flex items-center gap-1.5 px-4 py-2.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 font-bold text-xs rounded-xl shadow-sm transition-all"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Previous</span>
            </button>

            <button
              onClick={() => onToggleMastered(currentCard.id)}
              className={`flex items-center gap-2 px-5 py-2.5 font-bold text-xs rounded-xl shadow-sm transition-all ${
                isMastered
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                  : 'bg-indigo-600 text-white hover:bg-indigo-500 shadow-md shadow-indigo-200'
              }`}
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>{isMastered ? 'Marked Mastered' : 'Mark as Mastered'}</span>
            </button>

            <button
              onClick={handleNext}
              className="flex items-center gap-1.5 px-4 py-2.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 font-bold text-xs rounded-xl shadow-sm transition-all"
            >
              <span>Next</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
