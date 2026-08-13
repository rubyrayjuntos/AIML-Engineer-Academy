import { UserProgress } from './types';

export const defaultProgress = (): UserProgress => ({
  completedModules: [],
  labCompletions: {},
  quizScores: {},
  learnedFlashcards: [],
  codeRunHistory: 0,
  certificateGranted: false,
  userLevel: 'Junior ML Dev'
});

const USER_LEVELS: ReadonlySet<UserProgress['userLevel']> = new Set([
  'Junior ML Dev',
  'AI Engineer',
  'Senior Systems Architect',
  'Principal AI Engineer'
]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

export function parseProgress(raw: unknown): UserProgress | null {
  if (!isRecord(raw)) return null;
  const completedModules = Array.isArray(raw.completedModules)
    ? raw.completedModules.filter((id): id is number => typeof id === 'number' && Number.isFinite(id))
    : [];
  const learnedFlashcards = Array.isArray(raw.learnedFlashcards)
    ? raw.learnedFlashcards.filter((id): id is string => typeof id === 'string')
    : [];
  const labCompletions: Record<string, boolean> = {};
  if (isRecord(raw.labCompletions)) {
    for (const [key, value] of Object.entries(raw.labCompletions)) {
      labCompletions[key] = Boolean(value);
    }
  }
  const quizScores: Record<string, number> = {};
  if (isRecord(raw.quizScores)) {
    for (const [key, value] of Object.entries(raw.quizScores)) {
      if (typeof value === 'number' && Number.isFinite(value)) quizScores[key] = value;
    }
  }
  const codeRunHistory =
    typeof raw.codeRunHistory === 'number' && Number.isFinite(raw.codeRunHistory)
      ? raw.codeRunHistory
      : 0;
  const userLevel = USER_LEVELS.has(raw.userLevel as UserProgress['userLevel'])
    ? (raw.userLevel as UserProgress['userLevel'])
    : 'Junior ML Dev';
  return {
    completedModules,
    labCompletions,
    quizScores,
    learnedFlashcards,
    codeRunHistory,
    certificateGranted: Boolean(raw.certificateGranted),
    userLevel
  };
}
