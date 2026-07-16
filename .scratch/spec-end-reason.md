## Problem Statement

When the evolution ends, the user sees "Evolution finished after N generations" but gets no information about WHY it ended. The evolution can stop for three different reasons — reaching max generations, fitness plateauing, or user-initiated quit — and each reason tells a different story to the demo audience.

## Solution

Add an `end_condition` property to the Evolution class that reports why the evolution stopped. Surface this information in both the console output and the matplotlib dashboard so the presenter can explain what happened.

## User Stories

1. As a demo presenter, I want to see why the evolution stopped, so I can tell the audience whether it plateaued or hit the generation limit
2. As a demo presenter, I want the dashboard to show the end reason visually, so the audience watching the fitness chart understands why it stopped
3. As a developer, I want to cleanly quit the evolution without hacking private fields, so main.py code is maintainable
4. As a developer, I want to assert the end condition in tests, so I can verify plateau detection and max-gen stopping work correctly

## Implementation Decisions

- **End condition constants:** `Evolution.END_RUNNING = "running"`, `Evolution.END_MAX_GENS = "max_generations"`, `Evolution.END_PLATEAU = "plateau"`, `Evolution.END_QUIT = "quit"`. The `end_condition` property returns the current constant.
- **Stopping early:** `evolution.stop(reason)` sets the end condition and makes `is_finished()` return True. Replaces the current `_plateau_count` hack in main.py.
- **Console output:** Prints a concise line. For plateau: `"Evolution finished in 16.8s after 12 generations (plateau — best fitness 15808.2 unchanged since gen 2)"`. For max_generations: `"Evolution finished in 45.2s after 50 generations (reached max_generations)"`. For quit: `"Evolution stopped by user after 8 generations"`.
- **Dashboard:** The text panel displays the end reason on the final update. The fitness chart draws a vertical dashed line at the plateau start generation (when available).
- **Plateau tracking:** `_plateau_count` already exists internally. The end condition detects the plateau when `_plateau_count >= plateau_generations`. The plateau start generation is stored (generation when best fitness last improved) so the message and chart can reference it.

## Testing Decisions

- Test that `end_condition` returns `END_MAX_GENS` when `max_generations` is reached
- Test that `end_condition` returns `END_PLATEAU` when fitness flatlines
- Test that `end_condition` returns `END_QUIT` after `stop("quit")` is called
- Test that `stop()` makes `is_finished()` return True
- Existing evolution and integration tests continue to pass

## Out of Scope

- Per-brain death cause reporting (already in RunResult)
- Persisting end condition to a log file
- Dashboard animation or visual effects for the ending
