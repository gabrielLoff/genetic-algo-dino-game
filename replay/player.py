import json
import pygame
from replay.logger import GameplayLog, FrameRecord
from game.sprites import render_dino, render_cactus, render_ground, render_background


class ReplayPlayer:
    def __init__(self, screen, font=None):
        self._screen = screen
        self._font = font or pygame.font.SysFont("monospace", 14)
        self._speed = 1

    def play(self, log, speed=1, ghost_logs=None, ghost_labels=None):
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
            self._render_frame(record, log, ghost_logs, ghost_labels, frame_idx)
            frame_idx += self._speed
            clock.tick(60)

    def _render_frame(self, record, log, ghost_logs=None, ghost_labels=None, frame_idx=0):
        screen_w = self._screen.get_width()
        screen_h = self._screen.get_height()
        render_background(self._screen, screen_w, screen_h)

        ground_y = 320
        ground_h = 80
        ground_offset = int(record.frame * record.game_speed / 60) % 800
        render_ground(self._screen, ground_y, ground_h, ground_offset)

        for obs in record.obstacles:
            render_cactus(self._screen, obs["x"], ground_y, obs.get("size", "small"))

        if ghost_logs and ghost_labels:
            for gi, ghost_log in enumerate(ghost_logs):
                if frame_idx < ghost_log.frame_count:
                    ghost_frame = ghost_log.frames[frame_idx]
                    ghost_rect = pygame.Surface((40, 50), pygame.SRCALPHA)
                    ghost_rect.fill((200, 200, 200, 128))
                    self._screen.blit(ghost_rect, (80, ghost_frame.dino_y - 50))
                    label = self._font.render(ghost_labels[gi], True, (180, 180, 180))
                    self._screen.blit(label, (80, ghost_frame.dino_y - 60))

        render_dino(self._screen, 80, record.dino_y)

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
    from game.simulation import GameSimulation

    sim = GameSimulation(config, genome, seed)
    log = GameplayLog(generation=generation, brain_index=brain_index, seed=seed)
    frame_idx = 0

    def on_frame(state, frame, t):
        nonlocal frame_idx
        obstacles_data = []
        for c in state.obstacles:
            if hasattr(c, 'size'):
                obstacles_data.append({"x": c.x, "size": c.size})
            else:
                obstacles_data.append({"x": c.x, "height_level": c.height_level})
        log.add(FrameRecord(
            frame=frame_idx, dino_y=state.dino_y, obstacles=obstacles_data,
            brain_output=state.brain_output, game_speed=state.speed,
        ))
        frame_idx += 1

        if state.obs_manager.collision_with(state.dino_hitbox, config.ground_y):
            return False
        return True

    sim.run(on_frame)
    return log
