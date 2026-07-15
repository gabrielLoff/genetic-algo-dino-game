import pygame
import pytest
from game.config import Config
from game.loop import GameLoop


class FakeClock:
    def __init__(self):
        self._last_tick = 0
        self.tick_count = 0

    def tick(self, fps):
        self.tick_count += 1
        elapsed = 1000 / fps
        self._last_tick += elapsed
        return int(elapsed)

    def get_fps(self):
        return 60


class FakeDisplay:
    def fill(self, color):
        pass


def _fake_init():
    pass


def _fake_quit():
    pass


def _fake_set_mode(size, flags=0):
    return FakeDisplay()


def _fake_set_caption(title):
    pass


def _fake_flip():
    pass


def _fake_event_get():
    if not hasattr(_fake_event_get, "call_count"):
        _fake_event_get.call_count = 0
    _fake_event_get.call_count += 1
    if _fake_event_get.call_count > 5:
        return [pygame.event.Event(pygame.QUIT)]
    return []


def test_game_loop_creates_window_with_config_dimensions():
    display_modes = []
    def record_mode(size, flags=0):
        display_modes.append(size)
        return FakeDisplay()

    original_set_mode = pygame.display.set_mode
    original_init = pygame.init
    original_quit = pygame.quit
    original_event_get = pygame.event.get
    original_flip = pygame.display.flip

    try:
        pygame.display.set_mode = record_mode
        pygame.init = _fake_init
        pygame.quit = _fake_quit
        pygame.event.get = _fake_event_get
        pygame.display.flip = _fake_flip
        _fake_event_get.call_count = 0

        config = Config()
        loop = GameLoop(config)
        loop.run()

        assert len(display_modes) == 1
        assert display_modes[0] == (800, 400)
    finally:
        pygame.display.set_mode = original_set_mode
        pygame.init = original_init
        pygame.quit = original_quit
        pygame.event.get = original_event_get
        pygame.display.flip = original_flip


def test_fixed_timestep_accumulator():
    config = Config()

    original_clock = pygame.time.Clock
    pygame.time.Clock = lambda: FakeClock()
    original_init = pygame.init
    original_quit = pygame.quit
    original_set_mode = pygame.display.set_mode
    original_event_get = pygame.event.get
    original_set_caption = pygame.display.set_caption
    original_flip = pygame.display.flip

    try:
        pygame.init = _fake_init
        pygame.quit = _fake_quit
        pygame.display.set_mode = lambda size, flags=0: FakeDisplay()
        pygame.display.set_caption = _fake_set_caption
        pygame.display.flip = _fake_flip
        _fake_event_get.call_count = 0
        pygame.event.get = _fake_event_get

        updates = []
        def on_update(dt):
            updates.append(dt)

        loop = GameLoop(config, on_update=on_update, dt=1/60)
        loop.run()

        assert len(updates) > 0
        for dt in updates:
            assert abs(dt - 1/60) < 0.001
    finally:
        pygame.time.Clock = original_clock
        pygame.init = original_init
        pygame.quit = original_quit
        pygame.display.set_mode = original_set_mode
        pygame.event.get = original_event_get
        pygame.display.set_caption = original_set_caption
        pygame.display.flip = original_flip


def test_game_loop_handles_quit_event():
    config = Config()

    original_init = pygame.init
    original_quit = pygame.quit
    original_set_mode = pygame.display.set_mode
    original_set_caption = pygame.display.set_caption
    original_event_get = pygame.event.get
    original_flip = pygame.display.flip

    try:
        pygame.init = _fake_init
        pygame.quit = _fake_quit
        pygame.display.set_mode = lambda size, flags=0: FakeDisplay()
        pygame.display.set_caption = _fake_set_caption
        pygame.display.flip = _fake_flip
        _fake_event_get.call_count = 0
        pygame.event.get = _fake_event_get

        loop = GameLoop(config)
        loop.run()

        assert _fake_event_get.call_count > 0
    finally:
        pygame.init = original_init
        pygame.quit = original_quit
        pygame.display.set_mode = original_set_mode
        pygame.event.get = original_event_get
        pygame.display.set_caption = original_set_caption
        pygame.display.flip = original_flip
