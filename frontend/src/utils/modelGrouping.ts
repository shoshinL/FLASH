/**
 * Model grouping utilities
 */

import { MODEL_GROUPS, EMBEDDING_MODEL_GROUPS } from '../constants/modelGroups';

export function groupModels(
  provider: string,
  models: string[],
  isEmbedding: boolean = false
): Record<string, string[]> {
  const groups = isEmbedding ? EMBEDDING_MODEL_GROUPS : MODEL_GROUPS;
  const providerGroups = groups[provider];

  if (!providerGroups) {
    // No grouping config for this provider - return all as "Other Models"
    return { "Other Models": models };
  }

  const grouped: Record<string, string[]> = {};
  const ungrouped: string[] = [];

  // Categorize models into their groups
  for (const model of models) {
    let found = false;
    for (const [groupName, groupModels] of Object.entries(providerGroups)) {
      // Check if model matches any pattern in the group
      if (groupModels.some(pattern =>
        model === pattern ||
        model.startsWith(pattern.replace(':latest', '')) ||
        model.includes(pattern)
      )) {
        if (!grouped[groupName]) {
          grouped[groupName] = [];
        }
        grouped[groupName].push(model);
        found = true;
        break;
      }
    }
    if (!found) {
      ungrouped.push(model);
    }
  }

  // Add ungrouped models to "Other Models" if any exist
  if (ungrouped.length > 0) {
    grouped["Other Models"] = ungrouped;
  }

  return grouped;
}
