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


def _make_config():
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


class TestEvolution:
    def _make_config(self):
        return _make_config()

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


class TestDiversity:
    def test_diversity_zero_for_identical_population(self):
        config = _make_config()
        mock_pop = [np.ones(37) for _ in range(10)]
        config.population_size = len(mock_pop)
        np.random.seed(42)

        calls = []
        def mock_evaluator(cfg, pop, seed, hidden_size):
            calls.append(1)
            return list(range(len(pop), 0, -1)), []

        evolution = Evolution(config, evaluator=mock_evaluator)
        evolution.population = mock_pop
        diversity = evolution._compute_diversity()
        assert diversity == 0.0

    def test_diversity_positive_for_random_population(self):
        from ga.engine import create_population
        config = _make_config()
        np.random.seed(42)
        pop = create_population(size=10, hidden_size=config.hidden_layer_size, input_size=4)

        calls = []
        def mock_evaluator(cfg, p, seed, hidden_size):
            calls.append(1)
            return [1.0] * len(p), []

        evolution = Evolution(config, evaluator=mock_evaluator)
        evolution.population = pop
        diversity = evolution._compute_diversity()
        assert diversity > 0.0

    def test_diversity_stored_in_history(self):
        config = _make_config()
        config.max_generations = 3
        np.random.seed(42)

        evolution = Evolution(config)
        assert "diversity" in evolution.history[-1]
        while not evolution.is_finished():
            evolution.step()
        for record in evolution.history:
            assert "diversity" in record
            assert record["diversity"] >= 0.0


class TestMutationAdaptation:
    def test_effective_strength_none_returns_base(self):
        config = _make_config()
        config.mutation_adaptation = "none"
        config.mutation_strength = 0.5
        evolution = Evolution(config)
        strength = evolution._effective_mutation_strength(diversity=0.1)
        assert strength == 0.5

    def test_effective_strength_linear_decay_decreases_over_generations(self):
        config = _make_config()
        config.mutation_adaptation = "linear_decay"
        config.mutation_strength = 0.5
        config.mutation_strength_floor = 0.01
        config.max_generations = 10
        evolution = Evolution(config)
        strength_g0 = evolution._effective_mutation_strength(diversity=0.1)
        evolution.generation = 5
        strength_g5 = evolution._effective_mutation_strength(diversity=0.1)
        assert strength_g5 < strength_g0

    def test_effective_strength_linear_decay_respects_floor(self):
        config = _make_config()
        config.mutation_adaptation = "linear_decay"
        config.mutation_strength = 0.5
        config.mutation_strength_floor = 0.2
        config.max_generations = 10
        evolution = Evolution(config)
        evolution.generation = 10
        strength = evolution._effective_mutation_strength(diversity=0.1)
        assert strength >= 0.2

    def test_effective_strength_diversity_driven_scales(self):
        config = _make_config()
        config.mutation_adaptation = "diversity_driven"
        config.mutation_strength = 0.5
        config.diversity_warning_threshold = 0.1
        config.mutation_strength_floor = 0.01
        evolution = Evolution(config)
        high = evolution._effective_mutation_strength(diversity=0.2)
        low = evolution._effective_mutation_strength(diversity=0.03)
        assert low > high

    def test_effective_strength_diversity_driven_respects_floor(self):
        config = _make_config()
        config.mutation_adaptation = "diversity_driven"
        config.mutation_strength = 0.5
        config.diversity_warning_threshold = 0.1
        config.mutation_strength_floor = 0.1
        evolution = Evolution(config)
        strength = evolution._effective_mutation_strength(diversity=0.001)
        assert strength >= 0.1

    def test_effective_strength_diversity_driven_respects_cap(self):
        config = _make_config()
        config.mutation_adaptation = "diversity_driven"
        config.mutation_strength = 0.5
        config.diversity_warning_threshold = 0.1
        config.mutation_strength_cap = 1.0
        config.mutation_strength_floor = 0.1
        evolution = Evolution(config)
        strength = evolution._effective_mutation_strength(diversity=0.001)
        assert strength <= 1.0
        assert strength > 0.1


class TestWeightDiff:
    def test_identical_genomes_all_zero(self):
        from ga.evolution import compute_weight_diff
        genome = [0.1] * 37
        diff = compute_weight_diff(genome, genome, hidden_size=6)
        assert all(info["count"] == 0 for info in diff.values())

    def test_single_layer_groups(self):
        from ga.evolution import compute_weight_diff
        old = [0.0] * 37
        new = [0.0] * 37
        new[0] = 100.0
        diff = compute_weight_diff(old, new, hidden_size=6)
        assert "hidden_1_weights" in diff
        assert "hidden_1_bias" in diff
        assert "output_weights" in diff
        assert "output_bias" not in diff
        assert diff["hidden_1_weights"]["count"] >= 1

    def test_two_layer_groups(self):
        from ga.evolution import compute_weight_diff
        old = [0.0] * 79
        new = [0.0] * 79
        new[60] = 100.0
        diff = compute_weight_diff(old, new, hidden_size=6, num_hidden_layers=2)
        assert "hidden_1_weights" in diff
        assert "hidden_2_weights" in diff
        assert "output_weights" in diff

    def test_three_layer_groups(self):
        from ga.evolution import compute_weight_diff
        old = [0.0] * 121
        new = [0.0] * 121
        new[100] = 100.0
        diff = compute_weight_diff(old, new, hidden_size=6, num_hidden_layers=3)
        assert "hidden_1_weights" in diff
        assert "hidden_2_weights" in diff
        assert "hidden_3_weights" in diff
        assert "output_weights" in diff

    def test_large_shift_in_output_weights_counted(self):
        from ga.evolution import compute_weight_diff
        old = [0.0] * 37
        new = [0.0] * 37
        for i in range(31, 36):
            new[i] = 100.0
        diff = compute_weight_diff(old, new, hidden_size=6)
        assert diff["output_weights"]["count"] >= 4

    def test_diff_with_variation_threshold_excludes_small_shifts(self):
        from ga.evolution import compute_weight_diff
        np.random.seed(0)
        old = np.zeros(37)
        new = np.zeros(37)
        new[:3] = [5.0, 5.0, 5.0]
        new[3:37] = [0.05] * 34
        diff = compute_weight_diff(old, new, hidden_size=6)
        total_count = sum(info["count"] for info in diff.values())
        assert total_count < 37

    def test_returns_dict_with_count_and_total(self):
        from ga.evolution import compute_weight_diff
        diff = compute_weight_diff([0.0] * 37, [0.0] * 37, hidden_size=6)
        assert set(diff.keys()) == {
            "hidden_1_weights", "hidden_1_bias", "output_weights"
        }
        for info in diff.values():
            assert "count" in info
            assert "total" in info

    def test_two_layer_returns_dict_with_all_groups(self):
        from ga.evolution import compute_weight_diff
        diff = compute_weight_diff([0.0] * 79, [0.0] * 79, hidden_size=6, num_hidden_layers=2)
        assert set(diff.keys()) == {
            "hidden_1_weights", "hidden_1_bias",
            "hidden_2_weights", "hidden_2_bias",
            "output_weights"
        }


class TestWeightDiffIntegration:
    def test_silent_when_best_fitness_does_not_improve(self, capsys):
        from ga.evolution import Evolution
        config = _make_config()
        config.population_size = 5
        config.max_generations = 3
        np.random.seed(42)

        def mock_evaluator(cfg, pop, seed, hidden_size):
            return [1.0] * len(pop), []

        evolution = Evolution(config, evaluator=mock_evaluator)
        evolution.step()
        captured = capsys.readouterr()
        assert "best fitness" not in captured.out.lower()

    def test_prints_when_best_fitness_improves(self, capsys):
        from ga.evolution import Evolution
        config = _make_config()
        config.population_size = 5
        config.max_generations = 3
        np.random.seed(42)

        call_count = [0]
        def mock_evaluator(cfg, pop, seed, hidden_size):
            call_count[0] += 1
            return [float(call_count[0])] * len(pop), []

        evolution = Evolution(config, evaluator=mock_evaluator)
        evolution.step()
        captured = capsys.readouterr()
        assert "best fitness" in captured.out.lower() or "weight" in captured.out.lower()
