from game.config_screen import ConfigScreen, _VIEW_TOP
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


def test_build_groups_returns_all_parameter_groups(config_screen):
    cs = config_screen
    group_names = {g["name"] for g in cs._groups}
    assert "Genetic Algorithm" in group_names or "GA" in group_names
    assert "Neural Network" in group_names or "NN" in group_names
    assert "Game" in group_names


def test_config_screen_tracks_selected_parameter(config_screen):
    cs = config_screen
    assert 0 <= cs._selected_group < len(cs._groups)
    assert 0 <= cs._selected_param < len(cs._groups[cs._selected_group]["params"])


def test_config_screen_adjust_param_changes_value(config_screen):
    cs = config_screen
    cs._selected_group = 0
    cs._selected_param = 0
    orig = cs._config.population_size
    cs._handle_key(pygame.K_RIGHT)
    assert cs._config.population_size != orig


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
    view_bottom = cs._screen.get_height() - 55

    game_group_idx = next(
        i for i, g in enumerate(cs._groups) if g["name"] == "Game"
    )
    cs._selected_group = game_group_idx

    last_game_param = len(cs._current_group()["params"]) - 1
    cs._selected_param = next(
        i for i, (g, p, k) in enumerate(cs._param_map)
        if g == cs._selected_group and p == last_game_param
    )

    cs._scroll_offset = 200
    cs._scroll_to_visible()

    y = _VIEW_TOP
    group_names = sorted(set(g["name"] for g in cs._groups))
    for group_name in group_names:
        y += 24
        if group_name == cs._current_group()["name"]:
            for pi in range(len(cs._current_group()["params"])):
                if pi == cs._param_map[cs._selected_param][1]:
                    screen_y = y - cs._scroll_offset
                    assert screen_y >= _VIEW_TOP, (
                        f"selected item above viewport: screen_y={screen_y}"
                    )
                    assert screen_y + 20 <= view_bottom, (
                        f"selected item below viewport: screen_y={screen_y}"
                    )
                    return
                y += 20


def test_tour_mode_loads_descriptions(config_screen):
    cs = config_screen
    assert len(cs._tour_descriptions) > 0
    assert "population_size" in cs._tour_descriptions
    assert "hidden_layer_size" in cs._tour_descriptions
    assert "game_speed_initial" in cs._tour_descriptions


def test_tour_mode_toggles_on_t_key(config_screen):
    cs = config_screen
    assert not cs._tour_mode
    cs._handle_key(pygame.K_t)
    assert cs._tour_mode
    assert cs._tour_step == 0
    cs._handle_key(pygame.K_t)
    assert not cs._tour_mode


def test_tour_mode_arrow_keys_navigate_steps(config_screen):
    cs = config_screen
    cs._tour_mode = True
    cs._tour_step = 0
    cs._handle_key(pygame.K_RIGHT)
    assert cs._tour_step == 1
    cs._handle_key(pygame.K_LEFT)
    assert cs._tour_step == 0
    cs._handle_key(pygame.K_LEFT)
    total = cs._max_tour_step()
    assert cs._tour_step == total - 1


def test_tour_mode_exits_on_esc(config_screen):
    cs = config_screen
    cs._tour_mode = True
    cs._handle_key(pygame.K_ESCAPE)
    assert not cs._tour_mode


def test_tour_mode_does_not_block_space_start(config_screen):
    cs = config_screen
    cs._tour_mode = True
    cs._handle_key(pygame.K_SPACE)
    assert not cs._tour_mode
    assert cs._started


def test_normal_mode_unaffected_by_tour_state(config_screen):
    cs = config_screen
    cs._tour_mode = False
    initial_param = cs._selected_param
    cs._handle_key(pygame.K_DOWN)
    assert cs._selected_param != initial_param
