import React, { useMemo, useState } from 'react';
import { Database, Play, RotateCcw, Shield } from 'lucide-react';

type StepType = 'SCHEMA' | 'DRAFT' | 'GUARD' | 'EXECUTE' | 'REPAIR' | 'COMPILE' | 'FINAL';

interface SqlStep {
  type: StepType;
  title: string;
  detail: string;
  ok?: boolean;
}

function buildSteps(question: string, injectMalicious: boolean): SqlStep[] {
  const q = question.toLowerCase();
  const draftSql = injectMalicious
    ? 'SELECT 1; DROP TABLE users'
    : q.includes('revenue') || q.includes('total')
      ? 'SELECT SUM(amount) AS total_revenue FROM orders'
      : q.includes('count') || q.includes('how many')
        ? 'SELECT COUNT(*) AS user_count FROM users'
        : 'SELECT * FROM unknown_table';

  const guardPass = !injectMalicious && !draftSql.includes('unknown_table');
  const steps: SqlStep[] = [
    {
      type: 'SCHEMA',
      title: 'MCP get_table_schema',
      detail: 'Minimizer loads DDL for users + orders only (no SELECT * FROM sqlite_master dump into the planner).',
      ok: true,
    },
    {
      type: 'DRAFT',
      title: 'Typed SQLQueryResult draft',
      detail: `confidence_score≈0.9 · sql_query="${draftSql}"`,
      ok: true,
    },
    {
      type: 'GUARD',
      title: 'Read-only SQL firewall',
      detail: guardPass
        ? 'Accepted: single SELECT/WITH, no stacking/writes/PRAGMA.'
        : injectMalicious
          ? 'Rejected: statement stacking + DROP (blueprint security control).'
          : 'Rejected: unknown_table — feed error into repair loop.',
      ok: guardPass,
    },
  ];

  if (guardPass) {
    steps.push({
      type: 'EXECUTE',
      title: 'MCP execute_readonly_sql',
      detail:
        draftSql.includes('SUM')
          ? 'Rows: [{"total_revenue": 460.5}] on analytics SQLite (stand-in for Postgres RO replica).'
          : 'Rows: [{"user_count": 3}]',
      ok: true,
    });
  } else if (!injectMalicious) {
    steps.push({
      type: 'REPAIR',
      title: 'Validation feedback → repair',
      detail: 'Repaired draft: SELECT COUNT(*) AS user_count FROM users (PydanticAI-style retry seam).',
      ok: true,
    });
    steps.push({
      type: 'EXECUTE',
      title: 'MCP execute_readonly_sql',
      detail: 'Rows: [{"user_count": 3}] after one repair.',
      ok: true,
    });
  }

  steps.push({
    type: 'COMPILE',
    title: 'DSPy BootstrapFewShot stub',
    detail: 'Metric=exact_select · compiled 2 demos from trainset · freeze instruction+demos for prod.',
    ok: true,
  });

  steps.push({
    type: 'FINAL',
    title: injectMalicious ? 'Blocked — no execution' : 'Aligned with bp_sql_agent',
    detail: injectMalicious
      ? 'Firewall stopped the write. Privileged tools never saw a successful DROP.'
      : 'Schema → typed draft → guard → RO execute (+ optional DSPy compile). CI uses deterministic propose() seams.',
    ok: !injectMalicious,
  });

  return steps;
}

const typeStyles: Record<StepType, string> = {
  SCHEMA: 'bg-slate-50 border-slate-200',
  DRAFT: 'bg-indigo-50 border-indigo-200',
  GUARD: 'bg-amber-50 border-amber-200',
  EXECUTE: 'bg-emerald-50 border-emerald-200',
  REPAIR: 'bg-violet-50 border-violet-200',
  COMPILE: 'bg-blue-50 border-blue-200',
  FINAL: 'bg-slate-100 border-slate-300',
};

export const SqlAgentSimulator: React.FC = () => {
  const [question, setQuestion] = useState('What is total order revenue?');
  const [injectMalicious, setInjectMalicious] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const steps = useMemo(() => buildSteps(question, injectMalicious), [question, injectMalicious]);
  const visible = steps.slice(0, stepIndex + 1);
  const done = stepIndex >= steps.length - 1;

  return (
    <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm my-6 space-y-6">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 pb-6 border-b border-slate-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
            <Database className="w-3.5 h-3.5" />
            PydanticAI SQL + DSPy Lab
          </div>
          <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Text-to-SQL · Firewall · Compile
          </h3>
          <p className="text-sm text-slate-500 mt-1 max-w-2xl">
            Teaching walkthrough aligned with <code className="text-xs bg-slate-100 px-1 rounded">bp_sql_agent</code>
            : schema MCP tool, typed <code className="text-xs bg-slate-100 px-1 rounded">SQLQueryResult</code>,
            read-only firewall, repair, and a DSPy BootstrapFewShot stub. No live LLM or Postgres.
          </p>
        </div>
        <span className="text-[10px] font-bold uppercase tracking-wide text-amber-700 bg-amber-50 border border-amber-200 px-2 py-1 rounded-full whitespace-nowrap">
          Teaching estimate
        </span>
      </div>

      <div className="grid md:grid-cols-[1fr_auto] gap-3 items-end">
        <label className="block text-sm">
          <span className="font-medium text-slate-700">Natural-language question</span>
          <input
            value={question}
            onChange={(e) => {
              setQuestion(e.target.value);
              setStepIndex(0);
            }}
            className="mt-2 w-full border border-slate-200 rounded-xl px-3 py-2"
          />
        </label>
        <div className="flex gap-2 flex-wrap">
          <button
            type="button"
            onClick={() => setStepIndex((i) => Math.min(i + 1, steps.length - 1))}
            disabled={done}
            className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-xl bg-indigo-600 text-white disabled:opacity-40"
          >
            <Play className="w-3.5 h-3.5" /> Step
          </button>
          <button
            type="button"
            onClick={() => setStepIndex(0)}
            className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-xl bg-slate-100 text-slate-700"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Reset
          </button>
        </div>
      </div>

      <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer select-none">
        <input
          type="checkbox"
          checked={injectMalicious}
          onChange={(e) => {
            setInjectMalicious(e.target.checked);
            setStepIndex(0);
          }}
          className="rounded border-slate-300"
        />
        <Shield className="w-4 h-4 text-rose-600" />
        Inject malicious stacked SQL (<code className="text-xs">SELECT 1; DROP TABLE users</code>)
      </label>

      <ol className="space-y-3">
        {visible.map((step, idx) => (
          <li
            key={`${step.type}-${idx}`}
            className={`rounded-2xl border p-4 text-sm ${typeStyles[step.type]} ${
              step.ok === false ? 'ring-1 ring-rose-300' : ''
            }`}
          >
            <div className="flex items-center justify-between gap-2 mb-1">
              <span className="text-[10px] font-bold uppercase tracking-wider">{step.type}</span>
              {typeof step.ok === 'boolean' && (
                <span
                  className={`text-[10px] font-bold uppercase ${
                    step.ok ? 'text-emerald-700' : 'text-rose-700'
                  }`}
                >
                  {step.ok ? 'pass' : 'block'}
                </span>
              )}
            </div>
            <p className="font-semibold text-slate-800">{step.title}</p>
            <p className="text-slate-600 mt-1">{step.detail}</p>
          </li>
        ))}
      </ol>
    </div>
  );
};
