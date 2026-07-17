## Problem Statement

The replay shows the best brain in isolation. The audience can't directly compare how Gen 0 performed against Gen N — you'd need to separately replay each generation and remember what it looked like. The evolution of behavior is invisible.

## Solution

Offer a generation-comparison replay mode that plays two replays side-by-side in a split screen: Gen 0 best vs Gen N best. Both dinos jump simultaneously against the same obstacle sequence. The contrast makes the learning curve obvious.

## User Stories

1. As a demo presenter, I want to replay Gen 0 and Gen N simultaneously, so the audience sees the learning progression
2. As a developer, I want the split screen to use the existing ReplayPlayer with two log sources
3. As a demo audience, I want to see "before and after" without switching contexts

## Implementation Decisions

- LogStore already stores per-generation best logs. Compare mode picks two: earliest and latest
- The replay window splits horizontally or vertically at 50%
- Both sides use identical obstacle layout (derived from same seed)
- The gen 0 dino renders in red/semi-transparent, the final dino in standard colors
- Speed controls (1/2/4x) apply to both sides equally
- Hint text shows which generation is which

## Testing Decisions

- Test that two logs can be played simultaneously without frame sync errors
- Test that the split window renders both dinos correctly
- Existing replay tests continue to pass

## Out of Scope

- Comparing more than 2 generations at once
- Syncing obstacle positions when logs use different seeds
- Interactive selection of which generations to compare (uses earliest + latest)
