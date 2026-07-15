# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

## State labels

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

## Category labels

| Label | Meaning |
|-------|---------|
| `bug` | Something is broken |
| `enhancement` | New feature or improvement |
| `documentation` | Doc-only changes |

## Area labels

| Label | Covers |
|-------|--------|
| `area:config` | Config screen, menu, parameter adjustments |
| `area:ga` | Evolution, engine, selection, crossover, mutation, fitness |
| `area:game` | Dino, obstacles, physics, collision, rendering |
| `area:nn` | Neural network, genome, brain |
| `area:dashboard` | Matplotlib dashboard, charts |
| `area:replay` | Gameplay logs, replay player |

## Rules

- Every `bug` or `enhancement` issue must carry at least one area label. Multi-area issues get multiple.
- `documentation`, `question`, or meta issues can skip area labels.
- Every triaged issue carries exactly one state label and one category label.
