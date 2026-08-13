import React, { useMemo, useState } from 'react';
import { ClipboardCheck, ShieldAlert } from 'lucide-react';

export const EvalDeploySimulator: React.FC = () => {
  const [academyEval, setAcademyEval] = useState(false);
  const [judgeKey, setJudgeKey] = useState(false);
  const [promptfoo, setPromptfoo] = useState(false);
  const [academyDeploy, setAcademyDeploy] = useState(false);
  const [hfToken, setHfToken] = useState(false);
  const [renderKey, setRenderKey] = useState(false);
  const [apiOk, setApiOk] = useState(false);

  const claims = useMemo(
    () => ({
      deepeval_executed: academyEval && judgeKey,
      promptfoo_executed: promptfoo,
      huggingface_deployed: false,
      huggingface_api_ok: academyDeploy && hfToken && apiOk,
      render_deployed: academyDeploy && renderKey && apiOk,
      offline_edd: true,
    }),
    [academyEval, judgeKey, promptfoo, academyDeploy, hfToken, renderKey, apiOk]
  );

  const banner =
    !academyEval && !promptfoo && !academyDeploy
      ? 'CI default — offline EDD gates + provider plans. All live claims stay false.'
      : 'Optional flags enabled — claims only flip true when keys/API success conditions are met.';

  return (
    <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm my-6 space-y-6">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 pb-6 border-b border-slate-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-50 text-emerald-800 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
            <ClipboardCheck className="w-3.5 h-3.5" />
            Eval & Deploy Track Gate
          </div>
          <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            DeepEval · Promptfoo · HF / Render Claims
          </h3>
          <p className="text-sm text-slate-500 mt-1 max-w-2xl">
            Teaching estimate of Module 5 claim-safe gating. Does not call DeepEval, Promptfoo, Hugging Face,
            or Render APIs.
          </p>
        </div>
        <span className="text-[10px] font-bold uppercase tracking-wide text-amber-700 bg-amber-50 border border-amber-200 px-2 py-1 rounded-full whitespace-nowrap">
          Teaching estimate
        </span>
      </div>

      <div className="flex items-start gap-2 text-sm bg-slate-50 border border-slate-200 rounded-2xl p-4">
        <ShieldAlert className="w-4 h-4 mt-0.5 text-amber-600 shrink-0" />
        <p className="text-slate-700">{banner}</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" checked={academyEval} onChange={(e) => setAcademyEval(e.target.checked)} />
          <code className="text-xs bg-slate-100 px-1 rounded">ACADEMY_EVAL=1</code>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" checked={judgeKey} onChange={(e) => setJudgeKey(e.target.checked)} />
          Judge API key present
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" checked={promptfoo} onChange={(e) => setPromptfoo(e.target.checked)} />
          <code className="text-xs bg-slate-100 px-1 rounded">ACADEMY_PROMPTFOO=1</code>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" checked={academyDeploy} onChange={(e) => setAcademyDeploy(e.target.checked)} />
          <code className="text-xs bg-slate-100 px-1 rounded">ACADEMY_DEPLOY=1</code>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" checked={hfToken} onChange={(e) => setHfToken(e.target.checked)} />
          HF_TOKEN
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" checked={renderKey} onChange={(e) => setRenderKey(e.target.checked)} />
          RENDER_API_KEY
        </label>
        <label className="flex items-center gap-2 cursor-pointer sm:col-span-2">
          <input type="checkbox" checked={apiOk} onChange={(e) => setApiOk(e.target.checked)} />
          Live deploy API returned deployment id
        </label>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-6 gap-3">
        {(
          [
            ['offline_edd', claims.offline_edd],
            ['deepeval_executed', claims.deepeval_executed],
            ['promptfoo_executed', claims.promptfoo_executed],
            ['huggingface_api_ok', claims.huggingface_api_ok],
            ['huggingface_deployed', claims.huggingface_deployed],
            ['render_deployed', claims.render_deployed],
          ] as const
        ).map(([key, value]) => (
          <div key={key} className="rounded-2xl border border-slate-200 p-4">
            <div className="text-[10px] uppercase tracking-wide text-slate-500">{key}</div>
            <div className={`text-lg font-black mt-1 ${value ? 'text-emerald-700' : 'text-slate-800'}`}>
              {String(value)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
