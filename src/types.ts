export interface CodeExample {
  id: string;
  title: string;
  language: 'python' | 'typescript' | 'docker' | 'bash' | 'sql' | 'yaml';
  filename: string;
  code: string;
  explanation: string;
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  answerIndex: number;
  explanation: string;
  concept: string;
}

export interface Flashcard {
  id: string;
  term: string;
  category: string;
  definition: string;
  formulaOrCode?: string;
  keyTakeaway: string;
}

export interface LabTask {
  id: string;
  title: string;
  environment: 'WebContainers' | 'E2B Sandbox' | 'Modal GPU' | 'Docker / Render' | 'vLLM Engine';
  instructions: string[];
  expectedOutput: string;
  starterCode: CodeExample;
}

export interface CompetencyContract {
  explain: string[];
  buildAndDebug: string[];
  evidenceRequired: string[];
}

export interface ModuleData {
  id: number;
  slug: string;
  tag: string;
  title: string;
  subtitle: string;
  description: string;
  estimatedHours: number;
  objectives: string[];
  prerequisites: string[];
  competencyContract: CompetencyContract;
  sections: {
    title: string;
    content: string;
    keyFormula?: string;
    diagramType?: string;
  }[];
  codeExamples: CodeExample[];
  lab: LabTask;
  quizzes: QuizQuestion[];
  flashcards: Flashcard[];
}

export interface SystemNode {
  id: string;
  label: string;
  type: 'client' | 'gateway' | 'llm' | 'database' | 'cache' | 'security' | 'tool';
  description: string;
  latencyAvgMs: number;
  vramMb?: number;
}

export interface SystemEdge {
  from: string;
  to: string;
  label: string;
  protocol: 'gRPC' | 'HTTP/SSE' | 'Streamable HTTP' | 'stdio' | 'TCP/RDMA' | 'SQL';
}

export interface ArchitectureBlueprint {
  id: string;
  title: string;
  tagline: string;
  overview: string;
  nodes: SystemNode[];
  edges: SystemEdge[];
  securityConsiderations: string[];
  scalingBottlenecks: string[];
}

export interface UserProgress {
  completedModules: number[];
  labCompletions: Record<string, boolean>;
  quizScores: Record<string, number>; // moduleId -> score percentage
  learnedFlashcards: string[];
  codeRunHistory: number; // count of code execution simulations
  certificateGranted: boolean;
  userLevel: 'Junior ML Dev' | 'AI Engineer' | 'Senior Systems Architect' | 'Principal AI Engineer';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  source?: string;
}
