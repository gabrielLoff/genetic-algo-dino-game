import numpy as np
import pytest
from dashboard.charts import extract_fitness_history, compute_genome_stats


def test_extract_fitness_history_from_evolution_records():
    history = [
        {"generation": 0, "best_fitness": 100.0, "avg_fitness": 50.0},
        {"generation": 1, "best_fitness": 200.0, "avg_fitness": 80.0},
        {"generation": 2, "best_fitness": 250.0, "avg_fitness": 120.0},
    ]
    generations, bests, avgs = extract_fitness_history(history)
    assert generations == [0, 1, 2]
    assert bests == [100.0, 200.0, 250.0]
    assert avgs == [50.0, 80.0, 120.0]


def test_extract_fitness_history_empty_returns_empty():
    generations, bests, avgs = extract_fitness_history([])
    assert generations == []
    assert bests == []
    assert avgs == []


def test_compute_genome_stats():
    genome = np.array([0.5, -0.3, 1.2, 0.1, -0.9, 0.7])
    stats = compute_genome_stats(genome)
    assert "min" in stats
    assert "max" in stats
    assert "mean" in stats
    assert "std" in stats
    assert stats["min"] == -0.9
    assert stats["max"] == 1.2
    assert pytest.approx(stats["mean"], abs=0.01) == pytest.approx(0.216, abs=0.1)


def test_compute_genome_stats_single_value():
    genome = np.array([0.5])
    stats = compute_genome_stats(genome)
    assert stats["min"] == 0.5
    assert stats["max"] == 0.5
    assert stats["std"] == 0.0
