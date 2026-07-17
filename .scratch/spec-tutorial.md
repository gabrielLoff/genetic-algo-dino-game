## Problem Statement

First-time presenters face a config screen with 25+ parameters and 7 presets. The learning curve is steep — they need to understand population size, mutation rates, and fitness functions before they can see evolution in action. There's no "just show me something" option.

## Solution

Add a "Tutorial" preset designed as the first thing a new presenter runs. Small population, few generations, fast game speed. The entire evolution finishes in under 30 seconds. The preset uses survival_only fitness with a fast game speed so the audience immediately sees a dino learning to jump.

## User Stories

1. As a first-time presenter, I want a tutorial preset that runs in under 30 seconds, so I can quickly demonstrate the concept
2. As a demo audience, I want to see evolution working without waiting minutes between generations
3. As a developer, I want the tutorial preset in presets.json alongside other presets

## Implementation Decisions

- Preset added to presets.json: "Tutorial"
- Key values: population_size=20, max_generations=5, hidden_layer_size=4, game_speed_initial=600, time_cap_seconds=5, fitness_function=survival_clearance, master_seed=42
- Expected runtime: 15-30 seconds total
- Selected as the default preset when presets.json is first loaded
- Description: "Quick demo: runs in 30 seconds. Best for first-time presenters."

## Testing Decisions

- Test that tutorial preset values are correctly loaded
- Smoke test: tutorial completes in under 60 seconds
- Existing preset tests continue to pass

## Out of Scope

- Interactive tutorial walkthrough
- Animated guide overlay
