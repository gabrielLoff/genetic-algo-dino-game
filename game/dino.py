DINO_STATE_GROUNDED = "grounded"
DINO_STATE_JUMPING = "jumping"
DINO_STATE_FALLING = "falling"


class Dino:
    def __init__(self, ground_y=320, collision_inset=0.15):
        self.x = 80
        self.y = float(ground_y)
        self.velocity_y = 0.0
        self.state = DINO_STATE_GROUNDED
        self._ground_y = ground_y
        self._collision_inset = collision_inset

    def update(self, dt, gravity):
        if self.state != DINO_STATE_GROUNDED:
            self.velocity_y += gravity * dt
            self.y += self.velocity_y * dt

        if self.y >= self._ground_y:
            self.y = float(self._ground_y)
            self.velocity_y = 0.0
            self.state = DINO_STATE_GROUNDED
        elif self.velocity_y > 0:
            self.state = DINO_STATE_FALLING

    def jump(self, intensity, max_jump_velocity):
        if self.state == DINO_STATE_GROUNDED:
            self.velocity_y = intensity * max_jump_velocity
            self.state = DINO_STATE_JUMPING

    def hitbox(self):
        inset_x = 0
        inset_y = 0
        return (
            self.x + inset_x,
            self.y + inset_y,
            40 * (1 - self._collision_inset),
            50 * (1 - self._collision_inset),
        )
