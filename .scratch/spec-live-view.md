## Problem Statement

During the headless simulation, the audience only sees a matplotlib fitness chart updating. They have no visual connection to the actual dino game — the chart is abstract and doesn't show what the brains are actually learning.

## Solution

During headless evaluation, render a small Pygame overlay showing the current best brain's dino jumping over obstacles in real-time. The main game window shows the best brain getting better across generations while the dashboard shows the numbers.

## User Stories

1. As a demo audience, I want to see the dino in action during evolution, so I can connect the fitness numbers to actual behavior
2. As a demo presenter, I want the game window to show something meaningful during the headless run, not just close and reopen
3. As a developer, I want the live view to not slow down headless evaluation significantly

## Implementation Decisions

- The live view re-runs the current best genome with rendering using the same seed
- It runs at reduced frame rate (e.g., 2x speed) to minimize overhead
- The live view updates once per generation in the main loop
- The Pygame window stays open throughout the evolution (currently it closes after config screen)
- The replay at the end is still the full-quality best-brain replay

## Testing Decisions

- Test that the main Pygame window remains open during evolution (no close/reopen)
- Test that live view renders the best brain without crashing
- Existing integration tests continue to pass

## Out of Scope

- Rendering ALL brains simultaneously (too slow)
- Real-time frame-by-frame rendering during evaluation (would defeat headless purpose)
- Pausing the live view mid-generation
