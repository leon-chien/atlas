from __future__ import annotations

import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from atlas.core.filesystem import AtlasProjectPaths
from atlas.core.jsonio import write_json
from atlas.core.schemas import CameraIntrinsics, CameraPose, StageManifest, StageStatus


@dataclass(frozen=True)
class ColmapWorkspace:
    database: Path
    sparse: Path
    sparse_txt: Path
    point_cloud: Path
    cameras: Path
    manifest: Path


def colmap_workspace(project_dir: Path) -> ColmapWorkspace:
    paths = AtlasProjectPaths(project_dir)
    root = paths.reconstruction_dir / "colmap"
    return ColmapWorkspace(
        database=root / "database.db",
        sparse=root / "sparse",
        sparse_txt=root / "sparse_txt",
        point_cloud=paths.reconstruction_dir / "sparse_point_cloud.ply",
        cameras=paths.reconstruction_dir / "cameras.json",
        manifest=paths.reconstruction_dir / "colmap_manifest.json",
    )


def build_colmap_commands(
    project_dir: Path,
    colmap_bin: str = "colmap",
    matcher: str = "sequential",
) -> list[list[str]]:
    paths = AtlasProjectPaths(project_dir)
    workspace = colmap_workspace(project_dir)
    matcher_command = _matcher_command(matcher)
    return [
        [
            colmap_bin,
            "feature_extractor",
            "--database_path",
            str(workspace.database),
            "--image_path",
            str(paths.frames_dir),
            "--ImageReader.single_camera",
            "1",
        ],
        [
            colmap_bin,
            matcher_command,
            "--database_path",
            str(workspace.database),
        ],
        [
            colmap_bin,
            "mapper",
            "--database_path",
            str(workspace.database),
            "--image_path",
            str(paths.frames_dir),
            "--output_path",
            str(workspace.sparse),
        ],
        [
            colmap_bin,
            "model_converter",
            "--input_path",
            str(workspace.sparse / "0"),
            "--output_path",
            str(workspace.sparse_txt),
            "--output_type",
            "TXT",
        ],
        [
            colmap_bin,
            "model_converter",
            "--input_path",
            str(workspace.sparse / "0"),
            "--output_path",
            str(workspace.point_cloud),
            "--output_type",
            "PLY",
        ],
    ]


def run_colmap_poses(
    project_dir: Path,
    backend: str = "colmap",
    dry_run: bool = False,
    colmap_bin: str = "colmap",
    matcher: str = "sequential",
) -> list[list[str]]:
    if backend != "colmap":
        raise ValueError(f"Unsupported reconstruction backend: {backend}")

    paths = AtlasProjectPaths(project_dir)
    workspace = colmap_workspace(project_dir)
    commands = build_colmap_commands(project_dir, colmap_bin=colmap_bin, matcher=matcher)

    if dry_run:
        return commands

    if not paths.frames_dir.exists() or not any(paths.frames_dir.glob("*.jpg")):
        raise FileNotFoundError(f"No ingested JPG frames found in {paths.frames_dir}")
    if shutil.which(colmap_bin) is None:
        raise RuntimeError(
            f"COLMAP binary '{colmap_bin}' was not found. Install COLMAP or pass --colmap-bin."
        )

    workspace.sparse.mkdir(parents=True, exist_ok=True)
    workspace.sparse_txt.mkdir(parents=True, exist_ok=True)
    paths.reconstruction_dir.mkdir(parents=True, exist_ok=True)

    for command in commands[:3]:
        subprocess.run(command, check=True)

    sparse_model = select_largest_sparse_model(workspace.sparse)
    converter_commands = _converter_commands(colmap_bin, sparse_model, workspace)
    for command in converter_commands:
        subprocess.run(command, check=True)

    poses = parse_colmap_cameras(workspace.sparse_txt)
    write_json(workspace.cameras, [pose.model_dump(mode="json") for pose in poses])
    write_json(
        workspace.manifest,
        StageManifest(
            stage_name="reconstruction",
            backend=backend,
            inputs=[
                str(paths.frames_dir.relative_to(paths.root)),
                str(paths.frame_metadata.relative_to(paths.root)),
            ],
            outputs=[
                str(workspace.cameras.relative_to(paths.root)),
                str(workspace.point_cloud.relative_to(paths.root)),
            ],
            status=StageStatus.complete,
            message=(
                f"Reconstructed {len(poses)} camera poses with COLMAP "
                f"using {matcher} matching and sparse model {sparse_model.name}."
            ),
        ).model_dump(mode="json"),
    )
    return [*commands[:3], *converter_commands]


def select_largest_sparse_model(sparse_dir: Path) -> Path:
    candidates = [path for path in sparse_dir.iterdir() if path.is_dir()]
    scored: list[tuple[int, Path]] = []
    for candidate in candidates:
        images = candidate / "images.bin"
        points = candidate / "points3D.bin"
        if images.exists() and points.exists():
            scored.append((images.stat().st_size + points.stat().st_size, candidate))

    if not scored:
        raise RuntimeError(f"COLMAP did not produce a sparse model under {sparse_dir}")

    return max(scored, key=lambda item: item[0])[1]


def parse_colmap_cameras(model_txt_dir: Path) -> list[CameraPose]:
    cameras = _read_cameras(model_txt_dir / "cameras.txt")
    poses: list[CameraPose] = []

    images_path = model_txt_dir / "images.txt"
    if not images_path.exists():
        raise FileNotFoundError(f"Missing COLMAP images.txt: {images_path}")

    with images_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 10:
                continue

            qw, qx, qy, qz = (float(value) for value in parts[1:5])
            tx, ty, tz = (float(value) for value in parts[5:8])
            camera_id = int(parts[8])
            image_name = parts[9]
            intrinsics = cameras[camera_id]

            poses.append(
                CameraPose(
                    frame_id=Path(image_name).stem,
                    intrinsics=intrinsics,
                    world_to_camera=_world_to_camera_matrix(qw, qx, qy, qz, tx, ty, tz),
                    confidence=1.0,
                )
            )

            next(handle, None)

    return poses


def _read_cameras(cameras_path: Path) -> dict[int, CameraIntrinsics]:
    if not cameras_path.exists():
        raise FileNotFoundError(f"Missing COLMAP cameras.txt: {cameras_path}")

    cameras: dict[int, CameraIntrinsics] = {}
    with cameras_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            camera_id = int(parts[0])
            model = parts[1]
            width = int(parts[2])
            height = int(parts[3])
            params = [float(value) for value in parts[4:]]
            fx, fy, cx, cy = _intrinsics_from_colmap_params(model, width, height, params)
            cameras[camera_id] = CameraIntrinsics(
                fx=fx,
                fy=fy,
                cx=cx,
                cy=cy,
                width=width,
                height=height,
            )
    return cameras


def _matcher_command(matcher: str) -> str:
    matchers = {
        "sequential": "sequential_matcher",
        "exhaustive": "exhaustive_matcher",
    }
    if matcher not in matchers:
        raise ValueError(f"Unsupported COLMAP matcher: {matcher}")
    return matchers[matcher]


def _converter_commands(
    colmap_bin: str,
    sparse_model: Path,
    workspace: ColmapWorkspace,
) -> list[list[str]]:
    return [
        [
            colmap_bin,
            "model_converter",
            "--input_path",
            str(sparse_model),
            "--output_path",
            str(workspace.sparse_txt),
            "--output_type",
            "TXT",
        ],
        [
            colmap_bin,
            "model_converter",
            "--input_path",
            str(sparse_model),
            "--output_path",
            str(workspace.point_cloud),
            "--output_type",
            "PLY",
        ],
    ]


def _intrinsics_from_colmap_params(
    model: str,
    width: int,
    height: int,
    params: list[float],
) -> tuple[float, float, float, float]:
    if model in {"SIMPLE_PINHOLE", "SIMPLE_RADIAL", "RADIAL"}:
        focal, cx, cy = params[:3]
        return focal, focal, cx, cy
    if model in {"PINHOLE", "OPENCV", "OPENCV_FISHEYE", "FULL_OPENCV"}:
        fx, fy, cx, cy = params[:4]
        return fx, fy, cx, cy
    if model == "SIMPLE_RADIAL_FISHEYE":
        focal, cx, cy = params[:3]
        return focal, focal, cx, cy

    focal = max(width, height)
    return float(focal), float(focal), width / 2.0, height / 2.0


def _world_to_camera_matrix(
    qw: float,
    qx: float,
    qy: float,
    qz: float,
    tx: float,
    ty: float,
    tz: float,
) -> list[list[float]]:
    norm = math.sqrt(qw * qw + qx * qx + qy * qy + qz * qz)
    if norm == 0:
        raise ValueError("COLMAP quaternion has zero norm")
    qw, qx, qy, qz = qw / norm, qx / norm, qy / norm, qz / norm

    return [
        [
            1 - 2 * qy * qy - 2 * qz * qz,
            2 * qx * qy - 2 * qz * qw,
            2 * qx * qz + 2 * qy * qw,
            tx,
        ],
        [
            2 * qx * qy + 2 * qz * qw,
            1 - 2 * qx * qx - 2 * qz * qz,
            2 * qy * qz - 2 * qx * qw,
            ty,
        ],
        [
            2 * qx * qz - 2 * qy * qw,
            2 * qy * qz + 2 * qx * qw,
            1 - 2 * qx * qx - 2 * qy * qy,
            tz,
        ],
        [0.0, 0.0, 0.0, 1.0],
    ]
