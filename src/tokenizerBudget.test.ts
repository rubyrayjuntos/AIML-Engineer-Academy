import { describe, expect, it } from 'vitest';
import { estimateTokens, fitsInContext, remainingOutputBudget } from './tokenizerBudget';

describe('estimateTokens', () => {
  it('uses ~4 characters per token as the teaching default', () => {
    expect(estimateTokens('abcdefghijkl')).toBe(3);
  });

  it('never returns less than 1 for non-empty text', () => {
    expect(estimateTokens('hi')).toBe(1);
  });

  it('returns 0 for empty text', () => {
    expect(estimateTokens('')).toBe(0);
  });
});

describe('fitsInContext', () => {
  it('fits when prompt plus reserved output stay under the window', () => {
    expect(fitsInContext({ promptTokens: 1000, maxContext: 8192, reservedOutput: 512 })).toBe(true);
  });

  it('does not fit when reserved output would overflow', () => {
    expect(fitsInContext({ promptTokens: 8000, maxContext: 8192, reservedOutput: 512 })).toBe(false);
  });
});

describe('remainingOutputBudget', () => {
  it('is maxContext minus prompt tokens, floored at 0', () => {
    expect(remainingOutputBudget(1000, 8192)).toBe(7192);
    expect(remainingOutputBudget(9000, 8192)).toBe(0);
  });
});
