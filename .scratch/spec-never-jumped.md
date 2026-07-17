## Problem Statement

The console output shows generation numbers and fitness values, but doesn't tell the presenter what's actually happening in the population. Are brains learning? Are many brains not jumping at all? The presenter has to interpret raw fitness numbers with no guidance.

## Solution

After each generation, print a "never jumped" count — how many brains in the current population never triggered a jump during their run. A high count is a diagnostic signal: the population hasn't learned anything useful, and the presenter should consider adjusting mutation rate or fitness function.

## User Stories

1. As a demo presenter, I want to see how many brains never jumped, so I can gauge if the population is learning
2. As a developer, I want the count to come from RunResult data already available, with no performance impact
3. As a demo audience, I want the presenter to explain "15 brains never jumped — they're just standing there dying"

## Implementation Decisions

- RunResult already tracks `jumps_count`. After run_generation, count results where jumps_count == 0
- Printed on the same line as fitness: "Gen 3 | best=12000.0 avg=8000.0 | never-jumped: 12"
- Evolution tracks this in history: `"never_jumped": 12`
- No config needed — always on

## Testing Decisions

- Test that count is correct for a generation with known jumps data
- Test that count is 0 when all brains jump, max when none jump
- Existing runner tests continue to pass

## Out of Scope

- Tracking brains that jumped too much (over-jumpers)
- Visualizing the count on the dashboard (console only)
