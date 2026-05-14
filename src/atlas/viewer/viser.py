from __future__ import annotations

from pathlib import Path

from atlas.core.filesystem import AtlasProjectPaths
from atlas.pipeline.stages import not_implemented_stage


def open_viewer(project_dir: Path) -> None:
    paths = AtlasProjectPaths(project_dir)
    raise not_implemented_stage(
        "viewer",
        "viser",
        (paths.splats_dir / "atlas_world.ply", paths.graph_dir / "scene_graph.json"),
    )
