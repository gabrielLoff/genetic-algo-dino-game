from game.dino import Dino, DINO_STATE_GROUNDED, DINO_STATE_JUMPING, DINO_STATE_FALLING
from game.geometry import aabb_collides
from game.obstacle import Cactus, CACTUS_SIZE_SMALL


def test_dino_hitbox_collides_with_cactus():
    dino = Dino(ground_y=320, collision_inset=0.0)
    cactus = Cactus(x=80, size=CACTUS_SIZE_SMALL)
    cactus_hb = (cactus.hitbox()[0], 320 - cactus.height,
                 cactus.hitbox()[2], cactus.hitbox()[3])
    assert aabb_collides(dino.hitbox(), cactus_hb)


def test_dino_hitbox_above_ground():
    dino = Dino(ground_y=320, collision_inset=0.15)
    x, y, w, h = dino.hitbox()
    assert y < 320
    assert y + h > 270


def test_dino_initial_state():
    dino = Dino(ground_y=320, collision_inset=0.15)
    assert dino.y == 320
    assert dino.velocity_y == 0
    assert dino.state == DINO_STATE_GROUNDED
    assert dino.x == 80


def test_dino_gravity_pulls_down():
    dino = Dino(ground_y=320, collision_inset=0.15)
    dino.state = DINO_STATE_JUMPING
    dino.y = 100
    dino.velocity_y = 0
    gravity = 2000
    dt = 1 / 60
    dino.update(dt, gravity)
    assert dino.velocity_y > 0
    assert dino.y > 100


def test_dino_lands_on_ground():
    dino = Dino(ground_y=320, collision_inset=0.15)
    dino.state = DINO_STATE_FALLING
    dino.y = 340
    dino.velocity_y = 100
    dino.update(1/60, 2000)
    assert dino.y == 320
    assert dino.velocity_y == 0
    assert dino.state == DINO_STATE_GROUNDED


def test_dino_jump_applies_velocity():
    dino = Dino(ground_y=320, collision_inset=0.15)
    max_velocity = -600
    dino.jump(1.0, max_velocity)
    assert dino.velocity_y == -600
    assert dino.state == DINO_STATE_JUMPING


def test_dino_jump_scales_with_intensity():
    dino = Dino(ground_y=320, collision_inset=0.15)
    max_velocity = -600
    dino.jump(0.5, max_velocity)
    assert dino.velocity_y == -300
    assert dino.state == DINO_STATE_JUMPING


def test_dino_cannot_jump_while_airborne():
    dino = Dino(ground_y=320, collision_inset=0.15)
    dino.state = DINO_STATE_JUMPING
    dino.velocity_y = -100
    original_vy = dino.velocity_y
    dino.jump(1.0, -600)
    assert dino.velocity_y == original_vy
