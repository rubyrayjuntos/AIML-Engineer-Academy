import React, { useMemo, useState } from 'react';
import { Cpu, Gauge, ShieldAlert } from 'lucide-react';

type TrackMode = 'cpu_default' | 'gpu_requested_no_cuda' | 'gpu_ready';

function resolveMode(academyGpu: boolean, cuda: boolean): TrackMode {
  if (!academyGpu) return 'cpu_default';
  if (!cuda) return 'gpu_requested_no_cuda';
  return 'gpu_ready';
}

export const GpuTrackSimulator: React.FC = () => {
  const [academyGpu, setAcademyGpu] = useState(false);
  const [cuda, setCuda] = useState(false);
  const [engine, setEngine] = useState<'deterministic' | 'vllm'>('deterministic');
  const [qloraExecute, setQloraExecute] = useState(false);

  const mode = useMemo(() => resolveMode(academyGpu, cuda), [academyGpu, cuda]);

  const claims = useMemo(() => {
    const vllmWired = academyGpu && cuda && engine === 'vllm';
    const qloraRan = academyGpu && cuda && qloraExecute;
    return {
      gpu_used: vllmWired || qloraRan,
      vllm_measured: vllmWired,
      qlora_executed: qloraRan,
      local_cpu_path_measured: !vllmWired,
      mode,
    };
  }, [academyGpu, cuda, engine, qloraExecute, mode]);

  const banner =
    mode === 'cpu_default'
      ? 'CI / Cloud Agent default — NumPy + DeterministicEngine. claims.* stay false.'
      : mode === 'gpu_requested_no_cuda'
        ? 'ACADEMY_GPU=1 but CUDA missing — refuse silent vLLM fallback; keep claims honest.'
        : 'CUDA ready — optional QLoRA dry-run / vLLM adapter allowed on this host only.';

  return (
    <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm my-6 space-y-6">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 pb-6 border-b border-slate-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-slate-100 text-slate-700 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
            <Cpu className="w-3.5 h-3.5" />
            Optional GPU Track Gate
          </div>
          <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            ACADEMY_GPU · QLoRA Plan · vLLM Adapter
          </h3>
          <p className="text-sm text-slate-500 mt-1 max-w-2xl">
            Teaching estimate of claim-safe gating for Module 2 QLoRA and Module 4 vLLM. This UI does not
            start CUDA, download weights, or measure tokens/sec.
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

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input type="checkbox" checked={academyGpu} onChange={(e) => setAcademyGpu(e.target.checked)} />
          <span>
            <code className="text-xs bg-slate-100 px-1 rounded">ACADEMY_GPU=1</code>
          </span>
        </label>
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input type="checkbox" checked={cuda} onChange={(e) => setCuda(e.target.checked)} />
          <span>CUDA available</span>
        </label>
        <label className="block text-sm">
          <span className="text-xs font-bold uppercase text-slate-500">ACADEMY_ENGINE</span>
          <select
            className="mt-1 w-full border border-slate-200 rounded-xl px-3 py-2"
            value={engine}
            onChange={(e) => setEngine(e.target.value as 'deterministic' | 'vllm')}
          >
            <option value="deterministic">deterministic</option>
            <option value="vllm">vllm</option>
          </select>
        </label>
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input
            type="checkbox"
            checked={qloraExecute}
            onChange={(e) => setQloraExecute(e.target.checked)}
          />
          <span>
            <code className="text-xs bg-slate-100 px-1 rounded">ACADEMY_QLORA_EXECUTE=1</code>
          </span>
        </label>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {(
          [
            ['gpu_used', claims.gpu_used],
            ['vllm_measured', claims.vllm_measured],
            ['qlora_executed', claims.qlora_executed],
            ['cpu_path', claims.local_cpu_path_measured],
          ] as const
        ).map(([key, value]) => (
          <div key={key} className="rounded-2xl border border-slate-200 p-4">
            <div className="text-xs uppercase tracking-wide text-slate-500 flex items-center gap-1">
              <Gauge className="w-3.5 h-3.5" /> {key}
            </div>
            <div className={`text-xl font-black mt-1 ${value ? 'text-emerald-700' : 'text-slate-800'}`}>
              {String(value)}
            </div>
          </div>
        ))}
      </div>

      <ul className="text-xs text-slate-500 space-y-1 list-disc pl-5">
        <li>
          Module 2: <code className="bg-slate-100 px-1 rounded">python -m app.qlora_optional</code> writes a plan;
          training only with execute+model on a real GPU.
        </li>
        <li>
          Module 4: <code className="bg-slate-100 px-1 rounded">ACADEMY_ENGINE=vllm</code> requires{' '}
          <code className="bg-slate-100 px-1 rounded">ACADEMY_GPU=1</code> or the factory raises (no silent CPU
          mislabel).
        </li>
        <li>Cloud Agents should leave ACADEMY_GPU unset.</li>
      </ul>
    </div>
  );
};
