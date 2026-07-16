## Problem Statement

The config screen has 20+ adjustable parameters, but configuring them to demonstrate specific genetic algorithm behaviors requires deep knowledge of what each parameter does. A presenter wanting to show "fast vs slow convergence" or "different fitness function effects" must manually adjust many sliders — error-prone and slow during a live demo.

## Solution

Add a preset system: named, pre-configured parameter sets that demonstrate specific GA behaviors. The presenter selects a preset from a list in the config screen, parameters update instantly, and a description explains what the preset demonstrates. Presets are defined in `presets.json` at the repo root and can be edited without touching code.

## User Stories

1. As a demo presenter, I want to select a "Speedy Evolution" preset with one keypress, so I can quickly show how a large population converges fast
2. As a demo presenter, I want to switch between fitness function presets, so I can demonstrate how near-miss scoring produces different jumping behavior than survival-only
3. As a demo presenter, I want to load a "Chaos Mode" preset, so the audience can see wildly diverse brains producing entertaining replays
4. As a demo presenter, I want a description displayed for each preset, so I can explain to the audience what this configuration demonstrates
5. As a demo presenter, I want selecting a preset to reset all parameters to that preset's values, so there are no leftover tweaks from a previous demo
6. As a demo presenter, I want the "Default" preset to reload my baseline config.json, so I can return to my starting point at any time
7. As a developer, I want presets defined in a JSON file, so I can add or modify presets without touching Python code
8. As a demo presenter, I want a confirmation prompt before loading a preset, so I don't accidentally lose my manual parameter changes

## Presets to ship

| Preset | Demonstrates | Key overrides |
|--------|-------------|---------------|
| Default | Baseline behavior, reloads config.json | none — reloads from file or hardcoded defaults |
| Speedy Evolution | Fast convergence with large population | pop=200, mutation=0.3, tournament=0.3, max_gens=20 |
| Precise Timing | Near-miss rewards brains that jump at the last moment | fitness=near_miss, time_cap=60, obstacle_gap_mean=600 |
| Jump Efficiency | Brains penalized for jumping unnecessarily | fitness=efficiency, time_cap=60, cooldown=3 |
| Pure Survival | Simplest fitness — just distance traveled | fitness=survival_only, time_cap=30 |
| Chaos Mode | High mutation, no elitism — wild diversity | mutation_rate=0.8, mutation_strength=1.5, elitism=0.0, tournament=0.05 |
| Elite Guard | High elitism keeps best — observe stagnation | elitism=0.4, pop=50, mutation=0.01, plateau_gens=5 |

## Implementation Decisions

- **Preset file:** `presets.json` at repo root. Array of objects with `name`, `description`, and `params` (flat dict of optional parameter overrides)
- **Loading:** Loaded at app startup. If `presets.json` is missing, the "Default" preset still works (reloads from config.json or hardcoded defaults). Other presets are simply unavailable
- **Config screen integration:** A new cycler at the top of the config screen labeled "Preset". Left/right arrows cycle through available presets. Enter loads the selected preset with confirmation prompt
- **Full replacement on load:** Loading a preset resets ALL parameters to the preset's values. "Default" reloads from config.json (or PARAM_SPECS fallback). A brief overlay text confirms the load
- **Confirmation:** When the user presses Enter on a preset, a prompt appears: "Load preset X? Enter=confirm, Esc=cancel"
- **Description display:** The preset's description renders in the same area where individual parameter descriptions currently appear

## Testing Decisions

- Test that loading a preset updates all config values correctly
- Test that "Default" reloads from config.json (or hardcoded defaults when file is missing)
- Test that missing presets.json does not crash the app
- Test that confirmation prompt prevents accidental load
- Test that left/right cycles through presets and the description updates
- Existing config and config screen tests continue to pass

## Out of Scope

- Saving custom presets from the config screen
- Preset categories or folders
- Automatic preset recommendation based on previous runs

## Further Notes

Presets with fixed `master_seed` values produce reproducible results — useful for the presenter to pre-record or practice a specific demo flow.
