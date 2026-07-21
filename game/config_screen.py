from collections import namedtuple

import pygame
from game.config import Config, PARAM_SPECS
from game.presets import load_presets, apply_preset, save_user_preset


SaveResult = namedtuple("SaveResult", ["status", "message"])


class ParamGroup:
    def __init__(self, name, params):
        self.name = name
        self.params = params


class ConfigMenu:
    def __init__(self, config):
        self._config = config
        self._groups = self._build_groups()
        self._selected_group = 0
        self._selected_param = 0
        self._param_keys = list(self._groups[0].params.keys())

    def _build_groups(self):
        groups = {}
        for name, default, min_val, max_val, group, label, _type, desc in PARAM_SPECS:
            if group not in groups:
                groups[group] = {}
            groups[group][name] = (default, min_val, max_val, label, desc)
        return [ParamGroup(name, params) for name, params in groups.items()]

    def adjust_param(self, multiplier):
        if not self._groups:
            return
        group = self._groups[self._selected_group]
        key = self._param_keys[self._selected_param]
        param_info = group.params[key]
        default, min_val, max_val, _label, _desc = param_info

        if isinstance(default, str) or default is None:
            return

        new_val = getattr(self._config, key) * multiplier
        if min_val is not None:
            new_val = max(min_val, new_val)
        if max_val is not None:
            new_val = min(max_val, new_val)
        if isinstance(default, int):
            new_val = int(new_val)
        setattr(self._config, key, new_val)

_FITNESS_OPTIONS = ["survival_only", "survival_clearance", "near_miss", "efficiency"]
_GHOST_OPTIONS = ["off", "worst", "random", "top"]
_CROSSOVER_OPTIONS = ["uniform", "single_point", "two_point"]
_MUTATION_ADAPTATION_OPTIONS = ["none", "linear_decay", "diversity_driven"]

_VIEW_TOP = 75
_HINT_BASE = "SPACE=Start  ESC=Quit  ENTER=Edit  ARROWS=Navigate  LEFT/RIGHT=Adjust"


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
        self._presets = load_presets()
        self._preset_index = 0
        self._preset_index_b = 0
        self._focus_preset = False
        self._focus_compare_b = False
        self._compare_mode = False
        self._confirming_preset = False
        self._scroll_offset = 0
        self._input_mode = False
        self._input_buffer = ""
        self.comparison_presets = None
        self._saving_preset = False
        self._save_message = None

    def _build_param_map(self):
        self._param_map = []
        for gi, group in enumerate(self._menu._groups):
            keys = list(group.params.keys())
            for pi, key in enumerate(keys):
                self._param_map.append((gi, pi, key))

    def _sync_group(self):
        self._selected_group = self._param_map[self._selected_param][0]
        self._scroll_to_visible()

    def _handle_input_key(self, key):
        if key == pygame.K_RETURN:
            self._input_mode = False
            key_name = self._current_key()
            group = self._current_group()
            default, min_val, max_val, _label, _desc = group.params[key_name]
            try:
                new_val = float(self._input_buffer) if self._input_buffer else 0
            except ValueError:
                new_val = float(default or 0)
            if min_val is not None:
                new_val = max(min_val, new_val)
            if max_val is not None:
                new_val = min(max_val, new_val)
            if isinstance(default, int):
                new_val = int(new_val)
            setattr(self._config, key_name, new_val)
        elif key == pygame.K_ESCAPE:
            self._input_mode = False
        elif key == pygame.K_BACKSPACE:
            self._input_buffer = self._input_buffer[:-1]
        elif pygame.K_0 <= key <= pygame.K_9:
            self._input_buffer += chr(key)
        elif key == pygame.K_MINUS and self._input_buffer == "":
            self._input_buffer = "-"
        elif key == pygame.K_PERIOD and "." not in self._input_buffer:
            key_name = self._current_key()
            group = self._current_group()
            default, _min, _max, _label, _desc = group.params[key_name]
            if isinstance(default, float):
                self._input_buffer += "."

    def _attempt_save_preset(self, name, path="user_presets.json"):
        try:
            save_user_preset(name, self._config, path=path)
            return SaveResult("saved", name)
        except ValueError as e:
            return SaveResult("error", str(e))
        except Exception as e:
            return SaveResult("error", f"Could not save: {e}")

    def _handle_save_input_key(self, key):
        if key == pygame.K_RETURN:
            self._saving_preset = False
            name = self._input_buffer.strip()
            if not name:
                self._save_message = SaveResult("error", "Name cannot be empty")
            else:
                self._save_message = self._attempt_save_preset(name)
            self._input_buffer = ""
        elif key == pygame.K_ESCAPE:
            self._saving_preset = False
            self._input_buffer = ""
            self._save_message = None
        elif key == pygame.K_BACKSPACE:
            self._input_buffer = self._input_buffer[:-1]
        elif pygame.K_a <= key <= pygame.K_z:
            self._input_buffer += chr(key)
        elif key == pygame.K_SPACE:
            self._input_buffer += " "

    def _scroll_to_visible(self):
        view_bottom = self._screen.get_height() - 55
        row_h = 20

        y = _VIEW_TOP
        group_names = sorted(set(g.name for g in self._menu._groups))
        for group_name in group_names:
            y += 24
            if group_name == self._current_group().name:
                for pi in range(len(self._current_group().params)):
                    if pi == self._param_map[self._selected_param][1]:
                        screen_y = y - self._scroll_offset
                        if screen_y < _VIEW_TOP:
                            self._scroll_offset -= (_VIEW_TOP - screen_y)
                        elif screen_y + row_h > view_bottom:
                            self._scroll_offset += (screen_y + row_h - view_bottom)
                        return
                    y += row_h

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
        if self._confirming_preset:
            if key == pygame.K_RETURN:
                self._confirming_preset = False
                preset = self._presets[self._preset_index]
                apply_preset(self._config, preset)
                self._menu = ConfigMenu(self._config)
                self._build_param_map()
                self._selected_group = 0
                self._selected_param = 0
            elif key == pygame.K_ESCAPE:
                self._confirming_preset = False
            return

        if self._save_message is not None:
            self._save_message = None
            return

        if self._input_mode:
            self._handle_input_key(key)
            return

        if self._saving_preset:
            self._handle_save_input_key(key)
            return

        if key == pygame.K_s and not self._confirming_preset:
            self._saving_preset = True
            self._input_buffer = ""
            self._save_message = None
            return

        if key == pygame.K_c and not self._confirming_preset:
            self._compare_mode = not self._compare_mode
            if self._compare_mode:
                self._focus_compare_b = False
                self._focus_preset = True
            else:
                self._focus_preset = False
                self.comparison_presets = None
            return

        if key == pygame.K_TAB:
            if self._compare_mode:
                self._focus_compare_b = not self._focus_compare_b
            else:
                self._focus_preset = not self._focus_preset
        elif self._focus_preset:
            if self._compare_mode:
                if key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._started = True
                    self._running = False
                    self.comparison_presets = (
                        self._presets[self._preset_index],
                        self._presets[self._preset_index_b],
                    )
                elif key == pygame.K_ESCAPE:
                    self._compare_mode = False
                    self.comparison_presets = None
                elif key == pygame.K_LEFT:
                    if self._focus_compare_b:
                        self._preset_index_b = (self._preset_index_b - 1) % len(self._presets)
                    else:
                        self._preset_index = (self._preset_index - 1) % len(self._presets)
                elif key == pygame.K_RIGHT:
                    if self._focus_compare_b:
                        self._preset_index_b = (self._preset_index_b + 1) % len(self._presets)
                    else:
                        self._preset_index = (self._preset_index + 1) % len(self._presets)
            else:
                if key == pygame.K_RETURN:
                    preset = self._presets[self._preset_index]
                    if preset["name"] != "Default" or len(preset.get("params", {})) > 0:
                        self._confirming_preset = True
                    else:
                        apply_preset(self._config, preset)
                        self._menu = ConfigMenu(self._config)
                        self._build_param_map()
                        self._selected_group = 0
                        self._selected_param = 0
                elif key == pygame.K_SPACE:
                    self._started = True
                    self._running = False
                elif key == pygame.K_ESCAPE:
                    self._running = False
                elif key == pygame.K_LEFT:
                    self._preset_index = (self._preset_index - 1) % len(self._presets)
                elif key == pygame.K_RIGHT:
                    self._preset_index = (self._preset_index + 1) % len(self._presets)
                elif key == pygame.K_DOWN:
                    self._focus_preset = False
        else:
            if key == pygame.K_RETURN:
                key_name = self._current_key()
                group = self._current_group()
                default, _min, _max, _label, _desc = group.params[key_name]
                if isinstance(default, str) or default is None:
                    self._adjust_param(1)
                else:
                    self._input_mode = True
                    self._input_buffer = str(getattr(self._config, key_name))
                return
            elif key == pygame.K_SPACE:
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
            elif key == pygame.K_TAB:
                return

    def _adjust_param(self, direction):
        key = self._current_key()
        group = self._current_group()
        param_info = group.params[key]
        default, min_val, max_val, _label, _desc = param_info

        if isinstance(default, str):
            self._adjust_string_param(key, default, direction)
            return

        if default is None:
            self._adjust_nullable_param(key, direction)
            return

        current = getattr(self._config, key)

        if min_val is not None and max_val is not None:
            if isinstance(default, int):
                step = max(1, int((max_val - min_val) * 0.05))
            else:
                step = (max_val - min_val) * 0.01
        else:
            step = abs(current) * 0.1 if abs(current) > 0.01 else 1

        new_val = current + direction * step

        if min_val is not None:
            new_val = max(min_val, new_val)
        if max_val is not None:
            new_val = min(max_val, new_val)
        if isinstance(default, int):
            new_val = int(new_val)
        setattr(self._config, key, new_val)

    def _adjust_string_param(self, key, default, direction):
        if key == "ghost_mode":
            options = _GHOST_OPTIONS
        elif key == "crossover_operator":
            options = _CROSSOVER_OPTIONS
        elif key == "mutation_adaptation":
            options = _MUTATION_ADAPTATION_OPTIONS
        else:
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

        if self._compare_mode:
            self._render_compare_presets()
        else:
            self._render_single_preset()

        if self._confirming_preset:
            box_w = 400
            box_h = 60
            box_x = (self._screen.get_width() - box_w) // 2
            box_y = (self._screen.get_height() - box_h) // 2
            pygame.draw.rect(self._screen, (50, 50, 60), (box_x, box_y, box_w, box_h))
            pygame.draw.rect(self._screen, (200, 200, 100), (box_x, box_y, box_w, box_h), 2)
            preset = self._presets[self._preset_index]
            msg = self._font.render(
                f"Load preset '{preset['name']}'?  ENTER=Yes  ESC=No",
                True, (255, 255, 200))
            msg_rect = msg.get_rect(center=(self._screen.get_width() // 2, self._screen.get_height() // 2))
            self._screen.blit(msg, msg_rect)
            if self._focus_preset:
                hint = self._font.render("TAB=switch focus  SPACE=Start  ENTER=load preset  ARROWS=cycle presets", True, (120, 120, 140))
                self._screen.blit(hint, (20, self._screen.get_height() - 30))
            else:
                hint = self._font.render(f"{_HINT_BASE}  S=Save preset", True, (120, 120, 140))
                self._screen.blit(hint, (20, self._screen.get_height() - 30))
            pygame.display.flip()
            return

        if self._saving_preset or self._save_message is not None:
            box_w = 500
            box_h = 80
            box_x = (self._screen.get_width() - box_w) // 2
            box_y = (self._screen.get_height() - box_h) // 2
            pygame.draw.rect(self._screen, (50, 50, 60), (box_x, box_y, box_w, box_h))
            pygame.draw.rect(self._screen, (100, 200, 100), (box_x, box_y, box_w, box_h), 2)
            if self._saving_preset:
                title = self._font.render("Save preset as:", True, (200, 200, 255))
                self._screen.blit(title, (box_x + 20, box_y + 12))
                value = self._font.render(f"{self._input_buffer}_", True, (255, 255, 100))
                self._screen.blit(value, (box_x + 20, box_y + 38))
                hint = self._font.render("ENTER=Save  ESC=Cancel  (appears on next launch)", True, (150, 150, 200))
                self._screen.blit(hint, (box_x + 20, box_y + 58))
            else:
                status, message = self._save_message
                if status == "saved":
                    text = self._font.render(
                        f"Saved '{message}' — appears on next launch",
                        True, (100, 255, 100))
                else:
                    text = self._font.render(f"Error: {message}", True, (255, 100, 100))
                text_rect = text.get_rect(
                    center=(self._screen.get_width() // 2, self._screen.get_height() // 2))
                self._screen.blit(text, text_rect)
                hint = self._font.render("Press any key to continue", True, (150, 150, 200))
                hint_rect = hint.get_rect(
                    center=(self._screen.get_width() // 2, self._screen.get_height() // 2 + 24))
                self._screen.blit(hint, hint_rect)
            pygame.display.flip()
            return

        if not self._compare_mode:
            y = _VIEW_TOP
            group_names = sorted(set(g.name for g in self._menu._groups))
            current_group_name = self._current_group().name

            for group_name in group_names:
                screen_y = y - self._scroll_offset
                color = (255, 255, 100) if group_name == current_group_name else (150, 150, 150)
                if screen_y >= _VIEW_TOP:
                    label = self._font.render(group_name.upper(), True, color)
                    self._screen.blit(label, (20, screen_y))
                y += 24

                if group_name == current_group_name:
                    group = self._current_group()
                    selected_desc = ""
                    for pi, (key, (default, min_val, max_val, label, desc)) in enumerate(group.params.items()):
                        param_idx = next(i for i, (gi, pii, k) in enumerate(self._param_map)
                                         if gi == self._selected_group and pii == pi)
                        selected = param_idx == self._selected_param and not self._focus_preset
                        if selected:
                            selected_desc = desc

                        screen_y = y - self._scroll_offset
                        if screen_y >= _VIEW_TOP:
                            prefix = ">" if selected else " "
                            value = getattr(self._config, key)
                            if selected and self._input_mode:
                                value_str = self._input_buffer + "_"
                            elif value is None:
                                value_str = "Random"
                            elif isinstance(value, str):
                                value_str = value
                            elif isinstance(value, float):
                                value_str = f"{value:.3f}"
                            else:
                                value_str = str(value)

                            color = (255, 255, 255) if selected else (180, 180, 200)
                            text = self._font.render(f"{prefix} {label:25s} {value_str:>12s}", True, color)
                            self._screen.blit(text, (30, screen_y))
                        y += 20

            if selected_desc and not self._focus_preset:
                desc_text = self._font.render(selected_desc, True, (100, 180, 255))
                self._screen.blit(desc_text, (20, self._screen.get_height() - 50))

        if self._compare_mode:
            hint = self._font.render(
                "C=toggle compare  TAB=switch A/B  SPACE=Start  ESC=quit  ARROWS=cycle preset",
                True, (120, 120, 140))
        elif self._focus_preset:
            hint = self._font.render("TAB=switch focus  SPACE=Start  ENTER=load preset  ARROWS=cycle presets  C=compare", True, (120, 120, 140))
        else:
            hint = self._font.render(f"{_HINT_BASE}  S=Save preset  C=compare", True, (120, 120, 140))
        self._screen.blit(hint, (20, self._screen.get_height() - 30))
        pygame.display.flip()

    def _render_single_preset(self):
        preset = self._presets[self._preset_index]
        preset_color = (100, 255, 100) if self._focus_preset else (150, 150, 150)
        preset_label = self._font.render("Preset:", True, preset_color)
        self._screen.blit(preset_label, (20, 40))

        brackets = "<" if self._focus_preset else " "
        close_b = ">" if self._focus_preset else " "
        preset_name = f"{brackets} {preset['name']:30s} {close_b}"
        name_color = (255, 255, 150) if self._focus_preset else (180, 180, 200)
        name_text = self._font.render(preset_name, True, name_color)
        self._screen.blit(name_text, (110, 40))

        desc_line = preset.get("description", "")
        if self._focus_preset:
            desc_text = self._font.render(desc_line, True, (100, 180, 255))
            self._screen.blit(desc_text, (20, self._screen.get_height() - 50))

    def _render_compare_presets(self):
        preset_a = self._presets[self._preset_index]
        preset_b = self._presets[self._preset_index_b]
        focus_a = not self._focus_compare_b

        preset_label_a = self._font.render("Preset A:", True, (100, 255, 100))
        self._screen.blit(preset_label_a, (20, 40))

        brackets_a = "<" if focus_a else " "
        close_a = ">" if focus_a else " "
        preset_name_a = f"{brackets_a} {preset_a['name']:30s} {close_a}"
        name_color_a = (255, 255, 150) if focus_a else (180, 180, 200)
        name_text_a = self._font.render(preset_name_a, True, name_color_a)
        self._screen.blit(name_text_a, (130, 40))

        preset_label_b = self._font.render("Preset B:", True, (100, 255, 100))
        self._screen.blit(preset_label_b, (20, 62))

        brackets_b = "<" if not focus_a else " "
        close_b = ">" if not focus_a else " "
        preset_name_b = f"{brackets_b} {preset_b['name']:30s} {close_b}"
        name_color_b = (255, 255, 150) if not focus_a else (180, 180, 200)
        name_text_b = self._font.render(preset_name_b, True, name_color_b)
        self._screen.blit(name_text_b, (130, 62))

        focus_preset = preset_a if focus_a else preset_b
        desc_text = self._font.render(focus_preset.get("description", ""), True, (100, 180, 255))
        self._screen.blit(desc_text, (20, self._screen.get_height() - 50))
