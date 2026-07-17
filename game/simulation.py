import numpy as np
from game.dino import Dino
from game.obstacle import GameSpeed, ObstacleManager
from game.brain import Brain, JumpController


class FrameState:
    def __init__(self, dino, game_speed, obs_manager, brain_output, dt, jumped):
        self.dino_y = dino.y
        self.dino_hitbox = dino.hitbox()
        self.speed = game_speed.current
        self.obstacles = obs_manager.obstacles
        self.brain_output = brain_output
        self.jumped = jumped
        self.dino = dino
        self.obs_manager = obs_manager


class GameSimulation:
    def __init__(self, config, genome, seed):
        self._config = config
        self._genome = genome
        self._seed = seed

    def run(self, per_frame_callback):
        seed = self._config.obstacle_seed if self._config.obstacle_seed is not None else self._seed
        np.random.seed(seed)
        config = self._config

        dino = Dino(ground_y=config.ground_y, collision_inset=config.collision_inset)
        game_speed = GameSpeed(
            initial=config.game_speed_initial,
            max_speed=config.game_speed_max,
            increment=config.game_speed_increment,
        )
        obs_manager = ObstacleManager(
            screen_width=config.window_width,
            ground_y=config.ground_y,
            gap_mean=config.obstacle_gap_mean,
            min_gap=config.obstacle_min_gap,
            gap_decay=config.obstacle_gap_decay,
            pterodactyl_probability=config.pterodactyl_probability,
        )
        brain = Brain(self._genome, hidden_size=config.hidden_layer_size, input_size=4, num_hidden_layers=config.num_hidden_layers)
        jump_ctrl = JumpController(
            threshold=0.5,
            cooldown_frames=config.jump_cooldown_frames,
        )

        dt = 1.0 / 60.0
        time_alive = 0.0
        frame = 0

        while True:
            game_speed.update(dt)
            speed = game_speed.current
            obs_manager.update(speed, dt)

            distance_to_next = obs_manager.distance_to_next(dino.x, config.window_width)
            obstacle_present_flag = 1.0 if obs_manager.obstacle_present(dino.x) else 0.0
            normalized_distance = min(distance_to_next / config.window_width, 1.0)
            normalized_speed = speed / config.game_speed_max
            normalized_height = obs_manager.nearest_obstacle_height(dino.x, config.ground_y)
            inputs = np.array([normalized_distance, obstacle_present_flag, normalized_speed, normalized_height])
            brain_output = brain.evaluate(inputs)

            jumped = jump_ctrl.should_jump(brain_output)
            if jumped:
                dino.jump(brain_output, config.dino_max_jump_velocity)

            dino.update(dt, config.dino_gravity)
            jump_ctrl.update()

            state = FrameState(dino, game_speed, obs_manager, brain_output, dt, jumped)
            should_continue = per_frame_callback(state, frame, time_alive)

            if not should_continue:
                break

            time_alive += dt
            frame += 1

            if time_alive >= config.time_cap_seconds:
                break

        return frame, time_alive
