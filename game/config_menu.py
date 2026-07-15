from game.config import Config


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
        return [
            ParamGroup("Genetic Algorithm", {
                "population_size": (100, 10, 1000, "Population Size"),
                "mutation_rate": (0.1, 0.0, 1.0, "Mutation Rate"),
                "mutation_strength": (0.2, 0.01, 2.0, "Mutation Strength"),
                "tournament_size_percent": (0.1, 0.01, 1.0, "Tournament Size %"),
                "elitism_rate": (0.05, 0.0, 0.5, "Elitism Rate"),
                "fitness_function": ("survival_clearance", None, None, "Fitness Function"),
                "max_generations": (50, 1, 500, "Max Generations"),
                "plateau_generations": (10, 1, 100, "Plateau Gens"),
                "master_seed": (None, None, None, "Master Seed"),
            }),
            ParamGroup("Neural Network", {
                "hidden_layer_size": (6, 1, 100, "Hidden Layer Size"),
            }),
            ParamGroup("Game", {
                "game_speed_initial": (400, 50, 2000, "Initial Speed"),
                "game_speed_max": (1000, 100, 5000, "Max Speed"),
                "game_speed_increment": (2, 0.1, 50, "Speed Increment"),
                "obstacle_min_gap": (200, 50, 1000, "Min Obstacle Gap"),
                "obstacle_gap_mean": (500, 100, 2000, "Obstacle Gap Mean"),
                "obstacle_gap_decay": (0.001, 0.0, 0.1, "Gap Decay"),
                "time_cap_seconds": (30, 1, 300, "Time Cap (s)"),
                "jump_cooldown_frames": (5, 1, 30, "Jump Cooldown"),
                "collision_inset": (0.15, 0.0, 0.5, "Collision Inset"),
                "dino_gravity": (2000, 100, 5000, "Gravity"),
                "dino_max_jump_velocity": (-600, -2000, -10, "Max Jump Velocity"),
            }),
        ]

    def adjust_param(self, multiplier):
        if not self._groups:
            return
        group = self._groups[self._selected_group]
        key = self._param_keys[self._selected_param]
        param_info = group.params[key]
        default, min_val, max_val, _label = param_info

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
