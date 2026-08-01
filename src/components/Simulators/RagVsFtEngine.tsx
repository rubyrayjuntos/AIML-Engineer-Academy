import React, { useState } from 'react';
import { Database, Sparkles, Scale, CheckCircle2 } from 'lucide-react';

export const RagVsFtEngine: React.FC = () => {
  const [dataVolatility, setDataVolatility] = useState<'high' | 'static'>('high');
  const [customStyle, setCustomStyle] = useState<boolean>(false);
  const [hallucinationTolerance, setHallucinationTolerance] = useState<'strict' | 'flexible'>('strict');

  // Recommendation logic
  let recommendation: 'RAG' | 'Fine-Tuning' | 'Hybrid (RAG + Fine-Tuning)' = 'RAG';
  let scoreRAG = 0;
  let scoreFT = 0;

  if (dataVolatility === 'high') scoreRAG += 40; else scoreFT += 20;
  if (customStyle) scoreFT += 40; else scoreRAG += 10;
  if (hallucinationTolerance === 'strict') scoreRAG += 30; else scoreFT += 10;

  if (scoreRAG > 50 && scoreFT > 30) {
    recommendation = 'Hybrid (RAG + Fine-Tuning)';
  } else if (scoreRAG >= scoreFT) {
    recommendation = 'RAG';
  } else {
    recommendation = 'Fine-Tuning';
  }

  return (
    <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm my-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-6 border-b border-slate-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-50 text-amber-800 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
            <Scale className="w-3.5 h-3.5 text-amber-600" />
            RAG vs. Fine-Tuning Architectural Matrix
          </div>
          <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Knowledge Strategy & ROI Calculator
          </h3>
          <p className="text-sm text-slate-500 mt-1">
            Evaluate factual volatility, hallucination constraints, and training budgets to select the optimal strategy.
          </p>
        </div>
      </div>

      {/* Decision Controls */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 bg-slate-50 p-6 rounded-2xl border border-slate-100">
        {/* Data Volatility */}
        <div>
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-2">
            Data Update Frequency
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setDataVolatility('high')}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                dataVolatility === 'high' ? 'bg-amber-600 text-white border-amber-600' : 'bg-white text-slate-700 border-slate-200'
              }`}
            >
              Real-Time / Daily
            </button>
            <button
              onClick={() => setDataVolatility('static')}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                dataVolatility === 'static' ? 'bg-amber-600 text-white border-amber-600' : 'bg-white text-slate-700 border-slate-200'
              }`}
            >
              Static / Yearly
            </button>
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">Live vector DB indexing vs retraining</span>
        </div>

        {/* Custom Syntax/Style */}
        <div>
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-2">
            Custom Output Syntax / Formatting
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setCustomStyle(false)}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                !customStyle ? 'bg-amber-600 text-white border-amber-600' : 'bg-white text-slate-700 border-slate-200'
              }`}
            >
              Standard Markdown
            </button>
            <button
              onClick={() => setCustomStyle(true)}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                customStyle ? 'bg-amber-600 text-white border-amber-600' : 'bg-white text-slate-700 border-slate-200'
              }`}
            >
              Strict Domain Dialect
            </button>
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">Internalizing syntax into neural weights</span>
        </div>

        {/* Hallucination Tolerance */}
        <div>
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-2">
            Factual Accuracy Tolerance
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setHallucinationTolerance('strict')}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                hallucinationTolerance === 'strict' ? 'bg-amber-600 text-white border-amber-600' : 'bg-white text-slate-700 border-slate-200'
              }`}
            >
              Strict Zero-Tolerance
            </button>
            <button
              onClick={() => setHallucinationTolerance('flexible')}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                hallucinationTolerance === 'flexible' ? 'bg-amber-600 text-white border-amber-600' : 'bg-white text-slate-700 border-slate-200'
              }`}
            >
              Flexible / Creative
            </button>
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">RAG grounds responses in source evidence</span>
        </div>
      </div>

      {/* Recommendation Output Banner */}
      <div className="p-6 bg-slate-900 text-white rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400">Recommended Architecture</span>
          <h4 className="text-2xl font-black text-white mt-0.5">{recommendation}</h4>
          <p className="text-xs text-slate-300 mt-1 max-w-xl">
            {recommendation === 'RAG' && 'Deploy a hybrid vector search RAG pipeline. Provides immediate factual grounding without retraining costs.'}
            {recommendation === 'Fine-Tuning' && 'Execute QLoRA fine-tuning on domain dataset to internalize complex structural syntax and formatting.'}
            {recommendation === 'Hybrid (RAG + Fine-Tuning)' && 'Fine-tune a smaller base model for custom output syntax, and attach a RAG vector index for live factual context.'}
          </p>
        </div>

        <div className="flex gap-3 font-mono text-xs">
          <div className="p-3 bg-slate-800 rounded-xl text-center border border-slate-700">
            <div className="text-amber-400 font-bold">{scoreRAG} pts</div>
            <div className="text-[10px] text-slate-400">RAG Fit</div>
          </div>
          <div className="p-3 bg-slate-800 rounded-xl text-center border border-slate-700">
            <div className="text-blue-400 font-bold">{scoreFT} pts</div>
            <div className="text-[10px] text-slate-400">Fine-Tune Fit</div>
          </div>
        </div>
      </div>
    </div>
  );
};
