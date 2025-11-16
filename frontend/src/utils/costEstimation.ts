/**
 * Cost estimation utilities
 */

export function estimateThinkingCost(tokens: number): string {
  // Rough cost estimates (approximate, may vary)
  const costPerMillionTokens = 4.0; // Example: $4/million tokens for thinking
  const cost = (tokens / 1000000) * costPerMillionTokens;
  return cost < 0.01 ? '< $0.01' : `~$${cost.toFixed(2)}`;
}
