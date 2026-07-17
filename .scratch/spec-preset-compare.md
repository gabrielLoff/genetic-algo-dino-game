## Problem Statement

Presets are great shortcuts, but the presenter still has to manually run each one, then remember or screenshot the results to compare. There's no built-in "run A vs B" comparison.

## Solution

Add a preset comparison mode. The presenter selects two presets. The app runs both evolutions back to back and shows a comparison summary: which finished faster, which had higher final fitness, which plateaued, and how many generations each took.

## User Stories

1. As a demo presenter, I want to compare two presets side-by-side, so I can show how mutation rate or fitness function changes behavior
2. As a demo audience, I want to see a summary comparison after two runs, so I can understand which configuration was better
3. As a developer, I want the comparison to run both evolutions in sequence with the same dashboard

## Implementation Decisions

- A new "Compare" mode in the config screen: select two presets, then Enter starts both
- Both evolutions run sequentially (not in parallel)
- Results printed as a comparison table in the console
- Dashboard shows only the second run's chart (or averages both)
- Config: `compare_mode` boolean, default False

## Testing Decisions

- Test that two presets run without errors
- Test that comparison results contain both sets of data
- Existing integration tests continue to pass

## Out of Scope

- Running evolutions in parallel (same process, sequential)
- Statistical significance (single run each)
- Saving comparison results to file
