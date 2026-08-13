import { describe, expect, it } from 'vitest';
import { evaluateCertificateEligibility, PROGRAM_QUIZ_PASS } from './certificateEligibility';
import { modulesData } from './data/curriculumData';
import { defaultProgress } from './progress';
import { UserProgress } from './types';

function eligibleProgress(overrides: Partial<UserProgress> = {}): UserProgress {
  return {
    ...defaultProgress(),
    completedModules: modulesData.map(m => m.id),
    labCompletions: Object.fromEntries(modulesData.map(m => [m.lab.id, true])),
    quizScores: Object.fromEntries(modulesData.map(m => [String(m.id), PROGRAM_QUIZ_PASS])),
    ...overrides
  };
}

describe('evaluateCertificateEligibility', () => {
  it('is eligible when modules, labs, and every module quiz pass', () => {
    const result = evaluateCertificateEligibility(eligibleProgress());
    expect(result.eligible).toBe(true);
    expect(result.checks.every(c => c.done)).toBe(true);
  });

  it('accepts a passing program quiz in place of module quizzes', () => {
    const result = evaluateCertificateEligibility(
      eligibleProgress({ quizScores: { program: PROGRAM_QUIZ_PASS } })
    );
    expect(result.eligible).toBe(true);
    expect(result.checks.find(c => c.id === 'quizzes')?.done).toBe(true);
  });

  it('stays locked when a module is unmarked', () => {
    const result = evaluateCertificateEligibility(
      eligibleProgress({ completedModules: modulesData.map(m => m.id).slice(1) })
    );
    expect(result.eligible).toBe(false);
    expect(result.checks.find(c => c.id === 'modules')?.done).toBe(false);
  });

  it('stays locked when a lab is unconfirmed', () => {
    const labs = Object.fromEntries(modulesData.map(m => [m.lab.id, true]));
    delete labs[modulesData[0].lab.id];
    const result = evaluateCertificateEligibility(eligibleProgress({ labCompletions: labs }));
    expect(result.eligible).toBe(false);
    expect(result.checks.find(c => c.id === 'labs')?.done).toBe(false);
  });

  it('stays locked when quizzes are below the pass bar', () => {
    const result = evaluateCertificateEligibility(
      eligibleProgress({ quizScores: { program: PROGRAM_QUIZ_PASS - 1 } })
    );
    expect(result.eligible).toBe(false);
    expect(result.checks.find(c => c.id === 'quizzes')?.done).toBe(false);
  });
});
