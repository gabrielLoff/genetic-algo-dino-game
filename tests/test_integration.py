import numpy as np
from game.config import Config
from ga.evolution import Evolution


def test_fitness_improves_over_five_generations_survival_clearance():
    config = Config()
    config.output_size = 1
    config.population_size = 30
    config.hidden_layer_size = 6
    config.max_generations = 5
    config.plateau_generations = 20
    config.time_cap_seconds = 5
    config.fitness_function = "survival_clearance"
    config.pterodactyl_probability = 0.0
    config.master_seed = 42

    np.random.seed(42)
    evolution = Evolution(config)

    gen0_best = evolution.history[-1]["best_fitness"]
    gen_bests = [gen0_best]

    while not evolution.is_finished():
        evolution.step()
        gen_bests.append(evolution.history[-1]["best_fitness"])

    assert evolution.generation >= 5
    assert evolution.best_fitness > gen0_best, (
        f"Fitness did not improve: gen0={gen0_best:.1f}, gen{evolution.generation}={evolution.best_fitness:.1f}"
    )


def test_fitness_improves_over_five_generations_survival_only():
    config = Config()
    config.output_size = 1
    config.population_size = 30
    config.hidden_layer_size = 6
    config.max_generations = 5
    config.plateau_generations = 20
    config.time_cap_seconds = 5
    config.fitness_function = "survival_only"
    config.pterodactyl_probability = 0.0
    config.master_seed = 7

    np.random.seed(7)
    evolution = Evolution(config)

    gen0_best = evolution.history[-1]["best_fitness"]

    while not evolution.is_finished():
        evolution.step()

    assert evolution.generation >= 5
    assert evolution.best_fitness > gen0_best, (
        f"Fitness did not improve with survival_only: gen0={gen0_best:.1f}, gen{evolution.generation}={evolution.best_fitness:.1f}"
    )
