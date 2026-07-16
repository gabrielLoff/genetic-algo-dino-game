from game.config_screen import ConfigMenu, ParamGroup
from game.config import Config


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
