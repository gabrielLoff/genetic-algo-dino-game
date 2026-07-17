## Problem Statement

After running an evolution, the presenter has no way to save the results. The fitness data, best genome, and replay log are lost when the app closes. This makes the demo feel ephemeral — no data to share, analyze, or reproduce later.

## Solution

Add an export function accessible from the final screen. Pressing E exports three files to the working directory: fitness history as CSV, best genome as JSON, and the final replay log as JSON. File names include a timestamp.

## User Stories

1. As a demo presenter, I want to export fitness data as CSV, so I can plot it later or share with the audience
2. As a developer, I want to export the best genome as JSON, so I can reload it for analysis
3. As a demo presenter, I want the export to use a timestamped filename, so multiple runs don't overwrite each other

## Implementation Decisions

- Export triggered by E key press on the final screen
- CSV columns: generation, best_fitness, avg_fitness
- Best genome JSON: keys include genome (flat array), fitness, hidden_size, config snapshot
- Replay log exported as-is (already JSON)
- Files saved to working directory: `export_fitness_20260717_120000.csv`, `export_genome_*.json`, `export_replay_*.json`

## Testing Decisions

- Test that CSV contains correct structure and values
- Test that genome JSON can be reloaded into NeuralNetwork
- Existing tests continue to pass

## Out of Scope

- Configurable export directory
- Export all generations' logs (only best)
- UI file picker dialog
