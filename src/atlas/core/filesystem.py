from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from atlas.core.schemas import AtlasProjectConfig


@dataclass(frozen=True)
class AtlasProjectPaths:
    root: Path

    @property
    def config(self) -> Path:
        return self.root / "atlas.yaml"

    @property
    def input_dir(self) -> Path:
        return self.root / "input"

    @property
    def frames_dir(self) -> Path:
        return self.root / "frames"

    @property
    def metadata_dir(self) -> Path:
        return self.root / "metadata"

    @property
    def reconstruction_dir(self) -> Path:
        return self.root / "reconstruction"

    @property
    def depth_dir(self) -> Path:
        return self.root / "depth"

    @property
    def semantics_dir(self) -> Path:
        return self.root / "semantics"

    @property
    def masks_dir(self) -> Path:
        return self.semantics_dir / "masks"

    @property
    def splats_dir(self) -> Path:
        return self.root / "splats"

    @property
    def graph_dir(self) -> Path:
        return self.root / "graph"

    @property
    def navigation_dir(self) -> Path:
        return self.root / "navigation"

    @property
    def video_metadata(self) -> Path:
        return self.metadata_dir / "video.json"

    @property
    def frame_metadata(self) -> Path:
        return self.metadata_dir / "frames.json"

    def ensure_directories(self) -> None:
        for directory in [
            self.root,
            self.input_dir,
            self.frames_dir,
            self.metadata_dir,
            self.reconstruction_dir,
            self.depth_dir,
            self.semantics_dir,
            self.masks_dir,
            self.splats_dir,
            self.graph_dir,
            self.navigation_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


def create_project(project_dir: Path, project_name: str | None = None) -> AtlasProjectPaths:
    paths = AtlasProjectPaths(project_dir)
    paths.ensure_directories()

    if not paths.config.exists():
        config = AtlasProjectConfig(project_name=project_name or project_dir.name)
        config_yaml = yaml.safe_dump(config.model_dump(), sort_keys=False)
        paths.config.write_text(config_yaml, encoding="utf-8")

    return paths


def load_project_config(project_dir: Path) -> AtlasProjectConfig:
    config_path = AtlasProjectPaths(project_dir).config
    raw: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return AtlasProjectConfig.model_validate(raw)
