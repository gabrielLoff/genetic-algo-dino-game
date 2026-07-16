import pygame
from game.sprites import get_sprite, render_dino, render_cactus, render_ground, render_background


def test_get_sprite_falls_back_to_colored_rect():
    sprite = get_sprite("nonexistent.png", 40, 50, fallback_color=(100, 100, 100))
    assert sprite is not None
    assert sprite.get_width() == 40
    assert sprite.get_height() == 50


def test_get_sprite_returns_none_without_fallback():
    sprite = get_sprite("nonexistent2.png", 40, 50, fallback_color=None)
    assert sprite is None


def test_get_sprite_caches_result():
    s1 = get_sprite("cache_test.png", 10, 10, fallback_color=(200, 0, 0))
    s2 = get_sprite("cache_test.png", 10, 10, fallback_color=(200, 0, 0))
    assert s1 is s2


def test_render_functions_do_not_crash_with_missing_sprites():
    screen = pygame.Surface((800, 400))
    render_background(screen, 800, 400)
    render_ground(screen, 320, 80, 0)
    render_dino(screen, 80, 320)
    render_cactus(screen, 500, 320, "small")
    render_cactus(screen, 600, 320, "tall")
