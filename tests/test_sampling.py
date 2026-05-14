from __future__ import annotations

import numpy as np

from atlas.video.sampling import blur_score, select_frame_indices


def test_select_frame_indices_respects_sampling_and_limit():
    indices = select_frame_indices(total_frames=100, native_fps=10, sample_fps=2, max_frames=8)

    assert indices == [0, 10, 25, 35, 50, 60, 75, 85]


def test_blur_score_is_higher_for_sharp_edges():
    sharp = np.zeros((32, 32), dtype=np.uint8)
    sharp[:, 16:] = 255
    flat = np.zeros((32, 32), dtype=np.uint8)

    assert blur_score(sharp) > blur_score(flat)
