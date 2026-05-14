from __future__ import annotations

from pathlib import Path

from atlas.core.filesystem import AtlasProjectPaths
from atlas.pipeline.stages import not_implemented_stage


def run_splat_reconstruction(project_dir: Path, backend: str = "nerfstudio-splatfacto") -> None:
    paths = AtlasProjectPaths(project_dir)
    raise not_implemented_stage(
        "gaussian splat reconstruction",
        backend,
        (paths.splats_dir / "atlas_world.ply", paths.splats_dir / "splat_manifest.json"),
    )
