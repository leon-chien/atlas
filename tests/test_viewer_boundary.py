from __future__ import annotations

import pytest

from atlas.core.filesystem import create_project
from atlas.viewer import open_viewer


def test_viewer_boundary_reports_expected_artifacts(tmp_path):
    paths = create_project(tmp_path / "scan")

    with pytest.raises(NotImplementedError, match="atlas_world.ply"):
        open_viewer(paths.root)
