from game.geometry import inset_hitbox, aabb_collides


def test_inset_hitbox_shrinks_all_four_edges():
    result = inset_hitbox(100, 200, 40, 50, 0.1)
    x, y, w, h = result
    assert x > 100
    assert y > 200
    assert w < 40
    assert h < 50


def test_aabb_collides_no_overlap():
    assert not aabb_collides((0, 0, 10, 10), (20, 20, 10, 10))


def test_aabb_collides_overlap():
    assert aabb_collides((0, 0, 10, 10), (5, 5, 10, 10))
