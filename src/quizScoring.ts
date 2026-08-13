export type QuizItem = { id: string; answerIndex: number };

export function applyQuizSelection(
  selectedAnswers: Record<string, number>,
  quizId: string,
  optionIdx: number,
  locked: boolean
): Record<string, number> {
  if (locked) return selectedAnswers;
  return { ...selectedAnswers, [quizId]: optionIdx };
}

/** Percent of all questions correct, or null when nothing is answered. */
export function scoreModuleQuiz(
  quizzes: QuizItem[],
  selectedAnswers: Record<string, number>
): number | null {
  const answered = quizzes.filter(q => selectedAnswers[q.id] !== undefined);
  if (answered.length === 0) return null;
  const correct = answered.filter(q => selectedAnswers[q.id] === q.answerIndex).length;
  return Math.round((correct / quizzes.length) * 100);
}

export function submitModuleQuiz(
  locked: boolean,
  quizzes: QuizItem[],
  selectedAnswers: Record<string, number>
): { locked: true; scorePercent: number | null } {
  if (locked) return { locked: true, scorePercent: null };
  return { locked: true, scorePercent: scoreModuleQuiz(quizzes, selectedAnswers) };
}

/** Best score to keep for certificate eligibility; retakes must not lower a prior pass. */
export function nextPersistedQuizScore(previous: number | undefined, attempt: number): number {
  if (typeof previous === 'number' && Number.isFinite(previous)) {
    return Math.max(previous, attempt);
  }
  return attempt;
}

/** Fresh quiz UI when the learner opens a different module; same module keeps in-session lock. */
export function quizSessionForModule(
  sessionModuleId: number,
  moduleId: number,
  selectedAnswers: Record<string, number>,
  locked: boolean
): { moduleId: number; selectedAnswers: Record<string, number>; locked: boolean } {
  if (sessionModuleId === moduleId) {
    return { moduleId, selectedAnswers, locked };
  }
  return { moduleId, selectedAnswers: {}, locked: false };
}
