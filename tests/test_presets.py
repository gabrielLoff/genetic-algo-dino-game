import json
import os
import pytest
from game.config import Config, DEFAULT_CONFIG
from game.presets import load_presets, apply_preset, save_user_preset


def test_load_presets_returns_presets_from_file():
    presets = load_presets("presets.json", user_presets_path="/nonexistent")
    assert len(presets) >= 1
    assert all("name" in p and "description" in p for p in presets)


def test_tutorial_preset_has_correct_values():
    presets = load_presets("presets.json", user_presets_path="/nonexistent")
    tutorial = next((p for p in presets if p["name"] == "Tutorial"), None)
    assert tutorial is not None, "Tutorial preset not found"
    params = tutorial["params"]
    assert params["population_size"] == 20
    assert params["max_generations"] == 5
    assert params["hidden_layer_size"] == 4
    assert params["game_speed_initial"] == 600
    assert params["time_cap_seconds"] == 5
    assert params["fitness_function"] == "survival_clearance"
    assert params["master_seed"] == 42


def test_tutorial_preset_is_first():
    presets = load_presets("presets.json", user_presets_path="/nonexistent")
    assert presets[0]["name"] == "Tutorial"


def test_load_presets_returns_default_for_missing_file():
    presets = load_presets("nonexistent_presets.json", user_presets_path="/nonexistent")
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


def test_save_user_preset_writes_file(tmp_path):
    config = Config()
    config.population_size = 50
    path = str(tmp_path / "user_presets.json")
    save_user_preset("MyPreset", config, path=path)
    assert os.path.exists(path)
    with open(path) as f:
        data = json.load(f)
    assert "presets" in data
    assert any(p["name"] == "MyPreset" for p in data["presets"])


def test_save_user_preset_captures_only_non_default_params(tmp_path):
    config = Config()
    config.population_size = 50
    config.mutation_rate = 0.5
    path = str(tmp_path / "user_presets.json")
    save_user_preset("Sparse", config, path=path)
    with open(path) as f:
        data = json.load(f)
    preset = next(p for p in data["presets"] if p["name"] == "Sparse")
    assert "population_size" in preset["params"]
    assert "mutation_rate" in preset["params"]
    assert "hidden_layer_size" not in preset["params"]


def test_save_user_preset_overwrites_existing_name(tmp_path):
    config = Config()
    config.population_size = 50
    path = str(tmp_path / "user_presets.json")
    save_user_preset("MyPreset", config, path=path)

    config.population_size = 99
    save_user_preset("MyPreset", config, path=path)

    with open(path) as f:
        data = json.load(f)
    matching = [p for p in data["presets"] if p["name"] == "MyPreset"]
    assert len(matching) == 1
    assert matching[0]["params"]["population_size"] == 99


def test_save_user_preset_rejects_default_name(tmp_path):
    config = Config()
    path = str(tmp_path / "user_presets.json")
    with pytest.raises(ValueError):
        save_user_preset("Default", config, path=path)
    assert not os.path.exists(path)


def test_save_user_preset_rejects_default_name_case_insensitive(tmp_path):
    config = Config()
    path = str(tmp_path / "user_presets.json")
    for variant in ("default", "DEFAULT", "DeFaUlT"):
        with pytest.raises(ValueError):
            save_user_preset(variant, config, path=path)
    assert not os.path.exists(path)


def test_save_user_preset_creates_file_if_missing(tmp_path):
    config = Config()
    config.population_size = 50
    path = str(tmp_path / "user_presets.json")
    assert not os.path.exists(path)
    save_user_preset("First", config, path=path)
    assert os.path.exists(path)


def test_save_user_preset_appends_to_existing(tmp_path):
    config = Config()
    path = str(tmp_path / "user_presets.json")
    save_user_preset("A", config, path=path)
    save_user_preset("B", config, path=path)
    with open(path) as f:
        data = json.load(f)
    names = [p["name"] for p in data["presets"]]
    assert names == ["A", "B"]


def test_save_user_preset_atomic_write(tmp_path):
    config = Config()
    config.population_size = 50
    path = str(tmp_path / "user_presets.json")
    save_user_preset("Atomic", config, path=path)
    with open(path) as f:
        data = json.load(f)
    assert data["presets"][0]["name"] == "Atomic"


def test_load_presets_merges_user_presets(tmp_path):
    config = Config()
    config.population_size = 50
    user_path = str(tmp_path / "user_presets.json")
    save_user_preset("UserA", config, path=user_path)
    save_user_preset("UserB", config, path=user_path)

    builtins = load_presets("presets.json", user_presets_path=user_path)
    names = [p["name"] for p in builtins]
    assert "UserA" in names
    assert "UserB" in names

    builtin_count = len(load_presets("presets.json", user_presets_path="/nonexistent"))
    user_names = names[builtin_count:]
    assert user_names == ["UserA", "UserB"]


def test_load_presets_no_user_file_returns_builtins_only(tmp_path):
    user_path = str(tmp_path / "nonexistent_user_presets.json")
    presets = load_presets("presets.json", user_presets_path=user_path)
    assert presets == load_presets("presets.json", user_presets_path="/nonexistent")


def test_user_preset_overrides_builtin_with_same_name(tmp_path):
    config = Config()
    config.population_size = 999
    user_path = str(tmp_path / "user_presets.json")
    save_user_preset("Tutorial", config, path=user_path)

    presets = load_presets("presets.json", user_presets_path=user_path)
    tutorial_presets = [p for p in presets if p["name"] == "Tutorial"]
    assert len(tutorial_presets) == 1
    assert tutorial_presets[0]["params"]["population_size"] == 999
