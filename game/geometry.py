def inset_hitbox(x, y, w, h, inset_fraction):
    inset_x = w * inset_fraction
    inset_y = h * inset_fraction
    return (
        x + inset_x,
        y + inset_y,
        w - 2 * inset_x,
        h - 2 * inset_y,
    )


def aabb_collides(rect_a, rect_b):
    ax, ay, aw, ah = rect_a
    bx, by, bw, bh = rect_b
    return (
        ax < bx + bw
        and ax + aw > bx
        and ay < by + bh
        and ay + ah > by
    )
