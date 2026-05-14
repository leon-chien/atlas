from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StageStatus(StrEnum):
    """Lifecycle state for an Atlas pipeline stage."""

    pending = "pending"
    complete = "complete"
    failed = "failed"
    skipped = "skipped"


class AtlasModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AtlasProjectConfig(AtlasModel):
    project_name: str = "atlas_project"
    coordinate_convention: str = "right_handed_y_up"
    backends: dict[str, str] = Field(
        default_factory=lambda: {
            "pose": "colmap",
            "depth": "depth-anything-v2",
            "semantics_detector": "grounding-dino",
            "semantics_segmenter": "sam2",
            "embedding": "siglip",
            "splats": "nerfstudio-splatfacto",
            "viewer": "viser",
            "navigation": "astar-grid",
        }
    )
    stage_settings: dict[str, Any] = Field(default_factory=dict)


class FrameRecord(AtlasModel):
    frame_id: str
    timestamp_s: float = Field(ge=0)
    path: str
    blur_score: float = Field(ge=0)
    width: int = Field(gt=0)
    height: int = Field(gt=0)


class VideoMetadata(AtlasModel):
    source_video: str
    frame_count: int = Field(ge=0)
    fps: float = Field(ge=0)
    duration_s: float = Field(ge=0)
    width: int = Field(ge=0)
    height: int = Field(ge=0)


class CameraIntrinsics(AtlasModel):
    fx: float
    fy: float
    cx: float
    cy: float
    width: int = Field(gt=0)
    height: int = Field(gt=0)


class CameraPose(AtlasModel):
    frame_id: str
    intrinsics: CameraIntrinsics
    world_to_camera: list[list[float]] = Field(min_length=4, max_length=4)
    confidence: float = Field(ge=0, le=1)


class ObjectObservation(AtlasModel):
    frame_id: str
    label: str
    bbox_xyxy: list[float] = Field(min_length=4, max_length=4)
    mask_path: str | None = None
    score: float = Field(ge=0, le=1)
    embedding_id: str | None = None


class ObjectNode(AtlasModel):
    object_id: str
    label: str
    centroid_3d: list[float] = Field(min_length=3, max_length=3)
    bbox_3d: list[float] = Field(min_length=6, max_length=6)
    semantic_embedding_id: str | None = None
    collision_mesh: str | None = None
    visible_frames: list[str] = Field(default_factory=list)
    first_seen: str | None = None
    last_seen: str | None = None


class RelationEdge(AtlasModel):
    source: str
    target: str
    relation: Literal["on_top_of", "near", "left_of", "blocking", "reachable", "supports"]
    confidence: float = Field(ge=0, le=1)


class SceneGraph(AtlasModel):
    graph_id: str
    objects: list[ObjectNode] = Field(default_factory=list)
    relations: list[RelationEdge] = Field(default_factory=list)


class Trajectory(AtlasModel):
    trajectory_id: str
    poses: list[CameraPose] = Field(default_factory=list)
    waypoints: list[list[float]] = Field(default_factory=list)


class StageManifest(AtlasModel):
    stage_name: str
    backend: str
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    status: StageStatus = StageStatus.pending
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    message: str | None = None
