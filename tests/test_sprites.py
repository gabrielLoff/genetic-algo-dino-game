import pygame
from game.sprites import get_sprite, render_dino, render_cactus, render_pterodactyl, render_ground, render_background
from game.pixel_sprites import generate_pixel_sprite


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
    render_pterodactyl(screen, 700, 320, "low")
    render_pterodactyl(screen, 750, 320, "high")


def test_pixel_sprite_generates_dino():
    surf = generate_pixel_sprite("dino.png", 40, 50)
    assert surf is not None
    assert surf.get_width() == 40
    assert surf.get_height() == 50


def test_pixel_sprite_generates_cactus():
    surf = generate_pixel_sprite("cactus_small.png", 20, 40)
    assert surf is not None
    assert surf.get_width() == 20
    assert surf.get_height() == 40


def test_pixel_sprite_generates_pterodactyl():
    surf = generate_pixel_sprite("pterodactyl.png", 35, 28)
    assert surf is not None
    assert surf.get_width() == 35
    assert surf.get_height() == 28


def test_pixel_sprite_generates_ground():
    surf = generate_pixel_sprite("ground.png", 800, 80)
    assert surf is not None
    assert surf.get_width() == 800
    assert surf.get_height() == 80


def test_pixel_sprite_returns_none_for_unknown():
    assert generate_pixel_sprite("unknown.png", 10, 10) is None
