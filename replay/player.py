import json
import pygame
from replay.logger import GameplayLog, FrameRecord
from game.sprites import render_dino, render_cactus, render_ground, render_background


class ReplayPlayer:
    def __init__(self, screen, font=None):
        self._screen = screen
        self._font = font or pygame.font.SysFont("monospace", 14)
        self._speed = 1

    def play(self, log, speed=1):
        self._speed = speed
        clock = pygame.time.Clock()
        frame_idx = 0
        running = True
        frames = log.frames

        while running and frame_idx < len(frames):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_SPACE):
                        running = False
                    elif event.key == pygame.K_1:
                        self._speed = 1
                    elif event.key == pygame.K_2:
                        self._speed = 2
                    elif event.key == pygame.K_4:
                        self._speed = 4

            record = frames[frame_idx]
            self._render_frame(record, log)
            frame_idx += self._speed
            clock.tick(60)

    def _render_frame(self, record, log):
        screen_w = self._screen.get_width()
        screen_h = self._screen.get_height()
        render_background(self._screen, screen_w, screen_h)

        ground_y = 320
        ground_h = 80
        ground_offset = int(record.frame * record.game_speed / 60) % 800
        render_ground(self._screen, ground_y, ground_h, ground_offset)

        render_dino(self._screen, 80, record.dino_y)

        for obs in record.obstacles:
            render_cactus(self._screen, obs["x"], ground_y, obs.get("size", "small"))

        gauge_x = 700
        gauge_y = 20
        gauge_w = 20
        gauge_h = 100
        pygame.draw.rect(self._screen, (200, 200, 200),
                         (gauge_x, gauge_y, gauge_w, gauge_h), 1)
        fill_h = int(record.brain_output * gauge_h)
        pygame.draw.rect(self._screen, (0, 100, 200),
                         (gauge_x, gauge_y + gauge_h - fill_h, gauge_w, fill_h))

        label = self._font.render(f"Output: {record.brain_output:.2f}", True, (0, 0, 0))
        self._screen.blit(label, (gauge_x - 80, gauge_y + gauge_h + 5))

        gen_label = self._font.render(
            f"Gen {log.generation}  Brain {log.brain_index}  Frame {record.frame}  {self._speed}x",
            True, (0, 0, 0))
        self._screen.blit(gen_label, (10, 10))

        hint = self._font.render("SPACE=stop  1/2/4=speed", True, (120, 120, 120))
        self._screen.blit(hint, (10, self._screen.get_height() - 20))

        pygame.display.flip()


def record_run_to_log(genome, generation, brain_index, config, seed):
    import numpy as np
    from game.dino import Dino
    from game.obstacle import GameSpeed, ObstacleManager
    from game.brain import Brain, JumpController

    np.random.seed(seed)
    log = GameplayLog(generation=generation, brain_index=brain_index, seed=seed)

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
    )
    brain = Brain(genome, hidden_size=config.hidden_layer_size)
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
        obstacle_present = 1.0 if obs_manager.obstacle_present(dino.x) else 0.0
        normalized_distance = min(distance_to_next / config.window_width, 1.0)
        normalized_speed = speed / config.game_speed_max
        inputs = np.array([normalized_distance, obstacle_present, normalized_speed])
        brain_output = brain.evaluate(inputs)

        if jump_ctrl.should_jump(brain_output):
            dino.jump(brain_output, config.dino_max_jump_velocity)

        dino.update(dt, config.dino_gravity)
        jump_ctrl.update()

        obstacles_data = [
            {"x": c.x, "size": c.size}
            for c in obs_manager.obstacles
        ]
        log.add(FrameRecord(
            frame=frame, dino_y=dino.y, obstacles=obstacles_data,
            brain_output=brain_output, game_speed=speed,
        ))

        if obs_manager.collision_with(dino.hitbox(), config.ground_y):
            break

        time_alive += dt
        frame += 1

        if time_alive >= config.time_cap_seconds:
            break

    return log
