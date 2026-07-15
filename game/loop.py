import pygame


class GameLoop:
    def __init__(self, config, on_update=None, dt=1/60):
        self._config = config
        self._on_update = on_update
        self._dt = dt
        self._running = False

    def run(self):
        pygame.init()
        pygame.display.set_caption("Genetic Algorithm Dino Game")
        self._screen = pygame.display.set_mode(
            (self._config.window_width, self._config.window_height)
        )

        clock = pygame.time.Clock()
        self._running = True
        accumulator = 0.0

        while self._running:
            dt_ms = clock.tick(60)
            dt_seconds = dt_ms / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    break

            if not self._running:
                break

            accumulator += dt_seconds
            while accumulator >= self._dt:
                if self._on_update:
                    self._on_update(self._dt)
                accumulator -= self._dt

            self._screen.fill((255, 255, 255))
            pygame.display.flip()

        pygame.quit()
