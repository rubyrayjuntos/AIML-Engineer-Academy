import React, { useMemo, useState } from 'react';
import { Bot, Play, RotateCcw, CheckCircle2, ArrowRight } from 'lucide-react';

interface Step {
  type: 'THOUGHT' | 'ACTION' | 'OBSERVATION' | 'FINAL_ANSWER';
  content: string;
  toolCall?: { name: string; args: string };
  durationMs: number;
}

function buildStepsForGoal(goalPrompt: string): Step[] {
  const goal = goalPrompt.toLowerCase();

  if (goal.includes('churn') || goal.includes('report') || goal.includes('database') || goal.includes('sql')) {
    const wantsWrite = /update|write|persist|insert|modify/.test(goal);
    return [
      {
        type: 'THOUGHT',
        content: `Interpreting goal: "${goalPrompt}". Need retention metrics from subscriptions data${wantsWrite ? ', then a write action that should hit an approval gate' : ''}.`,
        durationMs: 140
      },
      {
        type: 'ACTION',
        content: 'Calling a read-only MCP schema tool before generating SQL.',
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
        content: 'Planning a parameterized aggregation for Q3 churn; avoiding string-concatenated SQL.',
        durationMs: 210
      },
      {
        type: 'ACTION',
        content: 'Executing a read-only SQL aggregation tool.',
        toolCall: {
          name: 'mcp.tools.execute_sql',
          args: '{"sql": "SELECT COUNT(*) FILTER (WHERE status=\'canceled\') * 100.0 / COUNT(*) AS churn FROM user_subscriptions;"}'
        },
        durationMs: 120
      },
      {
        type: 'OBSERVATION',
        content: 'SQL Result: churn = 2.84% (Q3 Churn Rate down 0.4% QoQ).',
        durationMs: 30
      },
      wantsWrite
        ? {
            type: 'ACTION' as const,
            content: 'Write tool requested — pausing for human approval before mutating executive_report.',
            toolCall: {
              name: 'mcp.tools.update_report',
              args: '{"table":"executive_report","status":"PENDING_HUMAN_APPROVAL"}'
            },
            durationMs: 95
          }
        : {
            type: 'THOUGHT' as const,
            content: 'No write tools are required for this goal. Preparing a typed ExecutiveSummaryReport response.',
            durationMs: 90
          },
      {
        type: 'FINAL_ANSWER',
        content: wantsWrite
          ? 'Q3 churn is 2.84% (−0.4% QoQ). Database update is staged and waiting on human approval — not auto-committed.'
          : 'Q3 Enterprise Churn Rate is 2.84% (−0.4% QoQ). Read-only analysis complete; no database writes were performed.',
        durationMs: 50
      }
    ];
  }

  if (goal.includes('mcp') || goal.includes('tool') || goal.includes('protocol')) {
    return [
      {
        type: 'THOUGHT',
        content: `Goal mentions protocol/tooling: "${goalPrompt}". Enumerate MCP primitives before choosing a transport.`,
        durationMs: 120
      },
      {
        type: 'ACTION',
        content: 'Listing MCP server capabilities over stdio.',
        toolCall: { name: 'mcp.list_tools', args: '{"transport":"stdio"}' },
        durationMs: 70
      },
      {
        type: 'OBSERVATION',
        content: 'Tools discovered: get_table_schema, execute_sql (read-only). Resources and prompts also advertised.',
        durationMs: 35
      },
      {
        type: 'THOUGHT',
        content: 'For remote deployment prefer Streamable HTTP; keep legacy HTTP+SSE only for compatibility.',
        durationMs: 100
      },
      {
        type: 'FINAL_ANSWER',
        content: 'Use stdio locally and Streamable HTTP remotely. Treat HTTP+SSE as deprecated. Gate consequential tools behind human approval.',
        durationMs: 45
      }
    ];
  }

  if (goal.includes('attention') || goal.includes('kv') || goal.includes('vllm') || goal.includes('paged')) {
    return [
      {
        type: 'THOUGHT',
        content: `Goal is systems/memory oriented: "${goalPrompt}". Compare logical tokens vs allocated PagedAttention blocks.`,
        durationMs: 110
      },
      {
        type: 'ACTION',
        content: 'Querying teaching calculator for fragmentation under block_size=16.',
        toolCall: { name: 'sim.vllm.estimate', args: '{"block_size":16,"avg_tokens":512,"streams":64}' },
        durationMs: 80
      },
      {
        type: 'OBSERVATION',
        content: 'Estimate: internal fragmentation comes from partially filled last pages; savings vs static max-length allocation can be large but must be measured on real hardware.',
        durationMs: 40
      },
      {
        type: 'FINAL_ANSWER',
        content: 'PagedAttention reduces allocation waste via fixed-size pages. Treat published savings % as workload-dependent, not a universal constant.',
        durationMs: 45
      }
    ];
  }

  return [
    {
      type: 'THOUGHT',
      content: `Custom goal received: "${goalPrompt}". Breaking it into tool-usable substeps with explicit observations.`,
      durationMs: 130
    },
    {
      type: 'ACTION',
      content: 'Calling a generic research tool for supporting facts.',
      toolCall: { name: 'tools.lookup', args: JSON.stringify({ query: goalPrompt.slice(0, 120) }) },
      durationMs: 90
    },
    {
      type: 'OBSERVATION',
      content: 'Lookup returned a short evidence snippet. Validating structure before drafting the final answer.',
      durationMs: 40
    },
    {
      type: 'THOUGHT',
      content: 'No high-risk write tools were requested. Returning a concise, citation-free teaching summary.',
      durationMs: 80
    },
    {
      type: 'FINAL_ANSWER',
      content: `Completed a ReAct loop for: "${goalPrompt}". In production, attach typed schemas, retries, and approval gates around side-effecting tools.`,
      durationMs: 50
    }
  ];
}

export const ReactAgentSimulator: React.FC = () => {
  const [goalPrompt, setGoalPrompt] = useState<string>('Analyze Q3 enterprise churn and update executive report in database');
  const [appliedGoal, setAppliedGoal] = useState<string>(goalPrompt);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [isRunning, setIsRunning] = useState<boolean>(false);

  const steps = useMemo(() => buildStepsForGoal(appliedGoal), [appliedGoal]);

  const applyGoal = () => {
    setAppliedGoal(goalPrompt.trim() || 'Summarize the ReAct loop for a generic engineering task');
    setCurrentStepIndex(0);
    setIsRunning(false);
  };

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
            Step through autonomous reasoning loops. The script adapts to your goal text (churn/SQL, MCP, vLLM, or generic).
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

      <div className="mb-6 bg-slate-50 p-4 rounded-2xl border border-slate-100">
        <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-1">
          Agent Task Objective
        </label>
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            value={goalPrompt}
            onChange={(e) => setGoalPrompt(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && applyGoal()}
            className="flex-1 bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            onClick={applyGoal}
            className="px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl"
          >
            Apply Goal
          </button>
        </div>
        <p className="text-[11px] text-slate-500 mt-2">
          Active script goal: <span className="font-mono text-slate-700">{appliedGoal}</span>
        </p>
      </div>

      <div className="space-y-3 mb-6 max-h-96 overflow-y-auto p-2">
        {steps.slice(0, currentStepIndex + 1).map((step, idx) => (
          <div
            key={`${appliedGoal}-${idx}-${step.type}`}
            className={`p-4 rounded-2xl border transition-all ${
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
