import json
import os


def load_presets(path="presets.json"):
    if not os.path.exists(path):
        return [{"name": "Default", "description": "Baseline configuration", "params": {}}]
    with open(path) as f:
        data = json.load(f)
    return data.get("presets", [])


def apply_preset(config, preset, config_path="config.json"):
    if preset["name"] == "Default":
        if os.path.exists(config_path):
            with open(config_path) as f:
                overrides = json.load(f)
        else:
            from game.config import DEFAULT_CONFIG
            overrides = dict(DEFAULT_CONFIG)
    else:
        overrides = preset.get("params", {})

    for key, value in overrides.items():
        setattr(config, key, value)
