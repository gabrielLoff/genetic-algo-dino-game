import numpy as np
from game.dino import Dino
from game.obstacle import GameSpeed, ObstacleManager, aabb_collides
from game.brain import Brain, JumpController
from ga.engine import compute_fitness
from game.config import Config


class RunResult:
    def __init__(self, brain_index, fitness, distance, obstacles_cleared,
                 jumps_count, near_misses, time_alive, died_by_collision, died_by_time_cap):
        self.brain_index = brain_index
        self.fitness = fitness
        self.distance = distance
        self.obstacles_cleared = obstacles_cleared
        self.jumps_count = jumps_count
        self.near_misses = near_misses
        self.time_alive = time_alive
        self.died_by_collision = died_by_collision
        self.died_by_time_cap = died_by_time_cap


class RunSimulation:
    def __init__(self, config, seed=42):
        self._config = config
        self._seed = seed

    def run_brain(self, genome, brain_index=0):
        np.random.seed(self._seed)

        config = self._config
        dino = Dino(ground_y=config.window_height - 80, collision_inset=config.collision_inset)
        game_speed = GameSpeed(
            initial=config.game_speed_initial,
            max_speed=config.game_speed_max,
            increment=config.game_speed_increment,
        )
        obs_manager = ObstacleManager(
            screen_width=config.window_width,
            ground_y=config.window_height - 80,
            gap_mean=config.obstacle_gap_mean,
            min_gap=config.obstacle_min_gap,
            gap_decay=config.obstacle_gap_decay,
        )
        brain = Brain(genome, hidden_size=config.hidden_layer_size)
        jump_ctrl = JumpController(
            threshold=0.5,
            cooldown_frames=config.jump_cooldown_frames,
        )

        dt = 1.0 / 60.0
        time_alive = 0.0
        total_distance = 0.0
        obstacles_cleared = 0
        jumps_count = 0
        near_misses = 0
        died_by_collision = False
        died_by_time_cap = False

        while True:
            game_speed.update(dt)
            speed = game_speed.current

            obs_manager.update(speed, dt)

            distance_to_next = obs_manager.distance_to_next(dino.x, config.window_width)
            obstacle_present = 1.0 if obs_manager.obstacle_present(dino.x) else 0.0
            normalized_distance = min(distance_to_next / config.window_width, 1.0)
            normalized_speed = speed / config.game_speed_max

            inputs = np.array([normalized_distance, obstacle_present, normalized_speed])
            brain_output = brain.evaluate(inputs)

            if jump_ctrl.should_jump(brain_output):
                dino.jump(brain_output, config.dino_max_jump_velocity)
                jumps_count += 1

            dino.update(dt, config.dino_gravity)
            jump_ctrl.update()

            if obs_manager.collision_with(dino.hitbox(), config.window_height - 80):
                died_by_collision = True
                break

            for cactus in obs_manager.obstacles:
                if cactus.x + cactus.width < dino.x and not cactus.cleared:
                    cactus.cleared = True
                    obstacles_cleared += 1
                    if abs(cactus.x + cactus.width - dino.x) < 30:
                        near_misses += 1

            time_alive += dt
            total_distance += speed * dt

            if time_alive >= config.time_cap_seconds:
                died_by_time_cap = True
                break

        fitness = compute_fitness(
            distance=total_distance,
            obstacles_cleared=obstacles_cleared,
            near_misses=near_misses,
            jumps_count=jumps_count,
            strategy=config.fitness_function,
        )

        return RunResult(
            brain_index=brain_index,
            fitness=fitness,
            distance=total_distance,
            obstacles_cleared=obstacles_cleared,
            jumps_count=jumps_count,
            near_misses=near_misses,
            time_alive=time_alive,
            died_by_collision=died_by_collision,
            died_by_time_cap=died_by_time_cap,
        )


def run_generation(config, population, seed=42, hidden_size=6):
    sim = RunSimulation(config, seed=seed)
    fitnesses = []
    for i, genome in enumerate(population):
        result = sim.run_brain(genome, brain_index=i)
        fitnesses.append(result.fitness)
    return fitnesses


def run_generation_with_results(config, population, seed=42, hidden_size=6):
    sim = RunSimulation(config, seed=seed)
    fitnesses = []
    results = []
    for i, genome in enumerate(population):
        result = sim.run_brain(genome, brain_index=i)
        fitnesses.append(result.fitness)
        results.append(result)
    return fitnesses, results
