from game.config_screen import ConfigMenu, ParamGroup, ConfigScreen, _VIEW_TOP
from game.config import Config
import pygame
import os
import json
import pytest


@pytest.fixture
def config_screen():
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    config = Config()
    cs = ConfigScreen(config, screen)
    try:
        yield cs
    finally:
        pygame.quit()


def test_param_group_creates_with_name_and_params():
    params = {"pop_size": (100, 10, 500, "Population Size")}
    group = ParamGroup("GA", params)
    assert group.name == "GA"
    assert len(group.params) == 1


def test_config_menu_groups_all_parameters():
    config = Config()
    menu = ConfigMenu(config)
    groups = menu._groups
    group_names = {g.name for g in groups}
    assert "Genetic Algorithm" in group_names or "GA" in group_names
    assert "Neural Network" in group_names or "NN" in group_names
    assert "Game" in group_names


def test_config_menu_tracks_selected_parameter():
    config = Config()
    menu = ConfigMenu(config)
    assert 0 <= menu._selected_group < len(menu._groups)
    assert 0 <= menu._selected_param < len(menu._groups[menu._selected_group].params)


def test_config_menu_updates_config_on_value_change():
    config = Config()
    menu = ConfigMenu(config)
    orig = config.population_size
    menu.adjust_param(1.5)
    assert config.population_size != orig


def test_render_handles_large_scroll_offset(config_screen):
    config_screen._scroll_offset = 200
    config_screen._render()


def test_view_top_constant_exists():
    assert _VIEW_TOP == 75


def test_attempt_save_preset_writes_file(config_screen, tmp_path):
    config_screen._config.population_size = 50
    path = str(tmp_path / "user_presets.json")
    result = config_screen._attempt_save_preset("MyPreset", path=path)
    assert result.status == "saved"
    assert result.message == "MyPreset"
    assert os.path.exists(path)
    with open(path) as f:
        data = json.load(f)
    assert any(p["name"] == "MyPreset" for p in data["presets"])


def test_attempt_save_preset_rejects_default_name(config_screen, tmp_path):
    path = str(tmp_path / "user_presets.json")
    result = config_screen._attempt_save_preset("Default", path=path)
    assert result.status == "error"
    assert "reserved" in result.message.lower()
    assert not os.path.exists(path)


def test_attempt_save_preset_captures_current_config(config_screen, tmp_path):
    config_screen._config.population_size = 75
    config_screen._config.mutation_rate = 0.42
    path = str(tmp_path / "user_presets.json")
    config_screen._attempt_save_preset("MyPreset", path=path)
    with open(path) as f:
        data = json.load(f)
    preset = next(p for p in data["presets"] if p["name"] == "MyPreset")
    assert preset["params"]["population_size"] == 75
    assert preset["params"]["mutation_rate"] == 0.42
    assert "hidden_layer_size" not in preset["params"]


def test_scroll_to_visible_keeps_item_in_viewport(config_screen):
    cs = config_screen
    group_names = sorted(set(g.name for g in cs._menu._groups))
    last_group_name = group_names[-1]

    for gi, group in enumerate(cs._menu._groups):
        if group.name == last_group_name:
            cs._selected_group = gi
            break

    cs._menu._selected_group = cs._selected_group
    cs._selected_param = next(
        i for i, (g, p, k) in enumerate(cs._param_map)
        if g == cs._selected_group and p == 0
    )

    cs._scroll_offset = 200
    screen_height = cs._screen.get_height()
    view_bottom = screen_height - 55

    cs._scroll_to_visible()

    y = _VIEW_TOP
    for gi, group in enumerate(cs._menu._groups):
        y += 24
        for pi in range(len(group.params)):
            if gi == cs._selected_group and pi == cs._param_map[cs._selected_param][1]:
                screen_y = y - cs._scroll_offset
                assert screen_y >= _VIEW_TOP, (
                    f"selected item above viewport: screen_y={screen_y}"
                )
                assert screen_y + 20 <= view_bottom, (
                    f"selected item below viewport: screen_y={screen_y}"
                )
                break
            if gi == cs._selected_group:
                y += 20
