import numpy as np
from game.geometry import inset_hitbox, aabb_collides

CACTUS_SIZE_SMALL = "small"
CACTUS_SIZE_TALL = "tall"

_CACTUS_DIMS = {
    CACTUS_SIZE_SMALL: (20, 40),
    CACTUS_SIZE_TALL: (25, 55),
}


class Cactus:
    def __init__(self, x, size=CACTUS_SIZE_SMALL):
        self.x = float(x)
        self.size = size
        self.width, self.height = _CACTUS_DIMS[size]
        self.cleared = False

    def update(self, speed, dt):
        self.x -= speed * dt

    def is_off_screen(self):
        return self.x + self.width < 0

    def hitbox(self):
        return inset_hitbox(self.x, 0, self.width, self.height, 0.15)


class GameSpeed:
    def __init__(self, initial=400, max_speed=1000, increment=2):
        self.initial = initial
        self.max_speed = max_speed
        self.increment = increment
        self.current = float(initial)

    def update(self, dt):
        self.current = min(self.max_speed, self.current + self.increment * dt)

    def reset(self):
        self.current = float(self.initial)


class ObstacleManager:
    def __init__(self, screen_width=800, ground_y=320, gap_mean=500, min_gap=200, gap_decay=0.001):
        self._screen_width = screen_width
        self._ground_y = ground_y
        self._gap_mean = float(gap_mean)
        self._initial_gap_mean = float(gap_mean)
        self._min_gap = min_gap
        self._gap_decay = gap_decay
        self._next_spawn = 20.0
        self._time = 0.0
        self.obstacles = []

    def update(self, speed, dt):
        self._time += dt
        self._gap_mean = max(
            self._min_gap,
            self._initial_gap_mean * np.exp(-self._gap_decay * self._time),
        )

        self._next_spawn -= speed * dt
        if self._next_spawn <= 0 and speed > 0:
            self._spawn()
            gap = np.random.exponential(self._gap_mean)
            self._next_spawn = max(self._min_gap, gap)

        for cactus in self.obstacles:
            cactus.update(speed, dt)

        self.obstacles = [c for c in self.obstacles if not c.is_off_screen()]

    def _spawn(self):
        size = CACTUS_SIZE_TALL if np.random.random() < 0.5 else CACTUS_SIZE_SMALL
        cactus = Cactus(x=self._screen_width, size=size)
        self.obstacles.append(cactus)

    def distance_to_next(self, dino_x, screen_width):
        ahead = [c for c in self.obstacles if c.x > dino_x]
        if not ahead:
            return float(screen_width)
        return float(min(c.x for c in ahead) - dino_x)

    def obstacle_present(self, dino_x):
        return any(c.x > dino_x and c.x < dino_x + self._screen_width for c in self.obstacles)

    def collision_with(self, dino_hitbox, ground_y):
        for cactus in self.obstacles:
            cactus_hb = (
                cactus.hitbox()[0],
                ground_y - cactus.height,
                cactus.hitbox()[2],
                cactus.hitbox()[3],
            )
            if aabb_collides(dino_hitbox, cactus_hb):
                return True
        return False
