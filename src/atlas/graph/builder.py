from __future__ import annotations

from pathlib import Path

from atlas.core.filesystem import AtlasProjectPaths
from atlas.pipeline.stages import not_implemented_stage


def build_scene_graph(project_dir: Path) -> None:
    paths = AtlasProjectPaths(project_dir)
    raise not_implemented_stage(
        "scene graph",
        "semantic-lifting",
        (paths.graph_dir / "scene_graph.json",),
    )
