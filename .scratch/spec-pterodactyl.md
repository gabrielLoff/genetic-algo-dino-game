## Problem Statement

The dino game currently only has ground-level cactus obstacles. The brain only needs to learn one action (jump) against one type of threat. The game lacks the strategic depth of the original Chrome dino game, which has flying pterodactyls at varying heights.

## Solution

Add pterodactyl obstacles that fly at 2-3 different heights. The brain must now decide whether to jump (for low ones) or stay grounded (for high ones). This doubles the action space and makes the GA's learning process more interesting to observe.

## User Stories

1. As a demo presenter, I want pterodactyl obstacles, so the brain faces a more interesting decision space
2. As a demo audience, I want to see the brain learn to duck under some obstacles and jump over others
3. As a developer, I want pterodactyl generation to use the same obstacle manager and seed system as cacti

## Implementation Decisions

- Pterodactyls are obstacles with a `height_level` property (low, mid, high)
- The brain input gains one more value: obstacle height (normalized)
- The NN input size becomes 4 (distance, presence, speed, height)
- The obstacle manager spawns pterodactyls at configurable probability (e.g., 30% pterodactyl, 70% cactus)
- When a pterodactyl is at high height, the dino can pass under it (no collision)
- Collision: only if pterodactyl height_level is low and dino is on ground, or dino jumps into it

## Testing Decisions

- Test that pterodactyl obstacles spawn correctly with height levels
- Test that pterodactyls at high height don't collide with grounded dino
- Test that pterodactyls at low height collide with grounded dino
- Existing obstacle and runner tests continue to pass

## Out of Scope

- Ducking action (requires a second output neuron from the brain)
- Animated pterodactyl wings
- Configurable pterodactyl spawn rate per preset
