from __future__ import annotations

import importlib.util

import pytest

from atlas.core.filesystem import create_project
from atlas.core.jsonio import write_json
from atlas.viewer import open_viewer, summarize_viewer_scene


def test_viewer_dry_run_summarizes_expected_artifacts(tmp_path):
    paths = create_project(tmp_path / "scan")
    write_json(paths.reconstruction_dir / "cameras.json", [{"frame_id": "frame_000001"}])
    (paths.reconstruction_dir / "sparse_point_cloud.ply").write_text("ply\n", encoding="utf-8")

    summary = open_viewer(paths.root, dry_run=True)

    assert summary.cameras == 1
    assert summary.sparse_point_cloud == paths.reconstruction_dir / "sparse_point_cloud.ply"
    assert summary.splat_world is None


def test_viewer_requires_viser_for_live_mode(tmp_path):
    if importlib.util.find_spec("viser") is not None:
        pytest.skip("live viewer loop is not exercised in smoke tests")

    paths = create_project(tmp_path / "scan")

    with pytest.raises(RuntimeError, match="viser"):
        open_viewer(paths.root)


def test_summarize_viewer_scene_without_outputs(tmp_path):
    paths = create_project(tmp_path / "scan")
    summary = summarize_viewer_scene(paths.root)

    assert summary.cameras == 0
    assert summary.sparse_point_cloud is None
