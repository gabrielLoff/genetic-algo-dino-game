import numpy as np
from ga.engine import (
    create_population,
    tournament_select,
    uniform_crossover,
    gaussian_mutation,
    elitism_survivors,
)
from game.runner import RunResult


def test_create_population_generates_correct_number():
    pop = create_population(size=10, hidden_size=6)
    assert len(pop) == 10
    genome_len = (6 * 4) + 6 + 6 + 1
    assert all(len(g) == genome_len for g in pop)


def test_create_population_uses_he_initialization():
    np.random.seed(42)
    pop = create_population(size=5, hidden_size=6)
    assert len(np.unique(np.concatenate(pop))) > 1


def test_tournament_select_returns_index_in_range():
    fitnesses = [1.0, 2.0, 3.0, 4.0, 5.0]
    np.random.seed(0)
    winner = tournament_select(fitnesses, k=3)
    assert 0 <= winner < 5


def test_tournament_select_favors_higher_fitness():
    np.random.seed(42)
    fitnesses = [0.1, 0.2, 100.0, 0.3, 0.4]
    winners = [tournament_select(fitnesses, k=3) for _ in range(100)]
    assert winners.count(2) > 50


def test_uniform_crossover_produces_child_length_match():
    parent_a = np.array([1.0] * 37)
    parent_b = np.array([2.0] * 37)
    np.random.seed(0)
    child = uniform_crossover(parent_a, parent_b)
    assert len(child) == 37
    assert all(v in (1.0, 2.0) for v in child)


def test_uniform_crossover_mixes_parents():
    np.random.seed(0)
    parent_a = np.ones(100)
    parent_b = np.zeros(100)
    child = uniform_crossover(parent_a, parent_b)
    assert 0 < np.sum(child) < 100


def test_gaussian_mutation_perturbs_genome():
    np.random.seed(42)
    original = np.array([1.0] * 37)
    mutated = gaussian_mutation(original, mutation_rate=1.0, mutation_strength=0.5)
    assert not np.array_equal(original, mutated)


def test_gaussian_mutation_respects_rate():
    np.random.seed(7)
    original = np.array([1.0] * 1000)
    mutated = gaussian_mutation(original, mutation_rate=0.2, mutation_strength=1.0)
    changed = np.sum(original != mutated)
    assert 150 <= changed <= 300


def test_elitism_survivors_returns_top_indices():
    fitnesses = [1.0, 5.0, 3.0, 10.0, 2.0]
    survivors = elitism_survivors(fitnesses, elitism_rate=0.4)
    assert len(survivors) == 2
    assert 3 in survivors
    assert 1 in survivors


def test_fitness_survival_clearance():
    result = RunResult(
        brain_index=0, distance=500, obstacles_cleared=3,
        jumps_count=0, near_misses=0, time_alive=10.0,
        died_by_collision=True, died_by_time_cap=False,
    )
    expected = 500 + 3 * 100
    assert result.fitness("survival_clearance") == expected


def test_fitness_survival_only():
    result = RunResult(
        brain_index=0, distance=400, obstacles_cleared=5,
        jumps_count=0, near_misses=0, time_alive=10.0,
        died_by_collision=True, died_by_time_cap=False,
    )
    assert result.fitness("survival_only") == 400


def test_fitness_near_miss():
    result = RunResult(
        brain_index=0, distance=300, obstacles_cleared=2,
        jumps_count=0, near_misses=4, time_alive=10.0,
        died_by_collision=True, died_by_time_cap=False,
    )
    expected = 300 + 4 * 50
    assert result.fitness("near_miss") == expected


def test_fitness_efficiency():
    result = RunResult(
        brain_index=0, distance=600, obstacles_cleared=4,
        jumps_count=10, near_misses=0, time_alive=10.0,
        died_by_collision=True, died_by_time_cap=False,
    )
    expected = 600 - max(0, 10 - 4 * 2) * 10
    assert result.fitness("efficiency") == expected
