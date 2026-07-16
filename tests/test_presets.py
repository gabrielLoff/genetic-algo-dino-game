import json
import os
import pytest
from game.config import Config, DEFAULT_CONFIG
from game.presets import load_presets, apply_preset


def test_load_presets_returns_presets_from_file():
    presets = load_presets("presets.json")
    assert len(presets) >= 1
    assert all("name" in p and "description" in p for p in presets)


def test_load_presets_returns_default_for_missing_file():
    presets = load_presets("nonexistent_presets.json")
    assert len(presets) == 1
    assert presets[0]["name"] == "Default"


def test_apply_preset_updates_config_values():
    config = Config()
    preset = {
        "name": "Test",
        "description": "Test preset",
        "params": {"population_size": 50, "mutation_rate": 0.99}
    }
    apply_preset(config, preset)
    assert config.population_size == 50
    assert config.mutation_rate == 0.99
    assert config.hidden_layer_size == DEFAULT_CONFIG["hidden_layer_size"]


def test_apply_default_preset_reloads_from_config_json(tmp_path):
    config = Config()
    config.population_size = 999
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"population_size": 42}))

    preset = {"name": "Default", "description": "", "params": {}}
    apply_preset(config, preset, config_path=str(config_path))
    assert config.population_size == 42


def test_apply_default_preset_falls_back_to_defaults(tmp_path):
    config = Config()
    config.population_size = 999
    nonexistent = str(tmp_path / "nonexistent.json")

    preset = {"name": "Default", "description": "", "params": {}}
    apply_preset(config, preset, config_path=nonexistent)
    assert config.population_size == DEFAULT_CONFIG["population_size"]


def test_apply_preset_only_overrides_specified_params():
    config = Config()
    original_hidden = config.hidden_layer_size
    preset = {
        "name": "Partial",
        "description": "Only overrides one param",
        "params": {"population_size": 25}
    }
    apply_preset(config, preset)
    assert config.population_size == 25
    assert config.hidden_layer_size == original_hidden
