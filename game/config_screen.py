import pygame
from game.config_menu import ConfigMenu

_FITNESS_OPTIONS = ["survival_only", "survival_clearance", "near_miss", "efficiency"]


class ConfigScreen:
    def __init__(self, config, screen):
        self._config = config
        self._screen = screen
        self._menu = ConfigMenu(config)
        self._font = pygame.font.SysFont("monospace", 16)
        self._title_font = pygame.font.SysFont("monospace", 20, bold=True)
        self._running = True
        self._selected_group = 0
        self._selected_param = 0
        self._started = False
        self._build_param_map()

    def _build_param_map(self):
        self._param_map = []
        for gi, group in enumerate(self._menu._groups):
            keys = list(group.params.keys())
            for pi, key in enumerate(keys):
                self._param_map.append((gi, pi, key))

    def _sync_group(self):
        self._selected_group = self._param_map[self._selected_param][0]

    def _current_group(self):
        return self._menu._groups[self._selected_group]

    def _current_key(self):
        return self._param_map[self._selected_param][2]

    def run(self):
        clock = pygame.time.Clock()

        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)

            self._render()
            clock.tick(30)

        return self._started

    def _handle_key(self, key):
        if key == pygame.K_RETURN:
            self._started = True
            self._running = False
        elif key == pygame.K_ESCAPE:
            self._running = False
        elif key == pygame.K_DOWN:
            self._selected_param = (self._selected_param + 1) % len(self._param_map)
            self._sync_group()
        elif key == pygame.K_UP:
            self._selected_param = (self._selected_param - 1) % len(self._param_map)
            self._sync_group()
        elif key == pygame.K_LEFT:
            self._adjust_param(-1)
        elif key == pygame.K_RIGHT:
            self._adjust_param(1)

    def _adjust_param(self, direction):
        key = self._current_key()
        group = self._current_group()
        param_info = group.params[key]
        default, min_val, max_val, _label = param_info

        if isinstance(default, str):
            self._adjust_string_param(key, default, direction)
            return

        if default is None:
            self._adjust_nullable_param(key, direction)
            return

        current = getattr(self._config, key)

        if isinstance(default, int):
            step = max(1, int(abs(current) * 0.1))
            new_val = current + direction * step
        else:
            step = abs(current) * 0.1 if abs(current) > 0.01 else 0.1
            new_val = current + direction * step

        if min_val is not None:
            new_val = max(min_val, new_val)
        if max_val is not None:
            new_val = min(max_val, new_val)
        if isinstance(default, int):
            new_val = int(new_val)
        setattr(self._config, key, new_val)

    def _adjust_string_param(self, key, default, direction):
        options = _FITNESS_OPTIONS
        current = getattr(self._config, key)
        try:
            idx = options.index(current)
        except ValueError:
            idx = 0
        idx = (idx + direction) % len(options)
        setattr(self._config, key, options[idx])

    def _adjust_nullable_param(self, key, direction):
        current = getattr(self._config, key)
        if current is None:
            setattr(self._config, key, max(0, direction))
        else:
            new_val = current + direction
            setattr(self._config, key, max(0, new_val))

    def _render(self):
        self._screen.fill((30, 30, 40))
        title = self._title_font.render("GA Dino Game — Configuration", True, (200, 200, 255))
        self._screen.blit(title, (20, 10))

        y = 50
        group_names = sorted(set(g.name for g in self._menu._groups))
        current_group_name = self._current_group().name

        for group_name in group_names:
            color = (255, 255, 100) if group_name == current_group_name else (150, 150, 150)
            label = self._font.render(group_name.upper(), True, color)
            self._screen.blit(label, (20, y))
            y += 24

            if group_name == current_group_name:
                group = self._current_group()
                for pi, (key, (default, min_val, max_val, label)) in enumerate(group.params.items()):
                    param_idx = next(i for i, (gi, pii, k) in enumerate(self._param_map)
                                     if gi == self._selected_group and pii == pi)
                    selected = param_idx == self._selected_param

                    prefix = ">" if selected else " "
                    value = getattr(self._config, key)
                    if value is None:
                        value_str = "Random"
                    elif isinstance(value, str):
                        value_str = value
                    elif isinstance(value, float):
                        value_str = f"{value:.3f}"
                    else:
                        value_str = str(value)

                    color = (255, 255, 255) if selected else (180, 180, 200)
                    text = self._font.render(f"{prefix} {label:25s} {value_str:>12s}", True, color)
                    self._screen.blit(text, (30, y))
                    y += 20

        hint = self._font.render("ENTER=Start  ESC=Quit  ARROWS=Navigate  LEFT/RIGHT=Adjust", True, (120, 120, 140))
        self._screen.blit(hint, (20, self._screen.get_height() - 30))
        pygame.display.flip()
