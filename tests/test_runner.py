import numpy as np
from game.runner import RunSimulation, RunResult
from game.config import Config
from ga.engine import create_population
from nn.network import NeuralNetwork


class TestRunSimulation:
    def test_run_result_stores_data(self):
        result = RunResult(
            brain_index=0,
            distance=500.0,
            obstacles_cleared=3,
            jumps_count=2,
            near_misses=1,
            time_alive=10.0,
            died_by_collision=True,
            died_by_time_cap=False,
        )
        assert result.distance == 500.0
        assert result.obstacles_cleared == 3

    def test_simulation_runs_headless(self):
        config = Config()
        config.time_cap_seconds = 2
        genome = NeuralNetwork(hidden_size=6).to_genome()
        np.random.seed(42)
        sim = RunSimulation(config, seed=42)
        result = sim.run_brain(genome, brain_index=0)
        assert isinstance(result, RunResult)
        assert result.time_alive > 0

    def test_simulation_enforces_time_cap(self):
        config = Config()
        config.time_cap_seconds = 0.05
        genome = NeuralNetwork(hidden_size=6).to_genome()
        np.random.seed(42)
        sim = RunSimulation(config, seed=42)
        result = sim.run_brain(genome, brain_index=0)
        assert result.time_alive <= 0.25  # generous margin for overhead

    def test_same_seed_produces_same_result(self):
        config = Config()
        np.random.seed(0)
        genome = NeuralNetwork(hidden_size=6).to_genome()
        sim1 = RunSimulation(config, seed=99)
        sim2 = RunSimulation(config, seed=99)
        r1 = sim1.run_brain(genome, brain_index=0)
        r2 = sim2.run_brain(genome, brain_index=0)
        assert r1.distance == r2.distance
        assert r1.obstacles_cleared == r2.obstacles_cleared

    def test_zero_speed_no_obstacles_no_death(self):
        config = Config()
        config.game_speed_initial = 0
        config.game_speed_increment = 0
        config.time_cap_seconds = 0.1
        genome = NeuralNetwork(hidden_size=6).to_genome()
        np.random.seed(42)
        sim = RunSimulation(config, seed=42)
        result = sim.run_brain(genome, brain_index=0)
        assert result.died_by_time_cap
        assert not result.died_by_collision


class TestGenerationRunner:
    def test_generation_evaluates_all_brains(self):
        from game.runner import run_generation
        config = Config()
        config.population_size = 10
        config.time_cap_seconds = 0.1
        config.fitness_function = "survival_clearance"
        population = create_population(size=10, genome_length=31)
        np.random.seed(42)
        fitnesses, results = run_generation(config, population, seed=42, hidden_size=6)
        assert len(fitnesses) == 10
        assert all(f >= 0 for f in fitnesses)

    def test_generation_includes_results(self):
        from game.runner import run_generation
        config = Config()
        config.population_size = 5
        config.time_cap_seconds = 0.05
        population = create_population(size=5, genome_length=31)
        np.random.seed(42)
        fitnesses, results = run_generation(
            config, population, seed=42, hidden_size=6
        )
        assert len(fitnesses) == 5
        assert len(results) == 5
        for r in results:
            assert isinstance(r, RunResult)
