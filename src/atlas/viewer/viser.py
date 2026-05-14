from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path

from atlas.core.filesystem import AtlasProjectPaths
from atlas.core.jsonio import read_json


@dataclass(frozen=True)
class ViewerSceneSummary:
    cameras: int
    sparse_point_cloud: Path | None
    splat_world: Path | None
    scene_graph: Path | None


def summarize_viewer_scene(project_dir: Path) -> ViewerSceneSummary:
    paths = AtlasProjectPaths(project_dir)
    camera_count = 0
    cameras_path = paths.reconstruction_dir / "cameras.json"
    if cameras_path.exists():
        cameras = read_json(cameras_path)
        if isinstance(cameras, list):
            camera_count = len(cameras)

    sparse_point_cloud = paths.reconstruction_dir / "sparse_point_cloud.ply"
    splat_world = paths.splats_dir / "atlas_world.ply"
    scene_graph = paths.graph_dir / "scene_graph.json"

    return ViewerSceneSummary(
        cameras=camera_count,
        sparse_point_cloud=sparse_point_cloud if sparse_point_cloud.exists() else None,
        splat_world=splat_world if splat_world.exists() else None,
        scene_graph=scene_graph if scene_graph.exists() else None,
    )


def open_viewer(project_dir: Path, dry_run: bool = False) -> ViewerSceneSummary:
    summary = summarize_viewer_scene(project_dir)
    if dry_run:
        return summary

    if importlib.util.find_spec("viser") is None:
        raise RuntimeError(
            "Python module 'viser' is not installed. Run `atlas doctor` for install hints."
        )

    import viser  # type: ignore[import-not-found]

    server = viser.ViserServer()
    _populate_viser_scene(server, summary)
    print("Atlas viewer running. Press Ctrl+C to stop.")
    try:
        while True:
            import time

            time.sleep(1.0)
    except KeyboardInterrupt:
        return summary


def _populate_viser_scene(server: object, summary: ViewerSceneSummary) -> None:
    scene = server.scene
    if summary.sparse_point_cloud is not None:
        scene.add_label(
            "/atlas/sparse_point_cloud",
            f"Sparse point cloud: {summary.sparse_point_cloud}",
            position=(0.0, 0.0, 0.0),
        )
    if summary.splat_world is not None:
        scene.add_label(
            "/atlas/splat_world",
            f"Gaussian splat: {summary.splat_world}",
            position=(0.0, 0.25, 0.0),
        )
    scene.add_label(
        "/atlas/cameras",
        f"Camera poses: {summary.cameras}",
        position=(0.0, 0.5, 0.0),
    )
