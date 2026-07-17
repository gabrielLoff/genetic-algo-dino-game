from game.config_screen import ConfigMenu, ParamGroup, ConfigScreen, _VIEW_TOP
from game.config import Config
import pygame


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


def test_render_handles_large_scroll_offset():
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    config = Config()
    cs = ConfigScreen(config, screen)
    cs._scroll_offset = 200
    try:
        cs._render()
    finally:
        pygame.quit()


def test_view_top_constant_exists():
    assert _VIEW_TOP == 75
