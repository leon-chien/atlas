from __future__ import annotations

from pathlib import Path

from atlas.core.filesystem import AtlasProjectPaths
from atlas.pipeline.stages import not_implemented_stage


def run_semantics(project_dir: Path) -> None:
    paths = AtlasProjectPaths(project_dir)
    raise not_implemented_stage(
        "semantics",
        "grounding-dino+sam2+siglip",
        (paths.semantics_dir / "detections.json", paths.semantics_dir / "embeddings.npy"),
    )
