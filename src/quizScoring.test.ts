import { describe, expect, it } from 'vitest';
import {
  applyQuizSelection,
  nextPersistedQuizScore,
  quizSessionForModule,
  scoreModuleQuiz,
  submitModuleQuiz
} from './quizScoring';

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

describe('nextPersistedQuizScore', () => {
  it('stores the first attempt', () => {
    expect(nextPersistedQuizScore(undefined, 75)).toBe(75);
  });

  it('keeps a higher previous score after a weaker retake', () => {
    expect(nextPersistedQuizScore(80, 40)).toBe(80);
  });

  it('raises the stored score when a retake improves', () => {
    expect(nextPersistedQuizScore(60, 90)).toBe(90);
  });
});

describe('quizSessionForModule', () => {
  const inProgress = { q1: 0, q2: 1 };

  it('keeps answers and lock on the same module', () => {
    expect(quizSessionForModule(2, 2, inProgress, true)).toEqual({
      moduleId: 2,
      selectedAnswers: inProgress,
      locked: true
    });
  });

  it('clears answers and lock when switching modules', () => {
    expect(quizSessionForModule(2, 3, inProgress, true)).toEqual({
      moduleId: 3,
      selectedAnswers: {},
      locked: false
    });
  });
});
