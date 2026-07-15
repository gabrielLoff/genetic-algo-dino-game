import numpy as np
from ga.engine import (
    create_population,
    tournament_select,
    uniform_crossover,
    gaussian_mutation,
    elitism_survivors,
    compute_fitness,
)


def test_create_population_generates_correct_number():
    pop = create_population(size=10, genome_length=31)
    assert len(pop) == 10
    assert all(len(g) == 31 for g in pop)


def test_create_population_uses_he_initialization():
    np.random.seed(42)
    pop = create_population(size=5, genome_length=31)
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
    parent_a = np.array([1.0] * 31)
    parent_b = np.array([2.0] * 31)
    np.random.seed(0)
    child = uniform_crossover(parent_a, parent_b)
    assert len(child) == 31
    assert all(v in (1.0, 2.0) for v in child)


def test_uniform_crossover_mixes_parents():
    np.random.seed(0)
    parent_a = np.ones(100)
    parent_b = np.zeros(100)
    child = uniform_crossover(parent_a, parent_b)
    assert 0 < np.sum(child) < 100


def test_gaussian_mutation_perturbs_genome():
    np.random.seed(42)
    original = np.array([1.0] * 31)
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


def test_compute_fitness_survival_clearance():
    fitness = compute_fitness(
        distance=500,
        obstacles_cleared=3,
        strategy="survival_clearance",
    )
    expected = 500 + 3 * 100
    assert fitness == expected


def test_compute_fitness_survival_only():
    fitness = compute_fitness(
        distance=400,
        obstacles_cleared=5,
        strategy="survival_only",
    )
    assert fitness == 400


def test_compute_fitness_near_miss():
    fitness = compute_fitness(
        distance=300,
        obstacles_cleared=2,
        near_misses=4,
        strategy="near_miss",
    )
    expected = 300 + 4 * 50
    assert fitness == expected


def test_compute_fitness_efficiency():
    fitness = compute_fitness(
        distance=600,
        obstacles_cleared=4,
        jumps_count=10,
        strategy="efficiency",
    )
    expected = 600 - max(0, 10 - 4 * 2) * 10
    assert fitness == expected
