from __future__ import annotations

from atlas.reconstruction.colmap import build_colmap_commands, parse_colmap_cameras


def test_colmap_command_builder_uses_sequential_video_flow(tmp_path):
    commands = build_colmap_commands(tmp_path / "scan")
    stages = [command[1] for command in commands]

    assert stages == [
        "feature_extractor",
        "sequential_matcher",
        "mapper",
        "model_converter",
        "model_converter",
    ]
    assert "--ImageReader.single_camera" in commands[0]


def test_parse_colmap_text_model_exports_camera_pose(tmp_path):
    model = tmp_path / "sparse_txt"
    model.mkdir()
    (model / "cameras.txt").write_text(
        "# Camera list\n"
        "1 PINHOLE 640 480 500 510 320 240\n",
        encoding="utf-8",
    )
    (model / "images.txt").write_text(
        "# Image list\n"
        "1 1 0 0 0 0.1 0.2 0.3 1 frame_000001.jpg\n"
        "\n",
        encoding="utf-8",
    )

    poses = parse_colmap_cameras(model)

    assert len(poses) == 1
    assert poses[0].frame_id == "frame_000001"
    assert poses[0].intrinsics.fx == 500
    assert poses[0].intrinsics.fy == 510
    assert poses[0].world_to_camera[0][3] == 0.1
