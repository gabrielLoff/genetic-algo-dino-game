# Genetic Algorithm parameters

The parameters that control the GA itself: population, selection, variation, fitness, and termination. These are the knobs that change how the algorithm searches, not what it searches over.

All defaults below come from `PARAM_SPECS` in `game/config.py` — that file is the source of truth for numbers, this file explains the *behavior*.

**Watch out for — config parameter source-of-truth:** all parameter metadata (default, min, max, label, group) lives in `PARAM_SPECS` in `game/config.py`. Never duplicate defaults across files. The `ConfigMenu` derives its groups from the same spec.

**Watch out for — config screen parameter steps:** step size must be range-based (not value-based) and symmetric. Integer steps need a minimum of 1 to avoid being truncated by `int()`. Without this, narrow-range integer parameters (e.g. `num_hidden_layers` 1–3) can become inert to Left/Right keys because the step truncates to 0.

### `population_size`

**Default:** 100 · **Range:** 10–1000

The number of Brains competing each Generation. Larger populations explore more of the genome space in parallel but each Generation takes proportionally longer (every Brain plays a full Run).

Trade-off: small populations converge fast but risk local optima; large populations are robust but slow. The **Tutorial** preset uses 20 for a 30-second demo, the **Speedy Evolution** preset uses 200 to show rapid convergence with selection pressure.

### `mutation_rate`

**Default:** 0.1 · **Range:** 0.0–1.0

The probability that any given gene in a child's Genome is perturbed by `gaussian_mutation` (`ga/engine.py:gaussian_mutation`). At 0.0 the GA only crosses over the existing Population; at 1.0 every gene is noisy.

**Chaos Mode** preset uses 0.8 with no elitism to demonstrate that high mutation destroys selection signal.

### `mutation_strength`

**Default:** 0.2 · **Range:** 0.01–2.0

The standard deviation of the Gaussian noise added to each mutated gene. Smaller values make small tweaks; larger values make large jumps. For the same `mutation_rate`, increasing this widens the search radius per Generation.

**Chaos Mode** preset uses 1.5 — every mutation is a big jump.

### `mutation_adaptation`

**Default:** `"none"` · **Range:** string enum: `none`, `linear_decay`, `diversity_driven`

How `mutation_strength` is adapted over the course of an Evolution. When this is `none`, the effective strength is always the base `mutation_strength`. The dashboard text panel shows the current effective strength when adaptation is active.

Each mode:

- **`none`** — effective strength is always `mutation_strength`. The default.
- **`linear_decay`** — effective strength ramps down linearly from `mutation_strength` to `mutation_strength_floor` as the Generation count approaches `max_generations`. Classic simulated-annealing pattern: explore early, exploit late.
- **`diversity_driven`** — effective strength scales with the Population's current diversity, normalized by `diversity_warning_threshold`. High diversity → full strength; low diversity → strength decays toward the floor. Self-regulating exploration.

### `mutation_strength_floor`

**Default:** 0.01 · **Range:** 0.0–0.5

The minimum effective strength when `mutation_adaptation` is active. Prevents the GA from freezing when `linear_decay` reaches zero or when `diversity_driven` collapses below the threshold.

### `tournament_size_percent`

**Default:** 0.1 · **Range:** 0.01–1.0

Fraction of the Population competing in each tournament for parent selection (`ga/engine.py:tournament_select`). With population 100 and 0.1, every tournament picks 10 random Brains and the fittest becomes a parent. Larger values increase selection pressure (only top Brains reproduce); smaller values are more permissive.

**Chaos Mode** uses 0.05 (very permissive) combined with high mutation to maximize exploration noise.

### `elitism_rate`

**Default:** 0.05 · **Range:** 0.0–0.5

Fraction of the top Brains that survive unchanged into the next Generation. At 0.0 no Brain is preserved; at 0.5 the top half of every Population carries over. High elitism protects good solutions but can lock the GA into premature convergence.

**Elite Guard** preset uses 0.4 with `mutation_rate=0.01` — observe how the Population stagnates with very low variation.

### `fitness_function`

**Default:** `"survival_clearance"` · **Range:** string enum: `survival_only`, `survival_clearance`, `near_miss`, `efficiency`

Which scoring rule `RunResult.fitness` (`game/runner.py`) applies. The selected function shapes the selection pressure: a Brain that survives but never jumps scores well under `survival_only` but poorly under `efficiency`.

Each mode:

- **`survival_only`** — fitness = raw distance traveled. Simplest signal. See **Pure Survival** preset.
- **`survival_clearance`** — fitness = distance + 100 × obstacles cleared. Adds a bonus for jumping over Obstacles. The default; rewards both longevity and obstacle-clearing.
- **`near_miss`** — fitness = distance + 50 × near-misses (defined in `runner.py` as clearing an Obstacle within 30 pixels). Rewards precision, not raw survival. See **Precise Timing** preset.
- **`efficiency`** — fitness = distance − 10 × max(0, jumps − 2 × obstacles_cleared). Penalizes wasted jumps. See **Jump Efficiency** preset.

### `crossover_operator`

**Default:** `"uniform"` · **Range:** string enum: `uniform`, `single_point`, `two_point`

How two parent Genomes combine to produce a child. Crossover dispatch happens in `ga/evolution.py:step`.

Each mode:

- **`uniform`** — each gene is independently picked from parent A or B with 50% probability. Maximum mixing; no schema preservation. The default.
- **`single_point`** — picks a split point in `[1, n-1]`, child = A's prefix + B's suffix. Preserves contiguous blocks of A's Genome.
- **`two_point`** — picks two split points, child = A's outer segments + B's middle. Alternates which parent provides the outer segments for symmetry. Preserves two contiguity regions.

### `max_generations`

**Default:** 50 · **Range:** 1–500

Hard cap on the number of Generations before the Evolution stops. The other termination path is `plateau_generations` (fitness stops improving). Whichever fires first ends the Evolution.

### `plateau_generations`

**Default:** 10 · **Range:** 1–100

If the best fitness does not improve for this many Generations in a row, the Evolution stops early. The plateau-counting happens in `ga/evolution.py:_evaluate_and_track`.

**Elite Guard** preset uses 5 (sensitive) combined with high elitism to make stagnation end the run quickly.

### `master_seed`

**Default:** `None` · **Range:** integer or `None` (random)

If set, this seed deterministically derives the per-Generation Obstacle seeds (`ga/evolution.py:derive_seed`). Same `master_seed` produces the same Obstacle sequence for every Brain in a Generation, ensuring fair fitness comparisons. With `None`, each Generation uses a random seed.

Reproducibility tip: setting `master_seed` to any integer makes the entire Evolution replayable, which is what every preset in `presets.json` does.
