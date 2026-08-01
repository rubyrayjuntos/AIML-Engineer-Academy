import React, { useState } from 'react';
import { Bot, Play, RotateCcw, CheckCircle2, ArrowRight } from 'lucide-react';

interface Step {
  type: 'THOUGHT' | 'ACTION' | 'OBSERVATION' | 'FINAL_ANSWER';
  content: string;
  toolCall?: { name: string; args: string };
  durationMs: number;
}

export const ReactAgentSimulator: React.FC = () => {
  const [goalPrompt, setGoalPrompt] = useState<string>("Analyze Q3 enterprise churn and update executive report in database");
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [isRunning, setIsRunning] = useState<boolean>(false);

  const steps: Step[] = [
    {
      type: 'THOUGHT',
      content: 'Goal requires querying user activity database to calculate Q3 churn rate, then updating the executive summary table.',
      durationMs: 140
    },
    {
      type: 'ACTION',
      content: 'Triggering MCP Database Tool to retrieve user retention schema.',
      toolCall: { name: 'mcp.tools.get_table_schema', args: '{"table": "user_subscriptions"}' },
      durationMs: 85
    },
    {
      type: 'OBSERVATION',
      content: 'Schema returned: id (INT), user_id (UUID), status (TEXT: active|canceled), canceled_at (TIMESTAMP).',
      durationMs: 40
    },
    {
      type: 'THOUGHT',
      content: 'Executing SQL aggregation: Count canceled users in Q3 divided by active baseline users.',
      durationMs: 210
    },
    {
      type: 'ACTION',
      content: 'Invoking SQL execution tool with parameterized read query.',
      toolCall: { name: 'mcp.tools.execute_sql', args: '{"sql": "SELECT COUNT(*) FILTER (WHERE status=\'canceled\') * 100.0 / COUNT(*) AS churn FROM user_subscriptions;"}' },
      durationMs: 120
    },
    {
      type: 'OBSERVATION',
      content: 'SQL Result: churn = 2.84% (Q3 Churn Rate down 0.4% QoQ).',
      durationMs: 30
    },
    {
      type: 'THOUGHT',
      content: 'PydanticAI validation passed (output_type=ExecutiveSummaryReport). Crafting final answer.',
      durationMs: 90
    },
    {
      type: 'FINAL_ANSWER',
      content: 'Executive Report Updated: Q3 Enterprise Churn Rate is 2.84% (a 0.4% improvement QoQ). All metric logs persisted.',
      durationMs: 50
    }
  ];

  const handleNextStep = () => {
    if (currentStepIndex < steps.length - 1) {
      setCurrentStepIndex(prev => prev + 1);
    }
  };

  const handleAutoRun = async () => {
    setIsRunning(true);
    for (let i = currentStepIndex; i < steps.length; i++) {
      setCurrentStepIndex(i);
      await new Promise(resolve => setTimeout(resolve, 600));
    }
    setIsRunning(false);
  };

  const handleReset = () => {
    setCurrentStepIndex(0);
    setIsRunning(false);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm my-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-6 border-b border-slate-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
            <Bot className="w-3.5 h-3.5 text-indigo-600" />
            ReAct Cognitive Agent Loop Emulator
          </div>
          <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Thought → Action → Observation Cycle
          </h3>
          <p className="text-sm text-slate-500 mt-1">
            Step through autonomous reasoning loops, tool calls, and reflection steps in real time.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleReset}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition-all"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
          <button
            onClick={handleNextStep}
            disabled={currentStepIndex >= steps.length - 1 || isRunning}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-xl shadow-sm transition-all"
          >
            <span>Next Step</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleAutoRun}
            disabled={currentStepIndex >= steps.length - 1 || isRunning}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 rounded-xl shadow-sm transition-all"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{isRunning ? 'Running...' : 'Auto Play'}</span>
          </button>
        </div>
      </div>

      {/* Goal Input */}
      <div className="mb-6 bg-slate-50 p-4 rounded-2xl border border-slate-100">
        <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-1">
          Agent Task Objective
        </label>
        <input
          type="text"
          value={goalPrompt}
          onChange={(e) => setGoalPrompt(e.target.value)}
          className="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* ReAct Stepper Visualization */}
      <div className="space-y-3 mb-6 max-h-96 overflow-y-auto p-2">
        {steps.slice(0, currentStepIndex + 1).map((step, idx) => (
          <div
            key={idx}
            className={`p-4 rounded-2xl border transition-all animate-fadeIn ${
              step.type === 'THOUGHT'
                ? 'bg-blue-950/90 text-blue-100 border-blue-800'
                : step.type === 'ACTION'
                ? 'bg-amber-950/90 text-amber-100 border-amber-800'
                : step.type === 'OBSERVATION'
                ? 'bg-slate-900 text-slate-200 border-slate-700'
                : 'bg-emerald-950/90 text-emerald-100 border-emerald-700'
            }`}
          >
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-black opacity-60">#0{idx + 1}</span>
                <span
                  className={`text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded ${
                    step.type === 'THOUGHT'
                      ? 'bg-blue-800/80 text-blue-200'
                      : step.type === 'ACTION'
                      ? 'bg-amber-800/80 text-amber-200'
                      : step.type === 'OBSERVATION'
                      ? 'bg-slate-800 text-slate-300'
                      : 'bg-emerald-800/80 text-emerald-200'
                  }`}
                >
                  {step.type}
                </span>
              </div>
              <span className="text-[10px] font-mono text-slate-400">{step.durationMs}ms</span>
            </div>

            <p className="text-xs leading-relaxed font-sans">{step.content}</p>

            {step.toolCall && (
              <div className="mt-2 p-2.5 bg-black/60 rounded-xl font-mono text-[11px] text-amber-300 border border-amber-900/50">
                <span className="text-amber-500 font-bold">Tool Invoked:</span> {step.toolCall.name}
                <div className="text-amber-200/80 mt-1">Args: {step.toolCall.args}</div>
              </div>
            )}
          </div>
        ))}
      </div>

      {currentStepIndex === steps.length - 1 && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-900 rounded-2xl flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <div className="text-xs font-semibold">
            ReAct execution loop completed in {steps.reduce((acc, s) => acc + s.durationMs, 0)}ms across {steps.length} cognitive cycles.
          </div>
        </div>
      )}
    </div>
  );
};
