import { describe, expect, it } from 'vitest';
import { defaultProgress, parseProgress } from './progress';

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
