import React, { useMemo, useState } from 'react';
import { Waves } from 'lucide-react';

/** Nichol & Dhariwal cosine schedule (teaching version). */
function cosineAlphaBar(t: number, T: number, s = 0.008): number {
  const f = (u: number) => Math.cos(((u / T + s) / (1 + s)) * (Math.PI / 2)) ** 2;
  return Math.min(1, Math.max(0, f(t) / f(0)));
}

/** Toy 1-D "image": a sharp pulse that gets noised over time. */
function makeSignal(n = 48): number[] {
  const x = new Array(n).fill(0);
  for (let i = 18; i < 30; i++) x[i] = 1;
  return x;
}

function qSample(x0: number[], t: number, T: number, seed: number): number[] {
  const abar = cosineAlphaBar(t, T);
  // Deterministic pseudo-noise from seed + index for stable teaching viz
  return x0.map((v, i) => {
    const noise = Math.sin(seed * 12.9898 + i * 78.233) * 43758.5453;
    const eps = (noise - Math.floor(noise)) * 2 - 1;
    return Math.sqrt(abar) * v + Math.sqrt(1 - abar) * eps;
  });
}

export const DiffusionSimulator: React.FC = () => {
  const T = 1000;
  const [t, setT] = useState(0);
  const [seed, setSeed] = useState(42);
  const x0 = useMemo(() => makeSignal(), []);
  const xt = useMemo(() => qSample(x0, t, T, seed), [x0, t, seed]);
  const abar = cosineAlphaBar(t, T);
  const snr = abar / Math.max(1e-12, 1 - abar);

  const minY = Math.min(...xt, ...x0);
  const maxY = Math.max(...xt, ...x0);
  const span = Math.max(1e-6, maxY - minY);

  const toPoints = (arr: number[]) =>
    arr
      .map((v, i) => {
        const x = (i / (arr.length - 1)) * 100;
        const y = 100 - ((v - minY) / span) * 90 - 5;
        return `${x},${y}`;
      })
      .join(' ');

  return (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
              <Waves size={18} />
            </div>
            <h3 className="font-bold text-slate-800">Diffusion Forward Process Lab</h3>
          </div>
          <p className="text-sm text-slate-500 max-w-2xl">
            Teaching estimate of the DDPM forward noising chain on a toy 1-D signal (not a real image
            generator). Drag <code className="text-xs bg-slate-100 px-1 rounded">t</code> to watch
            signal energy mix into noise under a cosine ᾱ schedule — the same idea Stable Diffusion
            applies in latent space with CLIP text conditioning on the reverse step.
          </p>
        </div>
        <span className="text-[10px] font-bold uppercase tracking-wide text-amber-700 bg-amber-50 border border-amber-200 px-2 py-1 rounded-full whitespace-nowrap">
          Teaching estimate
        </span>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <label className="block text-sm md:col-span-2">
          <span className="font-medium text-slate-700">
            Timestep t = {t} / {T}
          </span>
          <input
            type="range"
            min={0}
            max={T}
            step={1}
            value={t}
            onChange={(e) => setT(Number(e.target.value))}
            className="w-full mt-2"
          />
        </label>
        <label className="block text-sm">
          <span className="font-medium text-slate-700">Noise seed</span>
          <input
            type="number"
            value={seed}
            onChange={(e) => setSeed(Number(e.target.value) || 0)}
            className="mt-2 w-full border border-slate-200 rounded-lg px-3 py-2"
          />
        </label>
      </div>

      <div className="grid sm:grid-cols-3 gap-3 text-sm">
        <div className="rounded-lg bg-slate-50 border border-slate-100 p-3">
          <div className="text-xs text-slate-500 uppercase tracking-wide">ᾱ<sub>t</sub></div>
          <div className="font-mono font-semibold text-slate-800">{abar.toFixed(4)}</div>
        </div>
        <div className="rounded-lg bg-slate-50 border border-slate-100 p-3">
          <div className="text-xs text-slate-500 uppercase tracking-wide">SNR (ᾱ / (1−ᾱ))</div>
          <div className="font-mono font-semibold text-slate-800">
            {snr > 100 ? '>100' : snr.toFixed(3)}
          </div>
        </div>
        <div className="rounded-lg bg-slate-50 border border-slate-100 p-3">
          <div className="text-xs text-slate-500 uppercase tracking-wide">Regime</div>
          <div className="font-semibold text-slate-800">
            {t === 0 ? 'Clean x₀' : abar > 0.5 ? 'Mild noise' : abar > 0.05 ? 'Heavy noise' : 'Near prior'}
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <svg viewBox="0 0 100 100" className="w-full h-48" role="img" aria-label="Forward diffusion signal plot">
          <polyline
            fill="none"
            stroke="#94a3b8"
            strokeWidth="0.6"
            strokeDasharray="1.5 1.5"
            points={toPoints(x0)}
          />
          <polyline fill="none" stroke="#4f46e5" strokeWidth="1.2" points={toPoints(xt)} />
        </svg>
        <div className="flex gap-4 text-xs text-slate-500 mt-2">
          <span className="flex items-center gap-1">
            <span className="inline-block w-4 border-t border-dashed border-slate-400" /> x₀ (clean)
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block w-4 border-t-2 border-indigo-600" /> x<sub>t</sub> (noised)
          </span>
        </div>
      </div>

      <div className="text-xs text-slate-500 bg-indigo-50/60 border border-indigo-100 rounded-lg p-3 space-y-1">
        <p>
          <strong className="text-slate-700">Production map:</strong> real systems (SDXL, Flux) run this
          chain in a VAE <em>latent</em> space, not pixels. The U-Net / DiT predicts ε or v, conditioned
          on a CLIP (or T5) text embedding, often with classifier-free guidance.
        </p>
        <p>
          Lab counterpart: <code className="bg-white px-1 rounded">cosine_alpha_bar</code> +{' '}
          <code className="bg-white px-1 rounded">q_sample</code> in Module 2 Architecture Mechanics.
        </p>
      </div>
    </div>
  );
};
