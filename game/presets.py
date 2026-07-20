import json
import os
import tempfile

from game.config import DEFAULT_CONFIG


RESERVED_PRESET_NAMES = {"default"}


def load_presets(path="presets.json", user_presets_path="user_presets.json"):
    if not os.path.exists(path):
        builtins = [{"name": "Default", "description": "Baseline configuration", "params": {}}]
    else:
        builtins = _read_presets_file(path)
    return _merge_presets(builtins, _read_presets_file(user_presets_path))


def _read_presets_file(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        data = json.load(f)
    return data.get("presets", [])


def _merge_presets(builtins, user):
    by_name = {p["name"]: p for p in builtins}
    for p in user:
        by_name[p["name"]] = p
    return list(by_name.values())


def apply_preset(config, preset, config_path="config.json"):
    if preset["name"] == "Default":
        if os.path.exists(config_path):
            with open(config_path) as f:
                overrides = json.load(f)
        else:
            overrides = dict(DEFAULT_CONFIG)
    else:
        overrides = preset.get("params", {})

    for key, value in overrides.items():
        setattr(config, key, value)


def save_user_preset(name, config, path="user_presets.json"):
    # Reserved names are a one-way check: we only block "Default" because
    # it's the magic reload-from-config.json name. User presets that share
    # a name with a built-in intentionally override the built-in via
    # _merge_presets.
    if name.lower() in RESERVED_PRESET_NAMES:
        raise ValueError(
            f"Preset name {name!r} is reserved (case-insensitive match with 'default')"
        )

    params = {
        key: getattr(config, key)
        for key in DEFAULT_CONFIG
        if getattr(config, key) != DEFAULT_CONFIG[key]
    }

    existing = _read_presets_file(path)
    filtered = [p for p in existing if p["name"] != name]
    filtered.append({"name": name, "params": params})
    _atomic_write_json(path, {"presets": filtered})


def _atomic_write_json(path, payload):
    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".user_presets_", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass
        raise
