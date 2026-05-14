from __future__ import annotations

from atlas.core.filesystem import create_project
from atlas.core.status import project_status


def test_create_project_writes_expected_layout(tmp_path):
    paths = create_project(tmp_path / "scan", project_name="scan")

    assert paths.config.exists()
    assert paths.input_dir.is_dir()
    assert paths.frames_dir.is_dir()
    assert paths.metadata_dir.is_dir()
    assert paths.reconstruction_dir.is_dir()
    assert paths.depth_dir.is_dir()
    assert paths.semantics_dir.is_dir()
    assert paths.masks_dir.is_dir()
    assert paths.splats_dir.is_dir()
    assert paths.graph_dir.is_dir()
    assert paths.navigation_dir.is_dir()


def test_project_status_tracks_partial_outputs(tmp_path):
    paths = create_project(tmp_path / "scan")
    reports = {report.stage: report for report in project_status(paths.root)}

    assert reports["initialized"].complete is True
    assert reports["ingested"].complete is False

    paths.video_metadata.write_text("{}", encoding="utf-8")
    paths.frame_metadata.write_text("[]", encoding="utf-8")
    (paths.frames_dir / "frame_000001.jpg").write_bytes(b"not-a-real-image")

    reports = {report.stage: report for report in project_status(paths.root)}
    assert reports["ingested"].complete is True
    assert reports["reconstruction"].complete is False

    (paths.reconstruction_dir / "cameras.json").write_text("[]", encoding="utf-8")
    (paths.reconstruction_dir / "sparse_point_cloud.ply").write_text("ply\n", encoding="utf-8")

    reports = {report.stage: report for report in project_status(paths.root)}
    assert reports["reconstruction"].complete is True
