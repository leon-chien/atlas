from __future__ import annotations

import shutil
from pathlib import Path

import cv2

from atlas.core.filesystem import create_project
from atlas.core.jsonio import write_json, write_model
from atlas.core.schemas import FrameRecord, VideoMetadata
from atlas.video.sampling import blur_score, select_frame_indices


def ingest_video(
    video_path: Path,
    project_dir: Path,
    sample_fps: float = 2.0,
    max_frames: int = 180,
) -> int:
    if not video_path.exists():
        raise FileNotFoundError(f"Video does not exist: {video_path}")

    paths = create_project(project_dir)
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    native_fps = float(capture.get(cv2.CAP_PROP_FPS) or 0)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration_s = total_frames / native_fps if native_fps > 0 else 0.0
    selected = set(select_frame_indices(total_frames, native_fps, sample_fps, max_frames))

    copied_video = paths.input_dir / f"source_video{video_path.suffix.lower() or '.mp4'}"
    if video_path.resolve() != copied_video.resolve():
        shutil.copy2(video_path, copied_video)

    records: list[FrameRecord] = []
    frame_number = 0
    written_number = 0

    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if frame_number in selected:
            frame_id = f"frame_{written_number + 1:06d}"
            frame_path = paths.frames_dir / f"{frame_id}.jpg"
            cv2.imwrite(str(frame_path), frame)
            records.append(
                FrameRecord(
                    frame_id=frame_id,
                    timestamp_s=frame_number / native_fps if native_fps > 0 else 0.0,
                    path=str(frame_path.relative_to(paths.root)),
                    blur_score=blur_score(frame),
                    width=int(frame.shape[1]),
                    height=int(frame.shape[0]),
                )
            )
            written_number += 1
        frame_number += 1

    capture.release()

    write_model(
        paths.video_metadata,
        VideoMetadata(
            source_video=str(copied_video.relative_to(paths.root)),
            frame_count=total_frames,
            fps=native_fps,
            duration_s=duration_s,
            width=width,
            height=height,
        ),
    )
    write_json(paths.frame_metadata, [record.model_dump(mode="json") for record in records])
    return len(records)
