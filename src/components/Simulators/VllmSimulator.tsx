import React, { useState } from 'react';
import { Cpu, Zap, Layers, MemoryStick as Memory, AlertTriangle, RefreshCw } from 'lucide-react';

export const VllmSimulator: React.FC = () => {
  const [numRequests, setNumRequests] = useState<number>(64);
  const [avgPromptTokens, setAvgPromptTokens] = useState<number>(512);
  const [blockSize, setBlockSize] = useState<16 | 128>(16);
  const [gpuMemoryGb, setGpuMemoryGb] = useState<number>(24); // 24GB RTX 4090 / L4

  // Calculations
  const totalTokens = numRequests * avgPromptTokens;
  const bytesPerTokenInKvCache = 2 * 2 * 32 * 128; // fp16, 2 tensors (K,V), 32 layers, 128 head dim = ~524KB per token!
  const totalKvMemoryMb = Math.round((totalTokens * bytesPerTokenInKvCache) / (1024 * 1024));
  const totalKvMemoryGb = (totalKvMemoryMb / 1024).toFixed(2);

  // Block allocation calculations
  const totalBlocks = Math.ceil(totalTokens / blockSize);
  const wastedTokensPerBlock = Math.round(blockSize * 0.08); // average internal fragmentation
  const totalWastedMb = Math.round(((totalBlocks * wastedTokensPerBlock * bytesPerTokenInKvCache) / (1024 * 1024)));
  const fragmentationPercent = ((totalWastedMb / Math.max(totalKvMemoryMb, 1)) * 100).toFixed(1);

  // Static allocation comparison (legacy PyTorch allocation)
  const legacyStaticMemoryGb = ((numRequests * 2048 * bytesPerTokenInKvCache) / (1024 * 1024 * 1024)).toFixed(2);
  const memorySavingsVsLegacy = (((parseFloat(legacyStaticMemoryGb) - parseFloat(totalKvMemoryGb)) / parseFloat(legacyStaticMemoryGb)) * 100).toFixed(1);

  const isOom = parseFloat(totalKvMemoryGb) > gpuMemoryGb * 0.7; // >70% allocated to KV cache triggers OOM

  return (
    <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm my-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-6 border-b border-slate-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
            <Zap className="w-3.5 h-3.5 text-blue-600" />
            vLLM PagedAttention Benchmark Calculator
          </div>
          <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            KV Cache Memory & Block Size Optimization
          </h3>
          <p className="text-sm text-slate-500 mt-1">
            Simulate virtual memory page allocation, internal fragmentation, and OOM thresholds across GPU hardware.
          </p>
        </div>

        <button
          onClick={() => { setNumRequests(64); setAvgPromptTokens(512); setBlockSize(16); }}
          className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-xl transition-all self-start"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Reset Defaults</span>
        </button>
      </div>

      {/* Control Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 bg-slate-50 p-6 rounded-2xl border border-slate-100">
        {/* Concurrent Requests */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Concurrent Streams</label>
            <span className="font-mono text-sm font-bold text-blue-600">{numRequests} requests</span>
          </div>
          <input
            type="range"
            min="8"
            max="256"
            step="8"
            value={numRequests}
            onChange={(e) => setNumRequests(Number(e.target.value))}
            className="w-full accent-blue-600 cursor-pointer"
          />
          <span className="text-[11px] text-slate-400">Simulates active decode streams</span>
        </div>

        {/* Avg Prompt Tokens */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Avg Sequence Length</label>
            <span className="font-mono text-sm font-bold text-blue-600">{avgPromptTokens} tokens</span>
          </div>
          <input
            type="range"
            min="128"
            max="8192"
            step="128"
            value={avgPromptTokens}
            onChange={(e) => setAvgPromptTokens(Number(e.target.value))}
            className="w-full accent-blue-600 cursor-pointer"
          />
          <span className="text-[11px] text-slate-400">Prompt length + output generation</span>
        </div>

        {/* Block Size Selection */}
        <div>
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-2">
            PagedAttention block_size
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setBlockSize(16)}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                blockSize === 16
                  ? 'bg-blue-600 text-white border-blue-600 shadow-md shadow-blue-200'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
              }`}
            >
              16 Tokens (Default)
            </button>
            <button
              onClick={() => setBlockSize(128)}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all border ${
                blockSize === 128
                  ? 'bg-blue-600 text-white border-blue-600 shadow-md shadow-blue-200'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
              }`}
            >
              128 Tokens (Large)
            </button>
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">16 = minimal fragmentation; 128 = lower table overhead</span>
        </div>
      </div>

      {/* Warning Alert if OOM */}
      {isOom && (
        <div className="mb-6 p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-2xl flex items-center gap-3 animate-pulse">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
          <div className="text-xs">
            <strong className="font-bold">Out-Of-Memory (OOM) Hazard Detected:</strong> KV cache allocation ({totalKvMemoryGb} GB) exceeds safe GPU VRAM budget for {gpuMemoryGb}GB hardware. Reduce concurrent streams or decrease block size.
          </div>
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="p-5 rounded-2xl bg-slate-900 text-white shadow-md">
          <div className="flex justify-between items-center mb-1 text-slate-400">
            <span className="text-[11px] font-bold uppercase tracking-wider">Total KV Cache Memory</span>
            <Memory className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-black font-mono text-blue-400">{totalKvMemoryGb} GB</div>
          <div className="text-[11px] text-slate-400 mt-1">{totalTokens.toLocaleString()} tokens cached</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 text-white shadow-md">
          <div className="flex justify-between items-center mb-1 text-slate-400">
            <span className="text-[11px] font-bold uppercase tracking-wider">Physical Blocks Allocated</span>
            <Layers className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black font-mono text-emerald-400">{totalBlocks.toLocaleString()}</div>
          <div className="text-[11px] text-slate-400 mt-1">block_size = {blockSize} tokens/page</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 text-white shadow-md">
          <div className="flex justify-between items-center mb-1 text-slate-400">
            <span className="text-[11px] font-bold uppercase tracking-wider">Internal Fragmentation</span>
            <Cpu className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black font-mono text-amber-400">{fragmentationPercent}%</div>
          <div className="text-[11px] text-slate-400 mt-1">~{totalWastedMb} MB unused in memory pages</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 text-white shadow-md">
          <div className="flex justify-between items-center mb-1 text-slate-400">
            <span className="text-[11px] font-bold uppercase tracking-wider">Savings vs Static PyTorch</span>
            <Zap className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-black font-mono text-indigo-400">+{memorySavingsVsLegacy}%</div>
          <div className="text-[11px] text-slate-400 mt-1">Legacy PyTorch required {legacyStaticMemoryGb} GB</div>
        </div>
      </div>

      {/* Visual Memory Blocks Grid Simulation */}
      <div>
        <div className="flex justify-between items-center mb-3">
          <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            PagedAttention Physical Block Table Map (Visual Blocks)
          </h4>
          <span className="text-[11px] text-slate-500 font-mono">
            Green = Active KV Tokens | Dark = Free Page Allocation
          </span>
        </div>

        <div className="grid grid-cols-8 sm:grid-cols-12 md:grid-cols-16 gap-1.5 p-4 bg-slate-950 rounded-2xl border border-slate-800 max-h-48 overflow-y-auto">
          {Array.from({ length: Math.min(totalBlocks, 64) }).map((_, i) => (
            <div
              key={i}
              className={`h-7 rounded flex items-center justify-center font-mono text-[9px] font-bold transition-all ${
                i % 5 === 0
                  ? 'bg-amber-500/80 text-amber-950 border border-amber-400/50' // partial fragmentation
                  : 'bg-emerald-500/80 text-emerald-950 border border-emerald-400/50'
              }`}
              title={`Block #${i+1}: ${blockSize} token slots allocated`}
            >
              #{i+1}
            </div>
          ))}
          {totalBlocks > 64 && (
            <div className="col-span-full text-center py-2 text-xs font-mono text-slate-500 italic">
              + {totalBlocks - 64} more physical pages allocated dynamically in VRAM...
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
