import pygame


def _dino_grounded_surface(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    body_color = (60, 60, 60)
    eye_color = (255, 255, 255)
    belly_color = (100, 100, 100)

    rw, rh = w * 4 // 5, h * 4 // 5
    pygame.draw.rect(surf, body_color, (w - rw, 0, rw, rh))

    head_w, head_h = w // 3, h // 3
    pygame.draw.rect(surf, body_color, (w - rw, 1, head_w, head_h))

    pygame.draw.circle(surf, eye_color, (w - rw + head_w - 4, head_h // 2), 2)

    leg_w, leg_h = w // 6, h // 5
    pygame.draw.rect(surf, body_color, (w - rw + 3, rh - 1, leg_w, leg_h))
    pygame.draw.rect(surf, body_color, (w - rw + 8, rh - 1, leg_w, leg_h))

    arm_w, arm_h = w // 5, h // 10
    pygame.draw.rect(surf, body_color, (w - rw + 6, rh // 2, arm_w, arm_h))

    tail_pts = [(w - rw - 2, rh // 3), (0, rh // 2 - 2), (0, rh // 2 + 4), (w - rw - 1, rh * 3 // 4)]
    pygame.draw.polygon(surf, body_color, tail_pts)

    belly_x = w - rw + 6
    belly_w = rw - 12
    pygame.draw.rect(surf, belly_color, (belly_x, rh // 3, belly_w, rh // 3))

    return surf


def _cactus_small_surface(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    body_color = (34, 139, 34)
    spine_color = (0, 80, 0)

    trunk_w = w * 3 // 5
    pygame.draw.rect(surf, body_color, (w // 5, 0, trunk_w, h))
    pygame.draw.rect(surf, body_color, (0, h // 4, trunk_w, trunk_w))
    pygame.draw.rect(surf, body_color, (w - trunk_w, h // 3, trunk_w, trunk_w))

    r = int(1.5)
    pygame.draw.circle(surf, spine_color, (w // 3, 0), r)
    pygame.draw.circle(surf, spine_color, (w // 2, h // 5), r)
    pygame.draw.circle(surf, spine_color, (w * 2 // 3, h // 3), r)

    return surf


def _cactus_tall_surface(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    body_color = (0, 128, 0)
    spine_color = (34, 139, 34)

    trunk_w = w * 3 // 5
    pygame.draw.rect(surf, body_color, (w // 5, 0, trunk_w, h))

    arm_w = trunk_w
    arm_h = h // 5
    pygame.draw.rect(surf, body_color, (0, h // 4, arm_w, arm_h))
    pygame.draw.rect(surf, body_color, (w - arm_w, h // 3, arm_w, arm_h))

    r = int(1.5)
    pygame.draw.circle(surf, spine_color, (w // 4, h // 6), r)
    pygame.draw.circle(surf, spine_color, (w * 3 // 4, h // 4), r)
    pygame.draw.circle(surf, spine_color, (w // 2, h // 2), r)

    return surf


def _pterodactyl_surface(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    body_color = (139, 69, 19)
    wing_color = (100, 50, 14)
    eye_color = (255, 255, 100)

    body_x, body_w = w // 3, w // 3
    body_h = h * 2 // 3
    body_y = h - body_h
    pygame.draw.ellipse(surf, body_color, (body_x, body_y, body_w, body_h))

    wing_pts = [
        (body_x + body_w // 2, body_y + 2),
        (0, body_y - h // 4),
        (body_x + body_w // 4, body_y + body_h // 2),
    ]
    pygame.draw.polygon(surf, wing_color, wing_pts)

    wing_pts_r = [
        (body_x + body_w // 2, body_y + 2),
        (w, body_y - h // 4),
        (body_x + body_w * 3 // 4, body_y + body_h // 2),
    ]
    pygame.draw.polygon(surf, wing_color, wing_pts_r)

    head_x = body_x + body_w - 4
    head_y = body_y - 4
    head_w, head_h = 8, 6
    pygame.draw.ellipse(surf, body_color, (head_x, head_y, head_w, head_h))
    pygame.draw.circle(surf, eye_color, (head_x + head_w - 2, head_y + 2), 1)

    beak_x = head_x + head_w - 1
    pygame.draw.polygon(surf, (255, 200, 50), [
        (beak_x, head_y + 2),
        (beak_x + 5, head_y + head_h // 2),
        (beak_x, head_y + head_h - 2),
    ])

    return surf


def _ground_surface(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    dirt = (83, 83, 83)
    grass = (34, 139, 34)

    surf.fill(dirt)
    grass_h = h // 6
    pygame.draw.rect(surf, grass, (0, 0, w, grass_h))

    for i in range(0, w, 12):
        off = (i // 12) % 3
        pygame.draw.line(surf, grass, (i + off, 0), (i + off, grass_h * 2), 1)

    return surf


_PIXEL_SPRITES = {
    "dino.png": _dino_grounded_surface,
    "cactus_small.png": _cactus_small_surface,
    "cactus_tall.png": _cactus_tall_surface,
    "pterodactyl.png": _pterodactyl_surface,
    "ground.png": _ground_surface,
}


def generate_pixel_sprite(name, width, height):
    if name in _PIXEL_SPRITES:
        return _PIXEL_SPRITES[name](width, height)
    return None
