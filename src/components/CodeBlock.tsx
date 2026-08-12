import React, { useState } from 'react';
import { CodeExample } from '../types';
import { Copy, Check, Play, Terminal, Sparkles } from 'lucide-react';

interface CodeBlockProps {
  example: CodeExample;
  onCodeRun?: () => void;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ example, onCodeRun }) => {
  const [copied, setCopied] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [output, setOutput] = useState<string | null>(null);
  const [execTime, setExecTime] = useState<number | null>(null);

  const handleCopy = () => {
    navigator.clipboard.writeText(example.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRun = async () => {
    setIsRunning(true);
    setOutput(null);
    try {
      const res = await fetch('/api/simulate-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: example.code,
          language: example.language,
          title: example.title
        })
      });
      const data = await res.json();
      setOutput(data.output);
      setExecTime(data.executionTimeMs);
      if (onCodeRun) onCodeRun();
    } catch {
      setOutput('[ERROR] Simulation request failed. Verify server connection.');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden shadow-xl text-slate-200 my-4">
      {/* Header Bar */}
      <div className="bg-slate-900/90 px-4 py-3 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-rose-500/80 inline-block"></span>
            <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block"></span>
            <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block"></span>
          </div>
          <span className="font-mono text-xs font-semibold text-slate-300 ml-2">{example.filename}</span>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800/50">
            {example.language}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white bg-slate-800/60 hover:bg-slate-800 rounded-lg transition-all"
            title="Copy code"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          <button
            onClick={handleRun}
            disabled={isRunning}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-lg shadow-sm transition-all"
          >
            {isRunning ? (
              <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            ) : (
              <Play className="w-3.5 h-3.5 fill-current" />
            )}
            <span>{isRunning ? 'Simulating...' : 'Simulate Expected Output'}</span>
          </button>
        </div>
      </div>

      {/* Code Body */}
      <div className="p-4 overflow-x-auto font-mono text-xs leading-relaxed text-blue-100/90 bg-slate-950">
        <pre><code>{example.code}</code></pre>
      </div>

      {/* Code Explanation */}
      <div className="px-4 py-2.5 bg-slate-900/60 border-t border-slate-800/60 text-xs text-slate-400 flex items-start gap-2">
        <Sparkles className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
        <p className="leading-snug">{example.explanation}</p>
      </div>

      {/* Simulated Output Sandbox */}
      {output && (
        <div className="bg-slate-900 border-t border-slate-800 p-4 font-mono text-xs">
          <div className="flex items-center justify-between mb-2 text-slate-400 font-sans">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-emerald-400" />
              <span className="font-bold text-slate-200">Simulated Output (not executed)</span>
            </div>
            {execTime && <span className="text-[11px] text-slate-500">Duration: {execTime}ms</span>}
          </div>
          <pre className="p-3 bg-black/70 rounded-lg text-emerald-400 overflow-x-auto text-[11px] leading-relaxed border border-emerald-950">
            {output}
          </pre>
        </div>
      )}
    </div>
  );
};
