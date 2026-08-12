import React, { useMemo, useState } from 'react';
import { Globe2, Play, RotateCcw, ShieldAlert } from 'lucide-react';

type StepType = 'THOUGHT' | 'ACTION' | 'OBSERVATION' | 'APPROVAL_GATE' | 'FINAL_ANSWER';
type BrowserAction = 'navigate' | 'click' | 'type' | 'scroll' | 'extract_a11y';

interface BrowserStep {
  type: StepType;
  content: string;
  action?: { name: BrowserAction; args: string };
  observation?: { kind: 'a11y' | 'screenshot_summary'; text: string };
  requiresApproval?: boolean;
}

function buildStepsForGoal(goalPrompt: string): BrowserStep[] {
  const goal = goalPrompt.toLowerCase();
  const wantsWrite = /submit|purchase|buy|checkout|send|renew|pay/.test(goal);

  return [
    {
      type: 'THOUGHT',
      content: `Goal: "${goalPrompt}". Plan least-privilege browser tools; treat the page as an IPI surface.`,
    },
    {
      type: 'ACTION',
      content: 'Navigate to an allowlisted vendor origin.',
      action: { name: 'navigate', args: '{"url":"https://vendor.example/portal"}' },
    },
    {
      type: 'OBSERVATION',
      content: 'Sanitizer returns a typed summary — privileged planner never sees raw HTML.',
      observation: {
        kind: 'a11y',
        text: 'main > heading "License Renewal" ; textbox "Account ID" ; button "Continue"',
      },
    },
    {
      type: 'ACTION',
      content: 'Extract accessibility tree for stable role+name selectors (cheaper than a screenshot).',
      action: { name: 'extract_a11y', args: '{"root":"main"}' },
    },
    {
      type: 'OBSERVATION',
      content: 'Untrusted a11y snapshot minimized to structured fields.',
      observation: {
        kind: 'a11y',
        text: goal.includes('screenshot')
          ? '[screenshot_summary] Form visible; overlay text ignored by sanitizer policy'
          : 'textbox:Account ID ; button:Continue ; link:Support',
      },
    },
    {
      type: 'ACTION',
      content: 'Type into the account field (write-capable tool — still reversible).',
      action: { name: 'type', args: '{"selector":"textbox:Account ID","text":"ACME-001"}' },
      requiresApproval: false,
    },
    wantsWrite
      ? {
          type: 'APPROVAL_GATE' as const,
          content: 'Consequential write (submit/renew) staged — waiting on human approval before click.',
          action: { name: 'click', args: '{"selector":"button:Continue","status":"PENDING_HUMAN_APPROVAL"}' },
          requiresApproval: true,
        }
      : {
          type: 'THOUGHT' as const,
          content: 'Read-only inspection complete; no submit/purchase tool invoked.',
        },
    {
      type: 'FINAL_ANSWER',
      content: wantsWrite
        ? 'Renewal form is filled. Submit remains blocked until HITL approval — credentials never went to the raw page model path.'
        : 'Portal structure extracted via a11y observation. No consequential writes were performed.',
    },
  ];
}

export const BrowserAgentSimulator: React.FC = () => {
  const [goal, setGoal] = useState('Renew ACME license on the vendor portal');
  const [stepIndex, setStepIndex] = useState(0);
  const steps = useMemo(() => buildStepsForGoal(goal), [goal]);
  const visible = steps.slice(0, stepIndex + 1);
  const done = stepIndex >= steps.length - 1;

  const typeStyles: Record<StepType, string> = {
    THOUGHT: 'bg-slate-50 border-slate-200 text-slate-700',
    ACTION: 'bg-indigo-50 border-indigo-200 text-indigo-900',
    OBSERVATION: 'bg-amber-50 border-amber-200 text-amber-900',
    APPROVAL_GATE: 'bg-rose-50 border-rose-200 text-rose-900',
    FINAL_ANSWER: 'bg-emerald-50 border-emerald-200 text-emerald-900',
  };

  return (
    <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm my-6 space-y-6">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 pb-6 border-b border-slate-100">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-bold uppercase tracking-wider mb-2">
            <Globe2 className="w-3.5 h-3.5" />
            Browser / Computer-Use Lab
          </div>
          <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Governed Browser Agent Loop
          </h3>
          <p className="text-sm text-slate-500 mt-1 max-w-2xl">
            Teaching estimate of a Playwright-style ReAct loop: a11y observations, Dual-LLM quarantine,
            and HITL gates for consequential writes. No live browser is launched.
          </p>
        </div>
        <span className="text-[10px] font-bold uppercase tracking-wide text-amber-700 bg-amber-50 border border-amber-200 px-2 py-1 rounded-full whitespace-nowrap">
          Teaching estimate
        </span>
      </div>

      <div className="grid md:grid-cols-[1fr_auto] gap-3 items-end">
        <label className="block text-sm">
          <span className="font-medium text-slate-700">Goal prompt</span>
          <input
            value={goal}
            onChange={(e) => {
              setGoal(e.target.value);
              setStepIndex(0);
            }}
            className="mt-2 w-full border border-slate-200 rounded-xl px-3 py-2"
          />
        </label>
        <div className="flex gap-2">
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

      <div className="flex items-start gap-2 text-xs text-amber-800 bg-amber-50 border border-amber-100 rounded-xl p-3">
        <ShieldAlert className="w-4 h-4 mt-0.5 shrink-0" />
        <p>
          Page content is always <strong>untrusted</strong>. Include words like <em>submit</em> / <em>renew</em> /
          <em>purchase</em> in the goal to force an approval gate before write tools commit.
        </p>
      </div>

      <ol className="space-y-3">
        {visible.map((step, idx) => (
          <li
            key={`${step.type}-${idx}`}
            className={`rounded-2xl border p-4 text-sm ${typeStyles[step.type]}`}
          >
            <div className="flex items-center justify-between gap-2 mb-1">
              <span className="text-[10px] font-bold uppercase tracking-wider">{step.type}</span>
              {step.requiresApproval && (
                <span className="text-[10px] font-bold uppercase text-rose-700">HITL required</span>
              )}
            </div>
            <p>{step.content}</p>
            {step.action && (
              <pre className="mt-2 text-xs bg-white/70 rounded-lg px-2 py-1 overflow-x-auto">
                {step.action.name} {step.action.args}
              </pre>
            )}
            {step.observation && (
              <pre className="mt-2 text-xs bg-white/70 rounded-lg px-2 py-1 overflow-x-auto">
                [{step.observation.kind}] {step.observation.text}
              </pre>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
};
