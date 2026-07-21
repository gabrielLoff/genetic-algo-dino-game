# Invert diversity-driven mutation adaptation

The original `diversity_driven` formula scaled mutation strength proportionally to diversity: `mutation_strength * (diversity / threshold)`. Low diversity → low mutation. When the population converged, mutation dropped toward its floor, locking the convergence in permanently.

Invert the ratio to `mutation_strength * (threshold / diversity)`. Low diversity → higher mutation (to restore variation); high diversity → lower mutation (population is already diverse). Clamp the result at `mutation_strength_cap` (default 1.0) to prevent explosive mutation at near-zero diversity, and at `mutation_strength_floor` (default raised to 0.05) for a minimum exploration rate.
