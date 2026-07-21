from game.simulation import GameSimulation


_FITNESS_STRATEGIES = {
    "survival_only": lambda r: r.distance,
    "survival_clearance": lambda r: r.distance + r.obstacles_cleared * 100,
    "near_miss": lambda r: r.distance + r.near_misses * 50,
    "efficiency": lambda r: r.distance - max(0, r.jumps_count - r.obstacles_cleared * 2) * 10,
}


class RunResult:
    def __init__(self, brain_index, distance, obstacles_cleared,
                 jumps_count, near_misses, time_alive, died_by_collision, died_by_time_cap):
        self.brain_index = brain_index
        self.distance = distance
        self.obstacles_cleared = obstacles_cleared
        self.jumps_count = jumps_count
        self.near_misses = near_misses
        self.time_alive = time_alive
        self.died_by_collision = died_by_collision
        self.died_by_time_cap = died_by_time_cap

    def fitness(self, strategy="survival_clearance"):
        fn = _FITNESS_STRATEGIES.get(strategy)
        if fn is None:
            return self.distance
        return fn(self)


class RunStatsCollector:
    def __init__(self, config):
        self._ground_y = config.ground_y
        self.distance = 0.0
        self.obstacles_cleared = 0
        self.jumps_count = 0
        self.near_misses = 0
        self.died_by_collision = False
        self.time_alive = 0.0

    def __call__(self, state):
        if state.jumped:
            self.jumps_count += 1

        if state.obs_manager.collision_with(state.dino_hitbox, self._ground_y):
            self.died_by_collision = True
            return False

        for cactus in state.obstacles:
            if cactus.x + cactus.width < state.dino.x and not cactus.cleared:
                cactus.cleared = True
                self.obstacles_cleared += 1
                if abs(cactus.x + cactus.width - state.dino.x) < 30:
                    self.near_misses += 1

        self.distance += state.speed * (1.0 / 60.0)
        self.time_alive = state.time_alive + (1.0 / 60.0)
        return None

    def to_run_result(self, brain_index, config):
        died_by_time_cap = (
            self.time_alive >= config.time_cap_seconds
            and not self.died_by_collision
        )
        result = RunResult(
            brain_index=brain_index,
            distance=self.distance,
            obstacles_cleared=self.obstacles_cleared,
            jumps_count=self.jumps_count,
            near_misses=self.near_misses,
            time_alive=self.time_alive,
            died_by_collision=self.died_by_collision,
            died_by_time_cap=died_by_time_cap,
        )
        result.fitness_value = result.fitness(config.fitness_function)
        return result


class RunSimulation:
    def __init__(self, config, seed=42):
        self._config = config
        self._seed = seed

    def run_brain(self, genome, brain_index=0):
        config = self._config
        sim = GameSimulation(config, genome, self._seed)
        collector = RunStatsCollector(config)
        sim.run(observers=[collector])
        return collector.to_run_result(brain_index, config)


def run_generation(config, population, seed=42, hidden_size=6):
    sim = RunSimulation(config, seed=seed)
    fitnesses = []
    results = []
    for i, genome in enumerate(population):
        result = sim.run_brain(genome, brain_index=i)
        fitnesses.append(result.fitness_value)
        results.append(result)
    return fitnesses, results
