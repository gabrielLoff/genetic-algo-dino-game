from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import matplotlib
from dashboard.window import DashboardWindow, Evolution, compute_genome_stats


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


def test_dashboard_update_does_not_pause_event_loop():
    dashboard = DashboardWindow.__new__(DashboardWindow)
    dashboard._fig = MagicMock()
    dashboard._ax_fitness = MagicMock()
    dashboard._ax_cleared = MagicMock()
    dashboard._ax_text = MagicMock()
    evolution = SimpleNamespace(
        history=[{"generation": 0, "best_fitness": 1.0, "avg_fitness": 0.5}],
        generation=0,
        best_fitness=1.0,
        best_genome=None,
        end_condition=Evolution.END_RUNNING,
        _config=SimpleNamespace(diversity_warning_threshold=0.1, population_size=10, mutation_adaptation="none"),
    )

    with patch("dashboard.window.plt.pause") as pause:
        dashboard.update(evolution)

    dashboard._fig.canvas.draw.assert_called_once_with()
    dashboard._fig.canvas.flush_events.assert_called_once_with()
    pause.assert_not_called()


def test_backend_is_agg():
    assert matplotlib.get_backend().lower() == "agg"
