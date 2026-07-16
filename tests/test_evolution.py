import numpy as np
from game.config import Config
from ga.engine import create_population
from nn.network import NeuralNetwork
from ga.evolution import Evolution, derive_seed


class TestSeedDerivation:
    def test_derive_seed_deterministic(self):
        s1 = derive_seed(master_seed=42, generation=0)
        s2 = derive_seed(master_seed=42, generation=0)
        assert s1 == s2

    def test_derive_seed_different_per_generation(self):
        s0 = derive_seed(master_seed=42, generation=0)
        s1 = derive_seed(master_seed=42, generation=1)
        assert s0 != s1

    def test_derive_seed_different_per_master(self):
        sa = derive_seed(master_seed=42, generation=0)
        sb = derive_seed(master_seed=99, generation=0)
        assert sa != sb


class TestEvolution:
    def _make_config(self):
        config = Config()
        config.population_size = 10
        config.hidden_layer_size = 4
        config.time_cap_seconds = 0.1
        config.mutation_rate = 0.2
        config.mutation_strength = 0.1
        config.tournament_size_percent = 0.3
        config.elitism_rate = 0.1
        config.max_generations = 5
        config.plateau_generations = 10
        config.fitness_function = "survival_clearance"
        config.master_seed = 42
        return config

    def test_evolution_initializes_generation_zero(self):
        config = self._make_config()
        np.random.seed(42)
        evolution = Evolution(config)
        assert evolution.generation == 0
        assert len(evolution.population) == config.population_size
        assert evolution.best_fitness is not None

    def test_evolution_step_increments_generation(self):
        config = self._make_config()
        np.random.seed(42)
        evolution = Evolution(config)
        gen_before = evolution.generation
        evolution.step()
        assert evolution.generation == gen_before + 1

    def test_evolution_elitism_preserves_top_genomes(self):
        config = self._make_config()
        config.elitism_rate = 0.2
        np.random.seed(42)
        evolution = Evolution(config)
        elite_before = evolution.population[:2]
        evolution.step()
        for elite in elite_before:
            assert any(np.array_equal(elite, g) for g in evolution.population)

    def test_evolution_tracks_history(self):
        config = self._make_config()
        config.max_generations = 3
        np.random.seed(42)
        evolution = Evolution(config)
        evolution.step()
        evolution.step()
        assert len(evolution.history) >= 2

        for record in evolution.history:
            assert "best_fitness" in record
            assert "avg_fitness" in record
            assert "generation" in record

    def test_evolution_stops_at_max_generations(self):
        config = self._make_config()
        config.max_generations = 3
        np.random.seed(42)
        evolution = Evolution(config)
        while not evolution.is_finished():
            evolution.step()
        assert evolution.generation >= config.max_generations

    def test_evolution_plateau_detection_stops_early(self):
        config = self._make_config()
        config.max_generations = 100
        config.plateau_generations = 3
        np.random.seed(42)
        evolution = Evolution(config)
        while not evolution.is_finished() and evolution.generation < 50:
            evolution.step()
        assert evolution.generation < 50

    def test_end_condition_reports_max_generations(self):
        from ga.evolution import Evolution as Evo
        config = self._make_config()
        config.max_generations = 3
        np.random.seed(42)
        evolution = Evolution(config)
        while not evolution.is_finished():
            evolution.step()
        assert evolution.end_condition == Evo.END_MAX_GENS

    def test_end_condition_reports_plateau(self):
        from ga.evolution import Evolution as Evo
        config = self._make_config()
        config.max_generations = 100
        config.plateau_generations = 3
        np.random.seed(42)
        evolution = Evolution(config)
        while not evolution.is_finished() and evolution.generation < 50:
            evolution.step()
        assert evolution.end_condition in (Evo.END_PLATEAU, Evo.END_MAX_GENS)

    def test_stop_sets_end_condition(self):
        from ga.evolution import Evolution as Evo
        config = self._make_config()
        np.random.seed(42)
        evolution = Evolution(config)
        assert evolution.end_condition == Evo.END_RUNNING
        evolution.stop(Evo.END_QUIT)
        assert evolution.end_condition == Evo.END_QUIT
        assert evolution.is_finished()

    def test_mock_evaluator_is_injectable(self):
        from ga.evolution import Evolution as Evo
        config = self._make_config()
        config.max_generations = 3
        np.random.seed(42)

        calls = []
        def mock_evaluator(cfg, pop, seed, hidden_size):
            calls.append(1)
            fitnesses = list(range(len(pop), 0, -1))
            return fitnesses, []

        evolution = Evolution(config, evaluator=mock_evaluator)
        assert evolution.generation == 0
        while not evolution.is_finished():
            evolution.step()
        assert len(calls) >= 3
        assert evolution.end_condition == Evo.END_MAX_GENS
