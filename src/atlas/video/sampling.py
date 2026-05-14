from __future__ import annotations

import math

import cv2
import numpy as np


def blur_score(image: np.ndarray) -> float:
    """Return a simple sharpness score using variance of the Laplacian."""
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def select_frame_indices(
    total_frames: int,
    native_fps: float,
    sample_fps: float,
    max_frames: int,
) -> list[int]:
    if total_frames <= 0 or max_frames <= 0:
        return []
    if native_fps <= 0 or sample_fps <= 0 or sample_fps >= native_fps:
        indices = list(range(total_frames))
    else:
        stride = max(1, int(round(native_fps / sample_fps)))
        indices = list(range(0, total_frames, stride))

    if len(indices) <= max_frames:
        return indices

    step = len(indices) / max_frames
    sampled = [indices[math.floor(i * step)] for i in range(max_frames)]
    return sorted(set(sampled))
