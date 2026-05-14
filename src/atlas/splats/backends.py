from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from atlas.core.filesystem import AtlasProjectPaths
from atlas.core.jsonio import write_json
from atlas.core.schemas import StageManifest, StageStatus


@dataclass(frozen=True)
class NerfstudioSplatCommands:
    train: list[str]
    export: list[str]


def build_nerfstudio_commands(
    project_dir: Path,
    ns_train_bin: str = "ns-train",
    ns_export_bin: str = "ns-export",
) -> NerfstudioSplatCommands:
    paths = AtlasProjectPaths(project_dir)
    output_dir = paths.splats_dir / "nerfstudio"
    export_dir = paths.splats_dir / "export"
    planned_config = output_dir / "atlas_world" / "splatfacto" / "latest" / "config.yml"

    return NerfstudioSplatCommands(
        train=[
            ns_train_bin,
            "splatfacto",
            "--data",
            str(paths.root),
            "--output-dir",
            str(output_dir),
            "--experiment-name",
            "atlas_world",
            "--vis",
            "viewer",
        ],
        export=[
            ns_export_bin,
            "gaussian-splat",
            "--load-config",
            str(planned_config),
            "--output-dir",
            str(export_dir),
        ],
    )


def run_splat_reconstruction(
    project_dir: Path,
    backend: str = "nerfstudio-splatfacto",
    dry_run: bool = False,
    ns_train_bin: str = "ns-train",
    ns_export_bin: str = "ns-export",
) -> NerfstudioSplatCommands:
    if backend != "nerfstudio-splatfacto":
        raise ValueError(f"Unsupported splat backend: {backend}")

    paths = AtlasProjectPaths(project_dir)
    commands = build_nerfstudio_commands(
        project_dir,
        ns_train_bin=ns_train_bin,
        ns_export_bin=ns_export_bin,
    )
    if dry_run:
        return commands

    _validate_splat_inputs(paths)
    _require_binary(ns_train_bin, "Nerfstudio training binary")
    _require_binary(ns_export_bin, "Nerfstudio export binary")

    paths.splats_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(commands.train, check=True)

    config = _latest_nerfstudio_config(paths.splats_dir / "nerfstudio")
    export_command = [*commands.export[:3], str(config), *commands.export[4:]]
    subprocess.run(export_command, check=True)

    exported = _latest_exported_ply(paths.splats_dir / "export")
    shutil.copy2(exported, paths.splats_dir / "atlas_world.ply")
    write_json(
        paths.splats_dir / "splat_manifest.json",
        StageManifest(
            stage_name="splats",
            backend=backend,
            inputs=[
                str(paths.frames_dir.relative_to(paths.root)),
                str((paths.reconstruction_dir / "colmap").relative_to(paths.root)),
            ],
            outputs=[
                str((paths.splats_dir / "atlas_world.ply").relative_to(paths.root)),
                str((paths.splats_dir / "splat_manifest.json").relative_to(paths.root)),
            ],
            status=StageStatus.complete,
            message=f"Exported Nerfstudio splat from {config}.",
        ).model_dump(mode="json"),
    )
    return commands


def _validate_splat_inputs(paths: AtlasProjectPaths) -> None:
    if not any(paths.frames_dir.glob("*.jpg")):
        raise FileNotFoundError(f"No ingested JPG frames found in {paths.frames_dir}")
    if not (paths.reconstruction_dir / "colmap" / "sparse" / "0").exists():
        raise FileNotFoundError(
            "Missing COLMAP sparse model. "
            "Run `atlas reconstruct poses --project PROJECT_DIR` first."
        )


def _require_binary(binary: str, label: str) -> None:
    if shutil.which(binary) is None:
        raise RuntimeError(
            f"{label} '{binary}' was not found. Run `atlas doctor` for install hints."
        )


def _latest_nerfstudio_config(output_dir: Path) -> Path:
    configs = sorted(output_dir.glob("**/config.yml"), key=lambda path: path.stat().st_mtime)
    if not configs:
        raise FileNotFoundError(f"Nerfstudio did not write a config.yml under {output_dir}")
    return configs[-1]


def _latest_exported_ply(export_dir: Path) -> Path:
    point_clouds = sorted(export_dir.glob("**/*.ply"), key=lambda path: path.stat().st_mtime)
    if not point_clouds:
        raise FileNotFoundError(f"Nerfstudio export did not write a .ply under {export_dir}")
    return point_clouds[-1]
