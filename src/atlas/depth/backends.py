from __future__ import annotations

from pathlib import Path

from atlas.core.filesystem import AtlasProjectPaths
from atlas.pipeline.stages import not_implemented_stage


def run_depth(project_dir: Path, backend: str = "depth-anything-v2") -> None:
    paths = AtlasProjectPaths(project_dir)
    raise not_implemented_stage("depth", backend, (paths.depth_dir / "depth_manifest.json",))
