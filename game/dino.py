from game.geometry import inset_hitbox

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
        top = self.y - 50
        return inset_hitbox(self.x, top, 40, 50, self._collision_inset)
