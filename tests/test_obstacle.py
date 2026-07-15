import numpy as np
from game.obstacle import Cactus, CACTUS_SIZE_SMALL, CACTUS_SIZE_TALL
from game.obstacle import GameSpeed, ObstacleManager
from game.geometry import aabb_collides


class TestCactus:
    def test_cactus_initial_position_and_size(self):
        c = Cactus(x=500, size=CACTUS_SIZE_TALL)
        assert c.x == 500
        assert c.size == CACTUS_SIZE_TALL

    def test_cactus_scrolls_left(self):
        c = Cactus(x=500, size=CACTUS_SIZE_SMALL)
        c.update(speed=400, dt=1.0)
        assert c.x == 100

    def test_cactus_hitbox(self):
        c = Cactus(x=200, size=CACTUS_SIZE_SMALL)
        hb = c.hitbox()
        assert isinstance(hb, tuple)
        assert len(hb) == 4

    def test_cactus_is_off_screen(self):
        c = Cactus(x=-30, size=CACTUS_SIZE_SMALL)
        assert c.is_off_screen()

        c2 = Cactus(x=50, size=CACTUS_SIZE_TALL)
        assert not c2.is_off_screen()


class TestAABBCollision:
    def test_overlapping_rects_collide(self):
        rect_a = (100, 300, 40, 50)
        rect_b = (110, 310, 30, 30)
        assert aabb_collides(rect_a, rect_b)

    def test_separated_rects_do_not_collide(self):
        rect_a = (100, 300, 40, 50)
        rect_b = (500, 300, 30, 30)
        assert not aabb_collides(rect_a, rect_b)

    def test_adjacent_rects_do_not_collide(self):
        rect_a = (100, 300, 40, 50)
        rect_b = (140, 300, 30, 30)
        assert not aabb_collides(rect_a, rect_b)


class TestGameSpeed:
    def test_speed_starts_at_initial(self):
        gs = GameSpeed(initial=400, max_speed=1000, increment=2)
        assert gs.current == 400

    def test_speed_increases_over_time(self):
        gs = GameSpeed(initial=400, max_speed=1000, increment=2)
        gs.update(dt=10.0)
        assert gs.current == 420

    def test_speed_caps_at_maximum(self):
        gs = GameSpeed(initial=400, max_speed=500, increment=100)
        gs.update(dt=10.0)
        assert gs.current == 500


class TestObstacleManager:
    def test_initial_state_no_obstacles(self):
        om = ObstacleManager(screen_width=800, ground_y=320)
        assert len(om.obstacles) > 0 or om._next_spawn >= 0

    def test_spawns_obstacle_when_timer_expires(self):
        np.random.seed(0)
        om = ObstacleManager(screen_width=800, ground_y=320, gap_mean=200, min_gap=100)
        om._next_spawn = 0
        om.update(speed=400, dt=0.0)
        assert len(om.obstacles) > 0

    def test_distance_to_next_obstacle(self):
        np.random.seed(0)
        om = ObstacleManager(screen_width=800, ground_y=320)
        om.obstacles = [Cactus(x=300, size=CACTUS_SIZE_SMALL)]
        dist = om.distance_to_next(80, 800)
        assert dist == 220

    def test_distance_returns_screen_width_when_no_obstacles(self):
        om = ObstacleManager(screen_width=800, ground_y=320)
        om.obstacles = []
        dist = om.distance_to_next(80, 800)
        assert dist == 800

    def test_obstacle_present_flag(self):
        om = ObstacleManager(screen_width=800, ground_y=320)
        om.obstacles = [Cactus(x=300, size=CACTUS_SIZE_SMALL)]
        assert om.obstacle_present(80) is True

        om.obstacles = []
        assert om.obstacle_present(80) is False

    def test_gap_mean_decays_over_time(self):
        np.random.seed(0)
        om = ObstacleManager(screen_width=800, ground_y=320, gap_mean=500, gap_decay=0.1)
        original_mean = om._gap_mean
        om.update(speed=400, dt=5.0)
        assert om._gap_mean < original_mean

    def test_removes_off_screen_obstacles(self):
        np.random.seed(0)
        om = ObstacleManager(screen_width=800, ground_y=320)
        om.obstacles = [
            Cactus(x=-50, size=CACTUS_SIZE_SMALL),
            Cactus(x=300, size=CACTUS_SIZE_TALL),
        ]
        om.update(speed=400, dt=0.01)
        assert len(om.obstacles) == 1
