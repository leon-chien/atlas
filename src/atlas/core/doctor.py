from __future__ import annotations

import importlib.util
import platform
import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyCheck:
    name: str
    available: bool
    detail: str
    install_hint: str


def check_dependencies() -> list[DependencyCheck]:
    return [
        _binary_check(
            "COLMAP",
            "colmap",
            "macOS: brew install colmap. Linux: use your package manager or conda-forge.",
        ),
        _binary_check(
            "Nerfstudio",
            "ns-train",
            "Install when ready for splats: pip install nerfstudio or follow Nerfstudio CUDA docs.",
        ),
        _binary_check(
            "ffmpeg",
            "ffmpeg",
            "macOS: brew install ffmpeg. Linux: install ffmpeg from your package manager.",
        ),
        _python_check(
            "viser",
            "viser",
            "Install viewer extras: pip install -e '.[viewer]'.",
        ),
        _cuda_check(),
    ]


def _binary_check(name: str, executable: str, install_hint: str) -> DependencyCheck:
    path = shutil.which(executable)
    if path is None:
        return DependencyCheck(name, False, f"{executable} not found on PATH", install_hint)
    return DependencyCheck(name, True, path, install_hint)


def _python_check(name: str, module: str, install_hint: str) -> DependencyCheck:
    if importlib.util.find_spec(module) is None:
        return DependencyCheck(
            name,
            False,
            f"Python module '{module}' is not installed",
            install_hint,
        )
    return DependencyCheck(name, True, f"Python module '{module}' is importable", install_hint)


def _cuda_check() -> DependencyCheck:
    system = platform.system()
    if system == "Darwin":
        return DependencyCheck(
            "CUDA",
            False,
            "CUDA is not available on macOS; use a Linux/NVIDIA workstation or cloud GPU.",
            "Run Gaussian splat training on a CUDA-capable Linux machine.",
        )

    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi is None:
        return DependencyCheck(
            "CUDA",
            False,
            "nvidia-smi not found on PATH",
            "Install NVIDIA drivers/CUDA or use a CUDA cloud instance.",
        )

    try:
        result = subprocess.run(
            [nvidia_smi, "--query-gpu=name", "--format=csv,noheader"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.SubprocessError as exc:
        return DependencyCheck("CUDA", False, f"nvidia-smi failed: {exc}", "Check CUDA drivers.")

    gpu = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "NVIDIA GPU"
    return DependencyCheck("CUDA", True, gpu, "CUDA appears available.")
