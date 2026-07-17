import os
import pygame

_SPRITE_CACHE = {}

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sprites")


def _load_image(path, width, height):
    if not os.path.exists(path):
        return None
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (width, height))
    except pygame.error:
        return None


def get_sprite(name, width, height, fallback_color=None):
    key = (name, width, height)
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    path = os.path.join(ASSETS_DIR, name)
    image = _load_image(path, width, height)
    if image is not None:
        _SPRITE_CACHE[key] = image
        return image

    if fallback_color is not None:
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.fill(fallback_color)
        _SPRITE_CACHE[key] = surf
        return surf

    return None


def render_dino(screen, x, y):
    sprite = get_sprite("dino.png", 40, 50, fallback_color=(50, 50, 50))
    if sprite:
        screen.blit(sprite, (x, y - sprite.get_height()))


def render_cactus(screen, x, ground_y, size):
    if size == "tall":
        sprite = get_sprite("cactus_tall.png", 25, 55, fallback_color=(0, 128, 0))
    else:
        sprite = get_sprite("cactus_small.png", 20, 40, fallback_color=(0, 100, 0))
    if sprite:
        screen.blit(sprite, (x, ground_y - sprite.get_height()))


def render_pterodactyl(screen, x, ground_y, height_level):
    from game.obstacle import _PTERO_DIMS, _PTERO_HEIGHT_Y

    width, height = _PTERO_DIMS
    height_ratio = _PTERO_HEIGHT_Y.get(height_level, 0.5)
    y = int(ground_y - height - ground_y * height_ratio)

    sprite = get_sprite("pterodactyl.png", width, height, fallback_color=(139, 69, 19))
    if sprite:
        screen.blit(sprite, (x, y))


def render_ground(screen, ground_y, ground_h, offset):
    sprite = get_sprite("ground.png", 800, ground_h, fallback_color=(83, 83, 83))
    if sprite:
        for i in range(-1, 3):
            screen.blit(sprite, (i * 800 - offset, ground_y))


def render_background(screen, screen_w, screen_h):
    sprite = get_sprite("background.png", screen_w, screen_h)
    if sprite:
        screen.blit(sprite, (0, 0))
    else:
        screen.fill((255, 255, 255))
