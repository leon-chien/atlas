from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from atlas.core.filesystem import AtlasProjectPaths


@dataclass(frozen=True)
class StageStatusReport:
    stage: str
    complete: bool
    expected_outputs: tuple[Path, ...]


def project_status(project_dir: Path) -> list[StageStatusReport]:
    paths = AtlasProjectPaths(project_dir)
    stage_outputs = {
        "initialized": (paths.config,),
        "ingested": (paths.video_metadata, paths.frame_metadata),
        "reconstruction": (
            paths.reconstruction_dir / "cameras.json",
            paths.reconstruction_dir / "sparse_point_cloud.ply",
        ),
        "depth": (paths.depth_dir / "depth_manifest.json",),
        "semantics": (paths.semantics_dir / "detections.json",),
        "splats": (paths.splats_dir / "atlas_world.ply", paths.splats_dir / "splat_manifest.json"),
        "graph": (paths.graph_dir / "scene_graph.json",),
        "navigation": (paths.navigation_dir / "occupancy_grid.npz",),
    }

    reports: list[StageStatusReport] = []
    for stage, outputs in stage_outputs.items():
        complete = all(output.exists() for output in outputs)
        if stage == "ingested":
            complete = complete and any(paths.frames_dir.glob("*.jpg"))
        reports.append(StageStatusReport(stage=stage, complete=complete, expected_outputs=outputs))
    return reports
