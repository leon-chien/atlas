from __future__ import annotations

from pathlib import Path

from atlas.pipeline.stages import not_implemented_stage


def render_trajectory(project_dir: Path, trajectory_path: Path) -> None:
    raise not_implemented_stage(
        "counterfactual rendering",
        "splat-renderer",
        (project_dir / "render" / f"{trajectory_path.stem}_rgb.mp4",),
    )
