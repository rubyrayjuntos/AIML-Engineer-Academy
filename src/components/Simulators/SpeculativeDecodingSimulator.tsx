import React, { useMemo, useState } from 'react';
import { Gauge, RefreshCw, Zap } from 'lucide-react';

/** Teaching i.i.d. model: E[accepted drafts] + bonus token from verify. */
function expectedAcceptedLength(gamma: number, acceptProb: number): number {
  let acceptedDrafts = 0;
  for (let k = 1; k <= gamma; k += 1) acceptedDrafts += acceptProb ** k;
  return acceptedDrafts + 1;
}

function speculativeSpeedup(
  gamma: number,
  acceptProb: number,
  tDraft: number,
  tVerify: number
): number {
  const tokens = expectedAcceptedLength(gamma, acceptProb);
  const cycleTime = gamma * tDraft + tVerify;
  const baselineTps = 1 / tVerify;
  return tokens / cycleTime / baselineTps;
}

export const SpeculativeDecodingSimulator: React.FC = () => {
  const [gamma, setGamma] = useState(5);
  const [acceptProb, setAcceptProb] = useState(0.7);
  const [tDraft, setTDraft] = useState(0.2);
  const [tVerify, setTVerify] = useState(1.0);

  const stats = useMemo(() => {
    const tokens = expectedAcceptedLength(gamma, acceptProb);
    const speedup = speculativeSpeedup(gamma, acceptProb, tDraft, tVerify);
    const cycleMs = (gamma * tDraft + tVerify) * 1000;
    const tokensPerSec = tokens / ((gamma * tDraft + tVerify) || 1);
    const baselineTps = 1 / tVerify;
    return { tokens, speedup, cycleMs, tokensPerSec, baselineTps };
  }, [gamma, acceptProb, tDraft, tVerify]);

  const draftSlots = Array.from({ length: gamma }, (_, i) => {
    const pSurvive = acceptProb ** (i + 1);
    return { i: i + 1, pSurvive };
  });

  return (
    <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm my-6 space-y-6">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 pb-6 border-b border-slate-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
            <Zap className="w-3.5 h-3.5" />
            Speculative Decoding Calculator
          </div>
          <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Draft γ · Acceptance · Teaching Speedup
          </h3>
          <p className="text-sm text-slate-500 mt-1 max-w-2xl">
            Closed-form teaching estimate under i.i.d. acceptance probability. Correct acceptance sampling
            preserves the <em>target</em> distribution — this UI does not claim measured GPU results.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold uppercase tracking-wide text-amber-700 bg-amber-50 border border-amber-200 px-2 py-1 rounded-full whitespace-nowrap">
            Teaching estimate
          </span>
          <button
            type="button"
            onClick={() => {
              setGamma(5);
              setAcceptProb(0.7);
              setTDraft(0.2);
              setTVerify(1.0);
            }}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-xl"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Reset
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 bg-slate-50 p-6 rounded-2xl border border-slate-100">
        <label className="block text-sm">
          <div className="flex justify-between mb-2">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Draft length γ</span>
            <span className="font-mono text-sm font-bold text-blue-600">{gamma}</span>
          </div>
          <input
            type="range"
            min={1}
            max={12}
            value={gamma}
            onChange={(e) => setGamma(Number(e.target.value))}
            className="w-full accent-blue-600"
          />
        </label>
        <label className="block text-sm">
          <div className="flex justify-between mb-2">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Accept prob p</span>
            <span className="font-mono text-sm font-bold text-blue-600">{acceptProb.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min={0.1}
            max={0.95}
            step={0.05}
            value={acceptProb}
            onChange={(e) => setAcceptProb(Number(e.target.value))}
            className="w-full accent-blue-600"
          />
        </label>
        <label className="block text-sm">
          <div className="flex justify-between mb-2">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Draft cost (rel)</span>
            <span className="font-mono text-sm font-bold text-blue-600">{tDraft.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min={0.05}
            max={1}
            step={0.05}
            value={tDraft}
            onChange={(e) => setTDraft(Number(e.target.value))}
            className="w-full accent-blue-600"
          />
        </label>
        <label className="block text-sm">
          <div className="flex justify-between mb-2">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Verify cost (rel)</span>
            <span className="font-mono text-sm font-bold text-blue-600">{tVerify.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min={0.5}
            max={3}
            step={0.1}
            value={tVerify}
            onChange={(e) => setTVerify(Number(e.target.value))}
            className="w-full accent-blue-600"
          />
        </label>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="text-xs text-slate-500 uppercase tracking-wide flex items-center gap-1">
            <Gauge className="w-3.5 h-3.5" /> E[tokens / cycle]
          </div>
          <div className="text-2xl font-black text-slate-900 mt-1">{stats.tokens.toFixed(2)}</div>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="text-xs text-slate-500 uppercase tracking-wide">Teaching speedup</div>
          <div className="text-2xl font-black text-slate-900 mt-1">{stats.speedup.toFixed(2)}×</div>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="text-xs text-slate-500 uppercase tracking-wide">Spec tokens / sec (rel)</div>
          <div className="text-2xl font-black text-slate-900 mt-1">{stats.tokensPerSec.toFixed(2)}</div>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="text-xs text-slate-500 uppercase tracking-wide">Baseline tokens / sec (rel)</div>
          <div className="text-2xl font-black text-slate-900 mt-1">{stats.baselineTps.toFixed(2)}</div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <div className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3">
          Draft token survival curve (p^k)
        </div>
        <div className="flex items-end gap-2 h-28">
          {draftSlots.map((slot) => (
            <div key={slot.i} className="flex-1 flex flex-col items-center gap-1 h-full justify-end">
              <div
                className="w-full rounded-t-md bg-blue-500/80 min-h-[4px]"
                style={{ height: `${Math.max(4, slot.pSurvive * 100)}%` }}
                title={`P(accept first ${slot.i}) ≈ ${slot.pSurvive.toFixed(3)}`}
              />
              <span className="text-[10px] text-slate-500">{slot.i}</span>
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-500 mt-3">
          Cycle time teaching units: {(stats.cycleMs / 1000).toFixed(2)} (= γ·t_draft + t_verify). Link Module 2.4
          MTP heads as an optional draft source; measure real acceptance on your serving stack.
        </p>
      </div>
    </div>
  );
};
