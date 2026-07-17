## Problem Statement

The console output uses raw numbers and technical terms (fitness, generation, plateau). A presenter who isn't a GA expert has to translate these into plain language for their audience. The demo would be more accessible with human-readable narration.

## Solution

Add a narrated mode. When enabled (via preset or config), the console prints plain-English commentary after each generation: what happened, what it means, and what to expect next. No technical jargon. Designed for a presenter to read aloud.

## User Stories

1. As a non-expert presenter, I want plain-English generation summaries, so I can read them to my audience without translating
2. As a demo audience, I want to understand what's happening without needing GA knowledge
3. As a developer, I want narration to be a toggleable config parameter

## Implementation Decisions

- Config parameter: `narrated_mode`, default False
- Narration logic inspects evolution data after each generation and produces a sentence
- Examples: "The best brain survived 5.2 seconds and cleared 3 obstacles. The average brain survived 2.1 seconds. The population is improving."
- Plateau narration: "Best fitness hasn't improved in 5 generations. Evolution may be stalling."
- Max gens narration: "We've reached 50 generations. The best brain has learned to consistently jump over obstacles."
- Console prints narration line after the fitness line, with a different prefix ("Narrator:" vs raw numbers)

## Testing Decisions

- Test that narrated output is enabled/disabled correctly
- Test that narration does not crash when evolution data is empty
- Existing tests continue to pass

## Out of Scope

- Voice synthesis / text-to-speech
- Multi-language narration
- Customizable narration templates
