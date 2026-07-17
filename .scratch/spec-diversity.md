## Problem Statement

The dashboard shows best and average fitness, but the audience can't tell if the population is becoming too similar. Premature convergence is a key GA concept — all brains become nearly identical, and evolution stalls. The dashboard doesn't warn about this.

## Solution

Track and display a population diversity metric each generation. When diversity drops below a threshold, show a warning on the dashboard. The metric is average pairwise genome distance (mean absolute difference between all genome pairs in the population).

## User Stories

1. As a demo presenter, I want to see population diversity on the dashboard, so I can explain premature convergence
2. As a demo audience, I want a visual warning when diversity is low, so I understand why evolution is stalling
3. As a developer, I want the diversity metric computed efficiently from the existing population array

## Implementation Decisions

- Diversity metric: mean of all pairwise Euclidean distances between genomes, normalized by genome length
- Computed in Evolution after each generation
- Stored in history: `"diversity": 0.42`
- Dashboard: new line in the text panel: "Diversity: 0.42"
- Warning threshold: diversity < 0.05 → panel shows "⚠ Low diversity — population converging"
- Config parameter: `diversity_warning_threshold`, default 0.05

## Testing Decisions

- Test that diversity is 0 for identical populations
- Test that diversity is >0 for random populations
- Test that diversity decreases as evolution proceeds
- Existing integration tests continue to pass

## Out of Scope

- Multiple diversity metrics (Shannon entropy, etc.)
- Diversity history chart (just the current value)
- Automatic intervention when diversity is low (just a warning)
