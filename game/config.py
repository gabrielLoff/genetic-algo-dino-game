import json
import os

DEFAULT_CONFIG = {
    "population_size": 100,
    "hidden_layer_size": 6,
    "mutation_rate": 0.1,
    "mutation_strength": 0.2,
    "tournament_size_percent": 0.1,
    "elitism_rate": 0.05,
    "fitness_function": "survival_clearance",
    "game_speed_initial": 400,
    "game_speed_max": 1000,
    "game_speed_increment": 2,
    "obstacle_min_gap": 200,
    "obstacle_gap_mean": 500,
    "obstacle_gap_decay": 0.001,
    "time_cap_seconds": 30,
    "jump_cooldown_frames": 5,
    "collision_inset": 0.15,
    "dino_gravity": 2000,
    "dino_max_jump_velocity": -600,
    "window_width": 800,
    "window_height": 400,
    "max_generations": 50,
    "plateau_generations": 10,
    "master_seed": None,
}


class Config:
    def __init__(self, **kwargs):
        for key, default in DEFAULT_CONFIG.items():
            setattr(self, key, kwargs.get(key, default))


def load_config(path):
    overrides = {}
    if os.path.exists(path):
        with open(path) as f:
            overrides = json.load(f)
    return Config(**overrides)
