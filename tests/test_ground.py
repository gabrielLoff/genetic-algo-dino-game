from game.ground import Ground


def test_ground_initial_offset():
    ground = Ground(width=800, height=80)
    assert ground.offset == 0
    assert ground._height == 80


def test_ground_scrolls_left():
    ground = Ground(width=800, height=80)
    ground.update(speed=400, dt=1.0)
    assert ground.offset > 0
    assert ground.offset == 400.0


def test_ground_wraps_when_offset_exceeds_width():
    ground = Ground(width=800, height=80)
    ground.update(speed=800, dt=1.0)
    assert ground.offset == 0.0
