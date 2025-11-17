/**
 * UI Configuration Constants
 *
 * Centralized UI constants for timeouts, spacing, colors, and component limits.
 * Modify these values to adjust UI behavior across the application.
 */

// ============ Timeouts & Durations ============

export const TIMEOUTS = {
  /** Duration to show success messages before auto-hiding (milliseconds) */
  SUCCESS_MESSAGE: 3000,

  /** Duration to show error messages before auto-hiding (milliseconds) */
  ERROR_MESSAGE: 5000,

  /** Delay before showing tooltips (milliseconds) */
  TOOLTIP_DELAY: 150,
} as const;

// ============ Spacing & Sizing ============

export const SPACING = {
  /** Extra small spacing */
  XS: '4px',
  /** Small spacing */
  SM: '8px',
  /** Medium spacing */
  MD: '12px',
  /** Large spacing */
  LG: '16px',
  /** Extra large spacing */
  XL: '24px',
} as const;

export const FONT_SIZE = {
  /** Small text (help text, captions) */
  SM: '12px',
  /** Regular text */
  MD: '13px',
  /** Medium text */
  BASE: '14px',
  /** Large text (headings) */
  LG: '16px',
} as const;

// ============ Colors ============

export const COLORS = {
  /** Success state color */
  SUCCESS: '#2e7d32',

  /** Warning state color */
  WARNING: '#e65100',

  /** Muted text color */
  MUTED: '#666',

  /** Lighter muted text */
  MUTED_LIGHT: '#888',

  /** Placeholder/disabled text */
  DISABLED: '#999',
} as const;

// ============ Skeleton Loader ============

export const SKELETON = {
  /** Width for title skeleton */
  TITLE_WIDTH: '40%',

  /** Width for primary text skeleton */
  TEXT_WIDTH_PRIMARY: '20%',

  /** Width for secondary text skeleton */
  TEXT_WIDTH_SECONDARY: '15%',

  /** Margin bottom for skeleton elements */
  MARGIN_BOTTOM: '10px',
} as const;

// ============ Thinking Configuration ============

export const THINKING = {
  /** Default thinking budget in tokens (for providers like Claude) */
  DEFAULT_BUDGET_TOKENS: 2000,

  /** Minimum allowed thinking budget */
  MIN_BUDGET_TOKENS: 500,

  /** Maximum allowed thinking budget */
  MAX_BUDGET_TOKENS: 10000,

  /** Step size for budget token slider */
  BUDGET_STEP: 500,

  /** Default reasoning effort (for providers like OpenAI) */
  DEFAULT_EFFORT: 'medium' as const,

  /** Default summary setting */
  DEFAULT_SUMMARY: 'auto' as const,
} as const;

// ============ Cost Estimation ============

export const COST = {
  /** Approximate cost per million tokens for thinking (USD) */
  PER_MILLION_TOKENS: 4.0,

  /** Minimum cost to display (below this shows "< $0.01") */
  MIN_DISPLAY: 0.01,

  /** Number of decimal places for cost display */
  DECIMAL_PLACES: 2,
} as const;

/**
 * Estimate the cost of thinking tokens
 * @param tokens - Number of thinking tokens
 * @returns Formatted cost string
 */
export function estimateThinkingCost(tokens: number): string {
  const cost = (tokens / 1000000) * COST.PER_MILLION_TOKENS;
  return cost < COST.MIN_DISPLAY ? `< $${COST.MIN_DISPLAY.toFixed(2)}` : `~$${cost.toFixed(COST.DECIMAL_PLACES)}`;
}
