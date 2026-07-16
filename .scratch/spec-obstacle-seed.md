## Problem Statement

The obstacle sequence changes every generation because each generation gets a different seed. A presenter who wants to show "brains improving against a fixed challenge" can't — the challenge keeps changing. There's no way to pin the obstacle layout.

## Solution

Add an `obstacle_seed` parameter to the config. When set, every brain in every generation faces the identical obstacle sequence. When None (default), obstacles vary per generation as they do today. The seed is applied in GameSimulation before np.random is used, so the obstacle generator produces the same exponential gaps and cactus sizes every time.

## User Stories

1. As a demo presenter, I want to set a fixed obstacle seed, so every generation faces the same challenge and fitness improvements reflect genuine brain learning
2. As a demo presenter, I want None (default) to keep current random behavior, so I can switch between "fixed challenge" and "varying challenge" modes
3. As a developer, I want the obstacle seed to be independent of the evolution master seed, so I can control obstacle layout without changing the evolution's randomization

## Implementation Decisions

- **Config parameter:** `obstacle_seed` added to PARAM_SPECS. Type: None/int. Default: None. Group: "Game". Label: "Obstacle Seed". Description: "Fixed seed for obstacle layout; Random if None"
- **Seeding:** GameSimulation.run() checks config.obstacle_seed. If not None, uses `np.random.seed(config.obstacle_seed)` instead of `np.random.seed(self._seed)`
- **No other changes:** The per-generation evolution seed still controls population initialization and mutation randomness. Only obstacle generation is affected

## Testing Decisions

- Test that setting obstacle_seed produces identical obstacle positions across two Simulation runs with different brain genomes
- Test that obstacle_seed=None uses the simulation seed as before
- Existing tests pass unchanged
