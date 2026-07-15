from game.config import Config, PARAM_SPECS


class ParamGroup:
    def __init__(self, name, params):
        self.name = name
        self.params = params


class ConfigMenu:
    def __init__(self, config):
        self._config = config
        self._groups = self._build_groups()
        self._selected_group = 0
        self._selected_param = 0
        self._param_keys = list(self._groups[0].params.keys())

    def _build_groups(self):
        groups = {}
        for name, default, min_val, max_val, group, label, _type, desc in PARAM_SPECS:
            if group not in groups:
                groups[group] = {}
            groups[group][name] = (default, min_val, max_val, label, desc)
        return [ParamGroup(name, params) for name, params in groups.items()]

    def adjust_param(self, multiplier):
        if not self._groups:
            return
        group = self._groups[self._selected_group]
        key = self._param_keys[self._selected_param]
        param_info = group.params[key]
        default, min_val, max_val, _label, _desc = param_info

        if isinstance(default, str) or default is None:
            return

        new_val = getattr(self._config, key) * multiplier
        if min_val is not None:
            new_val = max(min_val, new_val)
        if max_val is not None:
            new_val = min(max_val, new_val)
        if isinstance(default, int):
            new_val = int(new_val)
        setattr(self._config, key, new_val)
