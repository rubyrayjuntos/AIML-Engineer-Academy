import { modulesData } from './data/curriculumData';
import { UserProgress } from './types';

export const PROGRAM_QUIZ_PASS = 60;

export function evaluateCertificateEligibility(progress: UserProgress) {
  const moduleIds = modulesData.map(m => m.id);
  const labIds = modulesData.map(m => m.lab.id);

  const modulesComplete = moduleIds.every(id => progress.completedModules.includes(id));
  const labsComplete = labIds.every(id => progress.labCompletions[id]);
  const moduleQuizzesPass = moduleIds.every(id => (progress.quizScores[String(id)] ?? -1) >= PROGRAM_QUIZ_PASS);
  const programQuizPass = (progress.quizScores.program ?? -1) >= PROGRAM_QUIZ_PASS;
  const quizzesPass = moduleQuizzesPass || programQuizPass;

  return {
    eligible: modulesComplete && labsComplete && quizzesPass,
    checks: [
      {
        id: 'modules',
        label: `Complete all ${moduleIds.length} modules`,
        done: modulesComplete,
        detail: `${progress.completedModules.length}/${moduleIds.length} marked complete`
      },
      {
        id: 'labs',
        label: 'Confirm lab evidence for every module',
        done: labsComplete,
        detail: `${labIds.filter(id => progress.labCompletions[id]).length}/${labIds.length} labs confirmed`
      },
      {
        id: 'quizzes',
        label: `Pass module quizzes or the program quiz at ≥${PROGRAM_QUIZ_PASS}%`,
        done: quizzesPass,
        detail: programQuizPass
          ? `Program quiz: ${progress.quizScores.program}%`
          : moduleQuizzesPass
            ? 'All module quizzes passed'
            : 'Quiz requirement not met yet'
      }
    ]
  };
}
