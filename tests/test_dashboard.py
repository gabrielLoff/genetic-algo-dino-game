import numpy as np
import pytest
from dashboard.window import compute_genome_stats


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
