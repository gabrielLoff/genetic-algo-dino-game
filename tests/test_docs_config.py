import re
from pathlib import Path

import pytest

from game.config import PARAM_SPECS


def _docs_dir():
    return Path(__file__).resolve().parents[1] / "docs" / "configs"


def _group_to_filename(group):
    return group.lower().replace(" ", "-")


def _params_by_group():
    groups = {}
    for spec in PARAM_SPECS:
        name, _default, _min, _max, group, _label, _type, _desc, _options = spec
        groups.setdefault(group, []).append(name)
    return groups


def _h3_headings(path):
    if not path.exists():
        return None
    headings = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^###\s+(.*?)\s*$", line)
        if m:
            headings.append(m.group(1).strip("`").strip())
    return headings


def _load_group_doc(group):
    filename = _group_to_filename(group) + ".md"
    path = _docs_dir() / filename
    params = _params_by_group().get(group, [])
    headings = _h3_headings(path) or []
    return params, headings, path


class TestDocsConfigExists:
    def test_every_group_has_a_doc_file(self):
        for group, params in _params_by_group().items():
            _, _, path = _load_group_doc(group)
            assert path.exists(), (
                f"Missing {path.relative_to(_docs_dir().parent)} — required because "
                f"PARAM_SPECS has these parameters in the {group!r} group: {params}. "
                f"Add an H3 entry for each, e.g. `### \\`{params[0]}\\``"
            )


class TestDocsConfigCoverage:
    @pytest.mark.parametrize("group", list({s[4] for s in PARAM_SPECS}))
    def test_every_param_in_group_has_h3_heading(self, group):
        params, headings, path = _load_group_doc(group)
        assert path.exists(), (
            f"Missing {path.relative_to(_docs_dir().parent)} — required because "
            f"PARAM_SPECS has these parameters in the {group!r} group: {params}"
        )
        headings_set = set(headings)
        missing = [p for p in params if p not in headings_set]
        assert not missing, (
            f"{path.relative_to(_docs_dir().parent)} is missing H3 entries for these "
            f"parameters from the {group!r} group: {missing}. "
            f"Add `### `{missing[0]}` ` (and one per missing name) to the file."
        )
