import json
import os

PARAM_SPECS = [
    ("population_size", 100, 10, 1000, "Genetic Algorithm", "Population Size", int),
    ("mutation_rate", 0.1, 0.0, 1.0, "Genetic Algorithm", "Mutation Rate", float),
    ("mutation_strength", 0.2, 0.01, 2.0, "Genetic Algorithm", "Mutation Strength", float),
    ("tournament_size_percent", 0.1, 0.01, 1.0, "Genetic Algorithm", "Tournament Size %", float),
    ("elitism_rate", 0.05, 0.0, 0.5, "Genetic Algorithm", "Elitism Rate", float),
    ("fitness_function", "survival_clearance", None, None, "Genetic Algorithm", "Fitness Function", str),
    ("max_generations", 50, 1, 500, "Genetic Algorithm", "Max Generations", int),
    ("plateau_generations", 10, 1, 100, "Genetic Algorithm", "Plateau Gens", int),
    ("master_seed", None, None, None, "Genetic Algorithm", "Master Seed", None),
    ("hidden_layer_size", 6, 1, 100, "Neural Network", "Hidden Layer Size", int),
    ("game_speed_initial", 400, 50, 2000, "Game", "Initial Speed", float),
    ("game_speed_max", 1000, 100, 5000, "Game", "Max Speed", float),
    ("game_speed_increment", 2, 0.1, 50, "Game", "Speed Increment", float),
    ("obstacle_min_gap", 200, 50, 1000, "Game", "Min Obstacle Gap", float),
    ("obstacle_gap_mean", 500, 100, 2000, "Game", "Obstacle Gap Mean", float),
    ("obstacle_gap_decay", 0.001, 0.0, 0.1, "Game", "Gap Decay", float),
    ("time_cap_seconds", 30, 1, 300, "Game", "Time Cap (s)", float),
    ("jump_cooldown_frames", 5, 1, 30, "Game", "Jump Cooldown", int),
    ("collision_inset", 0.15, 0.0, 0.5, "Game", "Collision Inset", float),
    ("dino_gravity", 2000, 100, 5000, "Game", "Gravity", float),
    ("dino_max_jump_velocity", -600, -2000, -10, "Game", "Max Jump Velocity", float),
    ("ground_height", 80, 40, 200, "Game", "Ground Height", int),
    ("window_width", 800, 400, 2560, "Game", "Window Width", int),
    ("window_height", 400, 200, 1440, "Game", "Window Height", int),
]

DEFAULT_CONFIG = {
    name: default for name, default, _min, _max, _group, _label, _type in PARAM_SPECS
}


class Config:
    def __init__(self, **kwargs):
        for key, default in DEFAULT_CONFIG.items():
            setattr(self, key, kwargs.get(key, default))

    @property
    def ground_y(self):
        return self.window_height - self.ground_height


def load_config(path):
    overrides = {}
    if os.path.exists(path):
        with open(path) as f:
            overrides = json.load(f)
    return Config(**overrides)
