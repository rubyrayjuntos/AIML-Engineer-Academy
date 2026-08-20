import React, { useMemo, useState } from 'react';
import { RefreshCw, Type } from 'lucide-react';
import { estimateTokens, fitsInContext, remainingOutputBudget } from '../../tokenizerBudget';

export const TokenizerBudgetSimulator: React.FC = () => {
  const [prompt, setPrompt] = useState(
    'Summarize the retention policy for customer records and cite the source document.'
  );
  const [maxContext, setMaxContext] = useState(8192);
  const [reservedOutput, setReservedOutput] = useState(512);
  const [charsPerToken, setCharsPerToken] = useState(4);

  const stats = useMemo(() => {
    const promptTokens = estimateTokens(prompt, charsPerToken);
    const remaining = remainingOutputBudget(promptTokens, maxContext);
    const fits = fitsInContext({ promptTokens, maxContext, reservedOutput });
    return { promptTokens, remaining, fits };
  }, [prompt, maxContext, reservedOutput, charsPerToken]);

  return (
    <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm my-6 space-y-6">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 pb-6 border-b border-slate-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-slate-100 text-slate-700 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
            <Type className="w-3.5 h-3.5" />
            Tokenizer / Context Budget
          </div>
          <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Prompt Tokens · Window · Reserved Output
          </h3>
          <p className="text-sm text-slate-500 mt-1 max-w-2xl">
            Teaching estimate at ~{charsPerToken} characters per token. This is not a real BPE/Unigram
            tokenizer and does not load a model vocabulary.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold uppercase tracking-wide text-amber-700 bg-amber-50 border border-amber-200 px-2 py-1 rounded-full whitespace-nowrap">
            Teaching estimate
          </span>
          <button
            type="button"
            onClick={() => {
              setPrompt('Summarize the retention policy for customer records and cite the source document.');
              setMaxContext(8192);
              setReservedOutput(512);
              setCharsPerToken(4);
            }}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-xl"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Reset
          </button>
        </div>
      </div>

      <label className="block text-sm">
        <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Prompt text</span>
        <textarea
          className="mt-2 w-full min-h-24 border border-slate-200 rounded-xl px-3 py-2 text-sm"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
      </label>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-50 p-6 rounded-2xl border border-slate-100">
        <label className="block text-sm">
          <div className="flex justify-between mb-2">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Max context</span>
            <span className="font-mono text-sm font-bold text-indigo-600">{maxContext}</span>
          </div>
          <input
            type="range"
            min={1024}
            max={128000}
            step={1024}
            value={maxContext}
            onChange={(e) => setMaxContext(Number(e.target.value))}
            className="w-full accent-indigo-600"
          />
        </label>
        <label className="block text-sm">
          <div className="flex justify-between mb-2">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Reserved output</span>
            <span className="font-mono text-sm font-bold text-indigo-600">{reservedOutput}</span>
          </div>
          <input
            type="range"
            min={64}
            max={4096}
            step={64}
            value={reservedOutput}
            onChange={(e) => setReservedOutput(Number(e.target.value))}
            className="w-full accent-indigo-600"
          />
        </label>
        <label className="block text-sm">
          <div className="flex justify-between mb-2">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Chars / token</span>
            <span className="font-mono text-sm font-bold text-indigo-600">{charsPerToken}</span>
          </div>
          <input
            type="range"
            min={3}
            max={6}
            step={1}
            value={charsPerToken}
            onChange={(e) => setCharsPerToken(Number(e.target.value))}
            className="w-full accent-indigo-600"
          />
        </label>
      </div>

      <div className="grid sm:grid-cols-3 gap-3">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Prompt tokens</span>
          <p className="mt-1 font-mono text-xl font-black text-slate-900">{stats.promptTokens}</p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Remaining budget</span>
          <p className="mt-1 font-mono text-xl font-black text-slate-900">{stats.remaining}</p>
        </div>
        <div className={`rounded-2xl border p-4 ${stats.fits ? 'border-emerald-200 bg-emerald-50' : 'border-rose-200 bg-rose-50'}`}>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Fits window?</span>
          <p className="mt-1 font-mono text-xl font-black text-slate-900">{stats.fits ? 'yes' : 'no'}</p>
        </div>
      </div>
    </div>
  );
};
