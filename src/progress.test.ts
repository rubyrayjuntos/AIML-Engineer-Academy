import { describe, expect, it } from 'vitest';
import { applyRecordedQuizScore, defaultProgress, parseProgress } from './progress';

describe('parseProgress', () => {
  it('returns null for non-objects', () => {
    expect(parseProgress(null)).toBeNull();
    expect(parseProgress('{"completedModules":[]}')).toBeNull();
    expect(parseProgress(42)).toBeNull();
  });

  it('accepts a well-formed snapshot', () => {
    const raw = {
      completedModules: [1, 2],
      labCompletions: { lab1: true },
      quizScores: { '1': 80, program: 70 },
      learnedFlashcards: ['fc1'],
      codeRunHistory: 3,
      certificateGranted: true,
      userLevel: 'AI Engineer'
    };
    expect(parseProgress(raw)).toEqual(raw);
  });

  it('falls back when arrays and records have the wrong shape', () => {
    const parsed = parseProgress({
      completedModules: { '0': 1 },
      labCompletions: ['lab1'],
      quizScores: { '1': '80', program: 90, bad: Number.NaN },
      learnedFlashcards: [1, 'ok'],
      codeRunHistory: '9',
      certificateGranted: 'yes',
      userLevel: 'Overlord'
    });
    expect(parsed).toEqual({
      ...defaultProgress(),
      quizScores: { program: 90 },
      learnedFlashcards: ['ok'],
      certificateGranted: true
    });
  });
});

describe('applyRecordedQuizScore', () => {
  it('does not let a weaker retake replace a passing module score', () => {
    const before = {
      ...defaultProgress(),
      quizScores: { '1': 80 },
      certificateGranted: true
    };
    const after = applyRecordedQuizScore(before, 1, 40);
    expect(after).toBe(before);
    expect(after.quizScores['1']).toBe(80);
    expect(after.certificateGranted).toBe(true);
  });

  it('records an improved retake', () => {
    const before = { ...defaultProgress(), quizScores: { '1': 50 } };
    const after = applyRecordedQuizScore(before, 1, 90);
    expect(after.quizScores['1']).toBe(90);
    expect(after.certificateGranted).toBe(false);
  });
});
