import { describe, expect, it } from 'vitest';
import { applyQuizSelection, scoreModuleQuiz, submitModuleQuiz } from './quizScoring';

const quizzes = [
  { id: 'q1', answerIndex: 0 },
  { id: 'q2', answerIndex: 1 },
  { id: 'q3', answerIndex: 2 },
  { id: 'q4', answerIndex: 0 }
];

describe('applyQuizSelection', () => {
  it('records a choice while unlocked', () => {
    expect(applyQuizSelection({}, 'q1', 2, false)).toEqual({ q1: 2 });
  });

  it('ignores clicks after submit', () => {
    const locked = { q1: 0 };
    expect(applyQuizSelection(locked, 'q1', 3, true)).toBe(locked);
    expect(applyQuizSelection(locked, 'q2', 1, true)).toEqual({ q1: 0 });
  });
});

describe('scoreModuleQuiz', () => {
  it('returns null when nothing is answered', () => {
    expect(scoreModuleQuiz(quizzes, {})).toBeNull();
  });

  it('counts unanswered questions as wrong', () => {
    expect(scoreModuleQuiz(quizzes, { q1: 0 })).toBe(25);
  });

  it('scores a full correct set at 100', () => {
    expect(scoreModuleQuiz(quizzes, { q1: 0, q2: 1, q3: 2, q4: 0 })).toBe(100);
  });
});

describe('submitModuleQuiz', () => {
  it('records the score once and locks', () => {
    const first = submitModuleQuiz(false, quizzes, { q1: 0, q2: 1, q3: 2, q4: 1 });
    expect(first).toEqual({ locked: true, scorePercent: 75 });
  });

  it('does not overwrite the score on a second submit', () => {
    const again = submitModuleQuiz(true, quizzes, { q1: 0, q2: 1, q3: 2, q4: 0 });
    expect(again.scorePercent).toBeNull();
  });
});
