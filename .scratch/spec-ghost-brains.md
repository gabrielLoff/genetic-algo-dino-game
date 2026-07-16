## Problem Statement

The replay only shows the best brain's dino — the audience sees one dino's movements in isolation. There's no visual comparison to understand what made the best brain better than others. The audience can't see "this is what NOT jumping looks like" versus "this is what learning looks like."

## Solution

Add configurable ghost brains to the replay. Based on a `ghost_mode` config parameter, the replay renders additional translucent dinos from the same generation alongside the best brain. The presenter can toggle between modes (off, worst, random, top-N) before starting the evolution. Ghosts are recorded after the generation completes by re-running the selected brains with the same seed.

## User Stories

1. As a demo presenter, I want the worst brain shown as a ghost in the replay, so the audience can visually compare a failing brain against the best
2. As a demo presenter, I want to toggle ghost mode between "off", "worst", "random", and "top N", so I can customize the comparison for different demos
3. As a demo presenter, I want ghost count configurable when using "top N" mode, so I control how many comparison brains appear
4. As a developer, I want ghosts recorded by re-running brains after generation evaluation, so the fitness loop stays clean and recording overhead is proportional to ghost count

## Implementation Decisions

- **Config parameters:**
  - `ghost_mode`: string, default `"off"`. Options: `"off"`, `"worst"`, `"random"`, `"top"`. Group: "Game". Type: str (dropdown like fitness_function). Description: "Show ghost brains in replay for visual comparison"
  - `ghost_count`: int, default `3`, min `1`, max `10`. Group: "Game". Description: "Number of ghost brains when mode is top N". Only visible/effective when ghost_mode is "top"
- **Ghost recording:** After `run_generation` returns results, inspect RunResult data to find ghost brains. For "worst": lowest fitness brain. For "random": randomly pick one. For "top": pick the next N-best (excluding the best). Call `record_run_to_log` for each ghost. Store alongside the best log.
- **Rendering:** In ReplayPlayer, render ghost dinos at 50% alpha before the best brain. Best brain renders last (on top) at 100% opacity. Ghosts get a small label at their position (e.g. "Worst", "#2").
- **Ghost log storage:** LogStore stores per-generation: best log + list of ghost logs. Cleanup removes all at session end as before.

## Testing Decisions

- Test that ghost_mode "worst" selects the brain with lowest fitness
- Test that ghost_mode "top" selects the correct N brains (not including the best)
- Test that ghost_mode "off" produces no ghost logs
- Test that ghost_count parameter is respected
- Existing replay and runner tests continue to pass
- Manual smoke: run with ghost_mode="worst", replay shows two dinos (one solid, one translucent)
