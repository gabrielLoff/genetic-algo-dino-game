import numpy as np
from game.geometry import inset_hitbox, aabb_collides

CACTUS_SIZE_SMALL = "small"
CACTUS_SIZE_TALL = "tall"

PTERO_HEIGHT_LOW = "low"
PTERO_HEIGHT_MID = "mid"
PTERO_HEIGHT_HIGH = "high"

_CACTUS_DIMS = {
    CACTUS_SIZE_SMALL: (20, 40),
    CACTUS_SIZE_TALL: (25, 55),
}

_PTERO_HEIGHT_Y = {
    PTERO_HEIGHT_LOW: 0.08,
    PTERO_HEIGHT_MID: 0.20,
    PTERO_HEIGHT_HIGH: 0.50,
}

_PTERO_DIMS = (35, 28)


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

    def world_hitbox(self, ground_y):
        top = ground_y - self.height
        return inset_hitbox(self.x, top, self.width, self.height, 0.15)


class Pterodactyl:
    def __init__(self, x, height_level=PTERO_HEIGHT_MID):
        self.x = float(x)
        self.height_level = height_level
        self.width = _PTERO_DIMS[0]
        self.height = _PTERO_DIMS[1]
        self.cleared = False

    def update(self, speed, dt):
        self.x -= speed * dt

    def is_off_screen(self):
        return self.x + self.width < 0

    def hitbox(self):
        return inset_hitbox(self.x, 0, self.width, self.height, 0.1)

    def world_hitbox(self, ground_y):
        top = self.sprite_top(ground_y)
        return inset_hitbox(self.x, top, self.width, self.height, 0.1)

    def sprite_top(self, ground_y):
        return int(ground_y - self.height - ground_y * _PTERO_HEIGHT_Y[self.height_level])


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
    def __init__(self, screen_width=800, ground_y=320, gap_mean=500, min_gap=200,
                 gap_decay=0.001, pterodactyl_probability=0.3):
        self._screen_width = screen_width
        self._ground_y = ground_y
        self._gap_mean = float(gap_mean)
        self._initial_gap_mean = float(gap_mean)
        self._min_gap = min_gap
        self._gap_decay = gap_decay
        self._pterodactyl_probability = pterodactyl_probability
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

        for obs in self.obstacles:
            obs.update(speed, dt)

        self.obstacles = [o for o in self.obstacles if not o.is_off_screen()]

    def _spawn(self):
        if np.random.random() < self._pterodactyl_probability:
            level = np.random.choice([PTERO_HEIGHT_LOW, PTERO_HEIGHT_MID, PTERO_HEIGHT_HIGH])
            self.obstacles.append(Pterodactyl(x=self._screen_width, height_level=level))
        else:
            size = CACTUS_SIZE_TALL if np.random.random() < 0.5 else CACTUS_SIZE_SMALL
            self.obstacles.append(Cactus(x=self._screen_width, size=size))

    def distance_to_next(self, dino_x, screen_width):
        ahead = [c for c in self.obstacles if c.x > dino_x]
        if not ahead:
            return float(screen_width)
        return float(min(c.x for c in ahead) - dino_x)

    def obstacle_present(self, dino_x):
        return any(c.x > dino_x and c.x < dino_x + self._screen_width for c in self.obstacles)

    def nearest_obstacle_height(self, dino_x, ground_y):
        ahead = [c for c in self.obstacles if c.x > dino_x]
        if not ahead:
            return 0.0
        nearest = min(ahead, key=lambda c: c.x)
        if isinstance(nearest, Cactus):
            return 0.0
        return _PTERO_HEIGHT_Y.get(nearest.height_level, 0.0)

    def nearest_obstacle_is_ptero(self, dino_x):
        ahead = [c for c in self.obstacles if c.x > dino_x]
        if not ahead:
            return 0.0
        nearest = min(ahead, key=lambda c: c.x)
        return 1.0 if isinstance(nearest, Pterodactyl) else 0.0

    def collision_with(self, dino_hitbox, ground_y):
        for obs in self.obstacles:
            obs_hb = obs.world_hitbox(ground_y)
            if aabb_collides(dino_hitbox, obs_hb):
                return True
        return False
