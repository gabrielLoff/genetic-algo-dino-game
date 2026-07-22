import numpy as np
from game.dino import Dino
from game.obstacle import GameSpeed, ObstacleManager
from game.brain import Brain, ActionController


class FrameState:
    def __init__(self, dino, game_speed, obs_manager, brain_output, dt, jumped, frame, time_alive):
        self.dino_y = dino.y
        self.dino_hitbox = dino.hitbox()
        self.speed = game_speed.current
        self.obstacles = obs_manager.obstacles
        self.brain_output = brain_output
        self.jumped = jumped
        self.frame = frame
        self.time_alive = time_alive
        self.dino = dino
        self.obs_manager = obs_manager
        self.is_crouching = dino.is_crouching


class GameSimulation:
    def __init__(self, config, genome, seed):
        self._config = config
        self._genome = genome
        self._seed = seed

    def run(self, per_frame_callback=None, observers=None):
        observers = list(observers or [])
        seed = self._config.obstacle_seed if self._config.obstacle_seed is not None else self._seed
        np.random.seed(seed)
        config = self._config

        dino = Dino(ground_y=config.ground_y, collision_inset=config.collision_inset)
        speed_initial = config.game_speed_initial
        gap_mean = config.obstacle_gap_mean
        ptero_prob = config.pterodactyl_probability

        tier = getattr(config, "curriculum_tier", 0)
        if tier == 0:
            speed_initial = speed_initial * 0.5
            gap_mean = gap_mean * 1.6
            ptero_prob = 0.0
        elif tier == 2:
            ptero_prob = min(ptero_prob * 1.5, 1.0)

        game_speed = GameSpeed(
            initial=speed_initial,
            max_speed=config.game_speed_max,
            increment=config.game_speed_increment,
        )
        obs_manager = ObstacleManager(
            screen_width=config.window_width,
            ground_y=config.ground_y,
            gap_mean=gap_mean,
            min_gap=config.obstacle_min_gap,
            gap_decay=config.obstacle_gap_decay,
            pterodactyl_probability=ptero_prob,
        )
        brain = Brain(self._genome, hidden_size=config.hidden_layer_size, input_size=4, num_hidden_layers=config.num_hidden_layers, output_size=config.output_size)
        action_ctrl = ActionController(
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

            jumped = action_ctrl.should_jump(brain_output)
            if jumped:
                dino.jump(brain_output if isinstance(brain_output, float) else brain_output[0], config.dino_max_jump_velocity)

            should_crouch = action_ctrl.should_crouch(brain_output)
            dino.crouch(should_crouch)

            dino.update(dt, config.dino_gravity)
            action_ctrl.update()

            state = FrameState(dino, game_speed, obs_manager, brain_output, dt, jumped, frame, time_alive)

            for observer in observers:
                if observer(state) is False:
                    return frame, time_alive

            if per_frame_callback is not None:
                if per_frame_callback(state, frame, time_alive) is False:
                    return frame, time_alive

            time_alive += dt
            frame += 1

            if time_alive >= config.time_cap_seconds:
                break

        return frame, time_alive
