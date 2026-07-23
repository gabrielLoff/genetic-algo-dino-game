# Game parameters

The world the brains live in: world scroll speed, obstacle layout, dino physics, window size, and what gets recorded for replay. Most of these don't affect the GA itself — they shape what fitness landscape the brains are climbing.

### `game_speed_initial`

**Default:** 400 · **Range:** 50–2000

Starting scroll speed in pixels per second. The world starts at this speed and ramps up toward `game_speed_max` over the course of a Run.

**Tutorial** preset uses 600 for a faster demo.

### `game_speed_max`

**Default:** 1000 · **Range:** 100–5000

Maximum scroll speed the world reaches. The speed cap is the upper bound on difficulty.

### `game_speed_increment`

**Default:** 2 · **Range:** 0.1–50

Pixels-per-second-per-second that the scroll speed ramps by. Larger values mean the world speeds up faster within a Run.

### `obstacle_min_gap`

**Default:** 200 · **Range:** 50–1000

Minimum pixel distance between consecutive Obstacles, enforced in `ObstacleManager.spawn` (`game/obstacle.py`) when the exponential gap distribution would otherwise produce smaller gaps.

### `obstacle_gap_mean`

**Default:** 500 · **Range:** 100–2000

Mean of the exponential distribution that determines inter-Obstacle distance. Larger values mean sparser Obstacles.

**Precise Timing** preset uses 600 (sparser gaps, more time to react).

### `obstacle_gap_decay`

**Default:** 0.001 · **Range:** 0.0–0.1

How fast the effective gap mean shrinks over time within a Run. With 0.0 the obstacle spacing is constant; with larger values the world gets more crowded as the Run progresses. Currently a small per-frame multiplier — most users leave this at default.

### `pterodactyl_probability`

**Default:** 0.3 · **Range:** 0.0–1.0

Probability a spawned Obstacle is a Pterodactyl (variable-height flying Obstacle) instead of a ground-level Cactus. At 0.0 all Obstacles are cacti; at 1.0 all are pterodactyls.

Brains that learn to handle both Obstacle types are more robust.

### `diversity_warning_threshold`

**Default:** 0.05 · **Range:** 0.0–1.0

Threshold for the low-diversity warning on the dashboard. When the Population's mean pairwise genome distance drops below this, the dashboard highlights the Generation as a convergence point. The diversity metric is mean pairwise Euclidean distance normalized by genome length.

Also used as the normalization constant for `diversity_driven` mutation adaptation — see `docs/configs/genetic-algorithm.md § mutation_adaptation`.

### `time_cap_seconds`

**Default:** 30 · **Range:** 1–300

Maximum duration of a single Run. A Brain that never hits an Obstacle still ends at this cap, preventing an immortal Brain from stalling the Generation.

**Tutorial** uses 5 (fast demo). **Precise Timing** and **Jump Efficiency** use 60 (longer runs to test precision).

### `jump_cooldown_frames`

**Default:** 5 · **Range:** 1–30

Minimum Frames between consecutive jumps (`game/brain.py:ActionController`). Prevents the Brain from spamming jumps for free height. Smaller values let the Brain attempt more jumps per second.

**Jump Efficiency** preset uses 3 to allow more jumps but penalizes them via the fitness function.

### `collision_inset`

**Default:** 0.15 · **Range:** 0.0–0.5

Fraction of the sprite's bounding box removed from each side for the collision hitbox. The actual shrink happens in `inset_hitbox` (`game/geometry.py:1`) which `Dino.hitbox` (`game/dino.py:34`) calls. Larger values give the dino a smaller, more forgiving collision box; 0.0 is full-bbox collision.

This is one of the most-magic parameters — small changes make the game feel dramatically easier or harder.

**Watch out for:** the Dino uses bottom-aligned y (feet on ground), and `Cactus` uses top-aligned y, while `Pterodactyl` uses its own `sprite_top`. The hitbox math in `inset_hitbox` handles both, but the coordinate convention leaks into the collision tests. See the [AGENTS.md gotcha on hitbox coordinate systems](../AGENTS.md).

### `dino_gravity`

**Default:** 2000 · **Range:** 100–5000

Downward acceleration of the Dino in pixels per second squared, applied in `Dino.update` (`game/dino.py:50`). Higher gravity makes jumps feel snappier and shorter.

### `dino_max_jump_velocity`

**Default:** −600 · **Range:** −2000 to −10

Upward velocity at full jump (negative because pygame y is inverted), applied in `Dino.jump` (`game/dino.py`). The Brain's Output is a 0–1 value; the actual velocity at jump time is `output × dino_max_jump_velocity`. More-negative values give taller jumps.

### `ground_height`

**Default:** 80 · **Range:** 40–200

Height of the ground area at the bottom of the screen. The ground occupies the bottom `ground_height` pixels of the window; the playable area is `window_height − ground_height`. Affects the dino's ground_y and the visual feel of the world.

### `window_width`

**Default:** 1024 · **Range:** 400–2560

Game window width in pixels. Larger widths give the config screen and replay more room to render parameter descriptions and overlays.

### `window_height`

**Default:** 640 · **Range:** 200–1440

Game window height in pixels. Larger heights give the config screen and replay more room to render parameter descriptions and overlays.

### `obstacle_seed`

**Default:** `None` · **Range:** integer or `None` (random)

Fixed seed for the Obstacle layout. If set, every Generation gets the same Obstacle sequence; if `None`, each Generation uses a fresh random seed. Different from `master_seed` (which controls per-Generation seed derivation); `obstacle_seed` directly overrides the per-Generation seed in `GameSimulation.run` (`game/simulation.py:29`, the `if self._config.obstacle_seed is not None` branch).

Useful for debugging: lock the Obstacle layout so a Brain's performance is reproducible across runs.

### `ghost_mode`

**Default:** `"off"` · **Range:** string enum: `off`, `worst`, `random`, `top`

Which other Brains to overlay on the Replay alongside the best Brain. Adds visual context for comparing brain behavior in the same Obstacle sequence.

Each mode:

- **`off`** — no ghosts. Default.
- **`worst`** — show the worst-scoring Brain of the Generation.
- **`random`** — show a random non-best Brain of the Generation.
- **`top`** — show the top-K runners-up (K = `ghost_count`).

### `ghost_count`

**Default:** 3 · **Range:** 1–10

Number of ghost Brains when `ghost_mode=top`. Ignored for other modes.

### `stop_on_first_survivor`

**Default:** `False` · **Range:** boolean

When enabled, evolution stops as soon as any Brain survives the full time cap without colliding. This is useful for demonstrations — you know the problem is "solved" when a Brain makes it to the end. When disabled (default), evolution always runs through all generations or until a plateau.

### `fullscreen`

**Default:** `False` · **Range:** boolean

Run the game in borderless fullscreen for presentations. The window covers the entire display; there's no title bar or window chrome. Useful for talks and demos.
