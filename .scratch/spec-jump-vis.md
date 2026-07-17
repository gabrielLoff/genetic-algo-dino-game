## Problem Statement

The dino's jump intensity is a continuous brain output (0-1), but the replay shows the dino at a single position per frame — you can't visually distinguish a max-height jump from a tiny hop. The audience sees "dino jumped" but not "dino jumped softly" vs "dino jumped at full power."

## Solution

During replay, show the dino vertically scaled or with a motion trail representing jump intensity. A small hop renders the dino slightly squished vertically. A full jump renders full height. Or: draw a vertical line/trail behind the dino proportional to jump intensity from that frame.

## User Stories

1. As a demo presenter, I want to see jump intensity reflected visually, so I can explain how the brain learns to modulate jump force
2. As a demo audience, I want to instantly see which jumps were full-power vs gentle, so I understand the brain's strategy
3. As a developer, I want the visualization to degrade gracefully if intensity data isn't available

## Implementation Decisions

- In the replay frame record, brain_output is already stored. Use it as the intensity factor
- Vertical scaling: dino sprite height = base_height * (0.5 + 0.5 * brain_output). At output 0.5, dino is 75% height. At output 1.0, full height
- The scaling is purely visual in the replay renderer — no game data changes
- Optional intensity trail: a translucent vertical line behind the dino with length proportional to brain_output

## Testing Decisions

- Test that dino sprite height varies with recorded brain_output values
- Existing replay tests continue to pass

## Out of Scope

- Changing game physics. This is purely a visual effect in the replay
- Trails that persist across frames (would need multi-frame state)
