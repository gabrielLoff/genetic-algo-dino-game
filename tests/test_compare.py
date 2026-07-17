import matplotlib
matplotlib.use('Agg')

import pygame
from game.config import Config
from game.config_screen import ConfigScreen
from game.presets import load_presets
from main import _compare_evolutions
from replay.logger import LogStore


def test_comparison_presets_starts_none():
    pygame.init()
    screen = pygame.display.set_mode((1, 1))
    config = Config()
    cs = ConfigScreen(config, screen)
    assert cs.comparison_presets is None
    pygame.quit()


def test_compare_mode_starts_off():
    pygame.init()
    screen = pygame.display.set_mode((1, 1))
    config = Config()
    cs = ConfigScreen(config, screen)
    assert cs._compare_mode is False
    pygame.quit()


def test_compare_evolutions_runs_both_presets():
    presets = load_presets("presets.json")
    assert len(presets) >= 2, "Need at least 2 presets for comparison test"

    evolution, result_store = _compare_evolutions(presets[0], presets[1])

    assert evolution is not None
    assert evolution.generation >= 1
    assert evolution.best_fitness >= 0
    assert isinstance(result_store, LogStore)


def test_compare_evolutions_returns_second_evolution():
    preset_a = {
        "name": "TestA",
        "description": "A test",
        "params": {
            "population_size": 10, "max_generations": 2,
            "time_cap_seconds": 0.5, "master_seed": 42,
        },
    }
    preset_b = {
        "name": "TestB",
        "description": "B test",
        "params": {
            "population_size": 10, "max_generations": 2,
            "time_cap_seconds": 0.5, "master_seed": 43,
        },
    }

    evolution, _ = _compare_evolutions(preset_a, preset_b)

    assert evolution is not None
    assert evolution.generation >= 1
    assert evolution.best_fitness >= 0


def test_compare_evolutions_with_different_fitness_functions():
    preset_a = {
        "name": "Survival",
        "description": "survival_clearance",
        "params": {
            "population_size": 10, "max_generations": 2,
            "time_cap_seconds": 0.5, "master_seed": 42,
            "fitness_function": "survival_clearance",
        },
    }
    preset_b = {
        "name": "SurvivalOnly",
        "description": "survival_only",
        "params": {
            "population_size": 10, "max_generations": 2,
            "time_cap_seconds": 0.5, "master_seed": 43,
            "fitness_function": "survival_only",
        },
    }

    evolution, _ = _compare_evolutions(preset_a, preset_b)

    assert evolution is not None
    assert evolution.generation >= 1
    assert evolution.best_fitness >= 0
