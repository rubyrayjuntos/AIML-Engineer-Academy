import React, { useState } from 'react';
import { systemBlueprints } from '../data/curriculumData';
import { Network, ShieldAlert, Cpu, ArrowRight } from 'lucide-react';

export const SystemDesignCanvas: React.FC = () => {
  const [selectedBpId, setSelectedBpId] = useState<string>('bp_chatgpt');
  const activeBp = systemBlueprints.find(b => b.id === selectedBpId) || systemBlueprints[0];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-violet-50 text-violet-700 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
          <Network className="w-3.5 h-3.5 text-violet-600" />
          Production Architecture Inspector
        </div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">
          System Design Blueprints
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Explore distributed system topologies, latency timelines, and security boundaries for enterprise AI apps.
        </p>

        {/* Blueprint Tabs */}
        <div className="flex flex-wrap gap-2 mt-6 pt-4 border-t border-slate-100">
          {systemBlueprints.map(bp => (
            <button
              key={bp.id}
              onClick={() => setSelectedBpId(bp.id)}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                selectedBpId === bp.id
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {bp.title}
            </button>
          ))}
        </div>
      </div>

      {/* Main Blueprint Diagram & Node Matrix */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm space-y-8">
        <div>
          <h2 className="text-xl font-bold text-slate-900">{activeBp.title}</h2>
          <p className="text-xs font-mono text-blue-600 font-bold mt-1">{activeBp.tagline}</p>
          <p className="text-xs text-slate-600 mt-2 leading-relaxed">{activeBp.overview}</p>
        </div>

        {/* Nodes Flow Map */}
        <div>
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-4">
            Topology Data Flow Nodes
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {activeBp.nodes.map((node, i) => (
              <div key={node.id} className="p-5 rounded-2xl bg-slate-950 text-slate-200 border border-slate-800 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-mono text-xs font-black text-blue-400">#0{i + 1}</span>
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    {node.type}
                  </span>
                </div>

                <h4 className="text-sm font-bold text-white">{node.label}</h4>
                <p className="text-[11px] text-slate-400 leading-relaxed">{node.description}</p>

                <div className="pt-2 border-t border-slate-800/80 flex justify-between items-center text-[10px] font-mono text-slate-400">
                  <span>Avg Latency:</span>
                  <span className="text-emerald-400 font-bold">{node.latencyAvgMs}ms</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Edges & Protocols List */}
        <div>
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
            Inter-Service Network Protocols
          </h3>

          <div className="space-y-2">
            {activeBp.edges.map((edge, i) => (
              <div key={i} className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between text-xs font-mono gap-2">
                <div className="flex items-center gap-2 text-slate-800 font-bold">
                  <span>{edge.from}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                  <span>{edge.to}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-slate-600 font-sans font-medium">{edge.label}</span>
                  <span className="px-2 py-0.5 rounded bg-violet-100 text-violet-800 font-bold text-[10px]">
                    {edge.protocol}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Security & Scaling Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-4 border-t border-slate-100">
          <div className="p-5 rounded-2xl bg-slate-900 text-slate-200 border border-slate-800 space-y-3">
            <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
              <ShieldAlert className="w-4 h-4" /> Security Considerations
            </h4>
            <ul className="space-y-2 text-xs text-slate-300">
              {activeBp.securityConsiderations.map((sec, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-amber-400">•</span>
                  <span>{sec}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 text-slate-200 border border-slate-800 space-y-3">
            <h4 className="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center gap-2">
              <Cpu className="w-4 h-4" /> Scaling Bottlenecks & Fixes
            </h4>
            <ul className="space-y-2 text-xs text-slate-300">
              {activeBp.scalingBottlenecks.map((bot, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-blue-400">•</span>
                  <span>{bot}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
