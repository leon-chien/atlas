# Atlas Implementation Plan

This is the canonical project plan record. Update it when the build order or major technical choices change.

## Current State

The repository has a first Python scaffold:

- package metadata and optional dependency groups
- typed Pydantic schemas for pipeline artifacts
- artifact layout helpers
- working `atlas init`, `atlas ingest`, and `atlas status`
- placeholder adapters for reconstruction, depth, semantics, splats, graph, rendering, navigation, and viewer
- lightweight tests for CLI, schemas, project layout, status, and frame sampling

The local development target is Python 3.11+. Heavy model and CUDA dependencies remain optional.

## Fast MVP Path

Build the shortest visible vertical slice:

```text
ingest -> COLMAP poses -> splat adapter -> viser preview -> basic scene graph -> navigation
```

Do not start by moving Hugging Face models into the repository. Model weights stay external and are cached at runtime. Use `HF_HOME=models/huggingface` and `TORCH_HOME=models/torch` only if a project-local cache becomes useful.

### 1. Developer Environment

- Use `uv sync --extra dev` as the preferred install path.
- Keep `python -m pip install -e ".[dev]"` as the fallback.
- Use `make test` for default tests and `make smoke` for fast CLI checks.
- Do not make heavyweight tests run by default.

### 2. COLMAP Reconstruction Adapter

Implement `atlas reconstruct poses --project PROJECT_DIR --backend colmap`.

Inputs:

- `frames/*.jpg`
- `metadata/frames.json`

Outputs:

- `reconstruction/cameras.json`
- `reconstruction/sparse_point_cloud.ply`
- ignored COLMAP workspace under `reconstruction/colmap/`

Implementation direction:

- Prefer the COLMAP CLI first because it is easy to inspect and reproduce.
- Use `feature_extractor -> sequential_matcher -> mapper -> model_converter`.
- Add a dry-run/helper path for testing command construction without requiring COLMAP.
- Export camera poses into Atlas schemas so later stages do not need COLMAP internals.
- Use `atlas doctor` before real runs to check COLMAP, Nerfstudio, ffmpeg, viewer extras, and CUDA availability.

### 3. Splat Adapter

Implement the quickest wrapper around Nerfstudio Splatfacto or `gsplat` that can consume the COLMAP output.

Outputs:

- `splats/atlas_world.ply`
- `splats/splat_manifest.json`

Do not implement a custom splat trainer in the MVP.

Current command target:

```bash
atlas splats train --project runs/desk_scan --backend nerfstudio-splatfacto
```

Use `--dry-run` locally until Nerfstudio and CUDA are available.

### 4. Viewer

Implement `atlas viewer open --project PROJECT_DIR` with `viser`.

First viewer targets:

- camera frustums
- sparse point cloud
- splat file when present
- basic object boxes once graph data exists

Use `--dry-run` to summarize available camera, point cloud, splat, and graph artifacts when `viser` is not installed.

### 5. Semantics And Scene Graph

After reconstruction and viewer are usable, add semantic lifting:

- GroundingDINO for boxes
- SAM 2 for masks
- SigLIP or CLIP for embeddings
- basic object association from label, embedding similarity, and 3D proximity

Scene graph output remains `graph/scene_graph.json`.

### 6. Navigation

Use the existing A* grid planner as the first navigation layer.

Inputs:

- occupancy grid
- object centroids or semantic targets

Outputs:

- planned path
- status/diagnostic artifact

Add PyBullet only after simple occupancy navigation works.

## Non-Goals For Now

- No end-to-end Atlas training.
- No custom Gaussian splat trainer.
- No reinforcement learning agent.
- No large web frontend before there is a useful reconstructed world to view.
- No exhaustive tiny-test expansion.

## Acceptance Strategy

Each milestone should finish with:

- expected artifacts written to the project directory
- `atlas status` reflecting the stage
- one smoke test or dry-run test proving the command boundary works
- docs updated only when the user-facing workflow changes

Current end-to-end instructions live in `docs/mvp-workflow.md`.
