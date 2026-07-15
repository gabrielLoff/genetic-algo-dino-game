import json
import pytest
from game.config import Config, DEFAULT_CONFIG, load_config


def test_default_config_has_all_required_keys():
    required = {
        "population_size", "hidden_layer_size", "mutation_rate",
        "mutation_strength", "tournament_size_percent", "elitism_rate",
        "fitness_function", "game_speed_initial", "game_speed_max",
        "game_speed_increment", "obstacle_min_gap", "obstacle_gap_mean",
        "obstacle_gap_decay", "time_cap_seconds", "jump_cooldown_frames",
        "collision_inset", "dino_gravity", "dino_max_jump_velocity",
        "window_width", "window_height", "max_generations",
        "plateau_generations", "master_seed",
    }
    missing = required - set(DEFAULT_CONFIG.keys())
    assert not missing, f"Missing defaults: {missing}"


def test_config_from_defaults():
    config = Config()
    assert config.population_size == DEFAULT_CONFIG["population_size"]
    assert config.hidden_layer_size == DEFAULT_CONFIG["hidden_layer_size"]


def test_config_overrides_supplied_values(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"population_size": 42, "hidden_layer_size": 8}))
    config = load_config(str(config_path))
    assert config.population_size == 42
    assert config.hidden_layer_size == 8
    assert config.mutation_rate == DEFAULT_CONFIG["mutation_rate"]


def test_load_config_returns_config_with_missing_file():
    config = load_config("nonexistent.json")
    assert config.population_size == DEFAULT_CONFIG["population_size"]
    assert config.mutation_rate == DEFAULT_CONFIG["mutation_rate"]


def test_load_config_with_partial_overrides(tmp_path):
    config_path = tmp_path / "partial.json"
    config_path.write_text(json.dumps({"mutation_rate": 0.05}))
    config = load_config(str(config_path))
    assert config.mutation_rate == 0.05
    assert config.population_size == DEFAULT_CONFIG["population_size"]
