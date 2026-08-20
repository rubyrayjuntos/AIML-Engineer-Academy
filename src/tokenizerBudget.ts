/** Teaching tokenizer: ~4 characters per token. Not a real BPE vocab. */

export function estimateTokens(text: string, charsPerToken = 4): number {
  if (!text) return 0;
  return Math.max(1, Math.ceil(text.length / charsPerToken));
}

export function remainingOutputBudget(promptTokens: number, maxContext: number): number {
  return Math.max(0, maxContext - promptTokens);
}

export function fitsInContext(args: {
  promptTokens: number;
  maxContext: number;
  reservedOutput: number;
}): boolean {
  return args.promptTokens + args.reservedOutput <= args.maxContext;
}
