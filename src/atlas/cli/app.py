from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from atlas.core.doctor import check_dependencies
from atlas.core.filesystem import create_project, load_project_config
from atlas.core.status import project_status
from atlas.depth import run_depth
from atlas.graph import build_scene_graph
from atlas.reconstruction import run_colmap_poses
from atlas.semantics import run_semantics
from atlas.splats import run_splat_reconstruction
from atlas.video import ingest_video
from atlas.viewer import open_viewer

app = typer.Typer(help="Atlas semantic world-modeling toolkit.")
reconstruct_app = typer.Typer(help="Pose and geometry reconstruction commands.")
depth_app = typer.Typer(help="Dense depth estimation commands.")
semantics_app = typer.Typer(help="Object detection, segmentation, and embedding commands.")
graph_app = typer.Typer(help="Persistent scene graph commands.")
splats_app = typer.Typer(help="Gaussian splat reconstruction commands.")
viewer_app = typer.Typer(help="Interactive preview commands.")

app.add_typer(reconstruct_app, name="reconstruct")
app.add_typer(depth_app, name="depth")
app.add_typer(semantics_app, name="semantics")
app.add_typer(graph_app, name="graph")
app.add_typer(splats_app, name="splats")
app.add_typer(viewer_app, name="viewer")


@app.command("doctor")
def doctor() -> None:
    """Check local tools needed for the Atlas MVP pipeline."""
    for check in check_dependencies():
        marker = "ok" if check.available else "missing"
        typer.echo(f"{check.name}: {marker} - {check.detail}")
        if not check.available:
            typer.echo(f"  install: {check.install_hint}")


@app.command("init")
def init_project(
    project_dir: Path,
    name: Annotated[str | None, typer.Option("--name")] = None,
) -> None:
    """Create an Atlas project directory and artifact layout."""
    paths = create_project(project_dir, project_name=name)
    typer.echo(f"Initialized Atlas project at {paths.root}")


@app.command("ingest")
def ingest(
    video_path: Path,
    project: Annotated[Path, typer.Option("--project", "-p")],
    sample_fps: Annotated[float, typer.Option("--sample-fps", min=0.01)] = 2.0,
    max_frames: Annotated[int, typer.Option("--max-frames", min=1)] = 180,
) -> None:
    """Extract selected frames and write video/frame metadata."""
    count = ingest_video(video_path, project, sample_fps=sample_fps, max_frames=max_frames)
    typer.echo(f"Ingested {count} frames into {project}")


@app.command("status")
def status(project_dir: Path) -> None:
    """Show which Atlas project artifacts currently exist."""
    config = load_project_config(project_dir)
    typer.echo(f"Project: {config.project_name}")
    for report in project_status(project_dir):
        marker = "complete" if report.complete else "missing"
        typer.echo(f"{report.stage}: {marker}")


@reconstruct_app.command("poses")
def reconstruct_poses(
    project: Annotated[Path, typer.Option("--project", "-p")],
    backend: Annotated[str, typer.Option("--backend")] = "colmap",
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
    colmap_bin: Annotated[str, typer.Option("--colmap-bin")] = "colmap",
    matcher: Annotated[str, typer.Option("--matcher")] = "sequential",
) -> None:
    """Estimate camera poses and sparse geometry."""
    commands = run_colmap_poses(
        project,
        backend=backend,
        dry_run=dry_run,
        colmap_bin=colmap_bin,
        matcher=matcher,
    )
    if dry_run:
        for command in commands:
            typer.echo(" ".join(command))
    else:
        typer.echo(f"Reconstructed COLMAP poses into {project / 'reconstruction'}")


@depth_app.command("run")
def depth_run(
    project: Annotated[Path, typer.Option("--project", "-p")],
    backend: Annotated[str, typer.Option("--backend")] = "depth-anything-v2",
) -> None:
    """Estimate dense monocular depth maps."""
    run_depth(project, backend=backend)


@semantics_app.command("run")
def semantics_run(project: Annotated[Path, typer.Option("--project", "-p")]) -> None:
    """Detect, segment, and embed frame-level objects."""
    run_semantics(project)


@graph_app.command("build")
def graph_build(project: Annotated[Path, typer.Option("--project", "-p")]) -> None:
    """Lift semantic observations into a persistent scene graph."""
    build_scene_graph(project)


@splats_app.command("train")
def splats_train(
    project: Annotated[Path, typer.Option("--project", "-p")],
    backend: Annotated[str, typer.Option("--backend")] = "nerfstudio-splatfacto",
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
    ns_train_bin: Annotated[str, typer.Option("--ns-train-bin")] = "ns-train",
    ns_export_bin: Annotated[str, typer.Option("--ns-export-bin")] = "ns-export",
) -> None:
    """Train/export Gaussian splats using an external trainer."""
    commands = run_splat_reconstruction(
        project,
        backend=backend,
        dry_run=dry_run,
        ns_train_bin=ns_train_bin,
        ns_export_bin=ns_export_bin,
    )
    if dry_run:
        typer.echo(" ".join(commands.train))
        typer.echo(" ".join(commands.export))
    else:
        typer.echo(f"Exported splat world into {project / 'splats'}")


@viewer_app.command("open")
def viewer_open(
    project: Annotated[Path, typer.Option("--project", "-p")],
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    """Open an interactive Atlas project viewer."""
    summary = open_viewer(project, dry_run=dry_run)
    if dry_run:
        typer.echo(f"cameras: {summary.cameras}")
        typer.echo(f"sparse_point_cloud: {summary.sparse_point_cloud or 'missing'}")
        typer.echo(f"splat_world: {summary.splat_world or 'missing'}")
        typer.echo(f"scene_graph: {summary.scene_graph or 'missing'}")
