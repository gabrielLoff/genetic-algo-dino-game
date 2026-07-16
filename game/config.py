import json
import os
from dataclasses import dataclass

PARAM_SPECS = [
    ("population_size", 100, 10, 1000, "Genetic Algorithm", "Population Size", int,
     "Number of brains competing each generation"),
    ("mutation_rate", 0.1, 0.0, 1.0, "Genetic Algorithm", "Mutation Rate", float,
     "Probability each gene is randomly altered"),
    ("mutation_strength", 0.2, 0.01, 2.0, "Genetic Algorithm", "Mutation Strength", float,
     "Magnitude of random changes to genes"),
    ("tournament_size_percent", 0.1, 0.01, 1.0, "Genetic Algorithm", "Tournament Size %", float,
     "Fraction of population competing to be a parent"),
    ("elitism_rate", 0.05, 0.0, 0.5, "Genetic Algorithm", "Elitism Rate", float,
     "Fraction of top brains kept unchanged each generation"),
    ("fitness_function", "survival_clearance", None, None, "Genetic Algorithm", "Fitness Function", str,
     "Strategy for scoring brains: survival, clearance, near-miss, efficiency"),
    ("max_generations", 50, 1, 500, "Genetic Algorithm", "Max Generations", int,
     "Stop evolution after this many generations"),
    ("plateau_generations", 10, 1, 100, "Genetic Algorithm", "Plateau Gens", int,
     "Stop if best fitness doesn't improve for this many gens"),
    ("master_seed", None, None, None, "Genetic Algorithm", "Master Seed", None,
     "Fixed seed for reproducible evolution; Random if None"),
    ("hidden_layer_size", 6, 1, 100, "Neural Network", "Hidden Layer Size", int,
     "Number of neurons in the hidden layer of the brain"),
    ("game_speed_initial", 400, 50, 2000, "Game", "Initial Speed", float,
     "Starting scroll speed (pixels/sec)"),
    ("game_speed_max", 1000, 100, 5000, "Game", "Max Speed", float,
     "Maximum scroll speed the game reaches"),
    ("game_speed_increment", 2, 0.1, 50, "Game", "Speed Increment", float,
     "How much speed increases per second"),
    ("obstacle_min_gap", 200, 50, 1000, "Game", "Min Obstacle Gap", float,
     "Minimum distance between consecutive obstacles"),
    ("obstacle_gap_mean", 500, 100, 2000, "Game", "Obstacle Gap Mean", float,
     "Average distance between obstacles (exponential distribution)"),
    ("obstacle_gap_decay", 0.001, 0.0, 0.1, "Game", "Gap Decay", float,
     "How fast the average gap shrinks over time"),
    ("time_cap_seconds", 30, 1, 300, "Game", "Time Cap (s)", float,
     "Maximum seconds a brain can survive in a single run"),
    ("jump_cooldown_frames", 5, 1, 30, "Game", "Jump Cooldown", int,
     "Frames a brain must wait between consecutive jumps"),
    ("collision_inset", 0.15, 0.0, 0.5, "Game", "Collision Inset", float,
     "How much smaller the collision box is than the sprite"),
    ("dino_gravity", 2000, 100, 5000, "Game", "Gravity", float,
     "Downward acceleration of the dino (pixels/sec^2)"),
    ("dino_max_jump_velocity", -600, -2000, -10, "Game", "Max Jump Velocity", float,
     "Upward velocity at full jump (negative = upward)"),
    ("ground_height", 80, 40, 200, "Game", "Ground Height", int,
     "Height of the ground area at the bottom of the screen"),
    ("window_width", 800, 400, 2560, "Game", "Window Width", int,
     "Game window width in pixels"),
    ("window_height", 400, 200, 1440, "Game", "Window Height", int,
     "Game window height in pixels"),
    ("obstacle_seed", None, None, None, "Game", "Obstacle Seed", None,
     "Fixed seed for obstacle layout; Random if None"),
    ("ghost_mode", "off", None, None, "Game", "Ghost Mode", str,
     "Show ghost brains in replay: off, worst, random, top"),
    ("ghost_count", 3, 1, 10, "Game", "Ghost Count", int,
     "Number of ghost brains when mode is top"),
    ("fullscreen", False, None, None, "Game", "Fullscreen", None,
     "Run in borderless fullscreen for presentations"),
]

DEFAULT_CONFIG = {
    name: default for name, default, _min, _max, _group, _label, _type, _desc in PARAM_SPECS
}


@dataclass
class Config:
    population_size: int = 100
    hidden_layer_size: int = 6
    mutation_rate: float = 0.1
    mutation_strength: float = 0.2
    tournament_size_percent: float = 0.1
    elitism_rate: float = 0.05
    fitness_function: str = "survival_clearance"
    game_speed_initial: float = 400
    game_speed_max: float = 1000
    game_speed_increment: float = 2
    obstacle_min_gap: float = 200
    obstacle_gap_mean: float = 500
    obstacle_gap_decay: float = 0.001
    time_cap_seconds: float = 30
    jump_cooldown_frames: int = 5
    collision_inset: float = 0.15
    dino_gravity: float = 2000
    dino_max_jump_velocity: float = -600
    ground_height: int = 80
    window_width: int = 800
    window_height: int = 400
    max_generations: int = 50
    plateau_generations: int = 10
    master_seed: int | None = None
    obstacle_seed: int | None = None
    ghost_mode: str = "off"
    ghost_count: int = 3
    fullscreen: bool = False

    @property
    def ground_y(self):
        return self.window_height - self.ground_height


def load_config(path):
    overrides = {}
    if os.path.exists(path):
        with open(path) as f:
            overrides = json.load(f)
    return Config(**overrides)
