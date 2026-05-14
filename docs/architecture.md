# Atlas Architecture

Atlas is organized as an artifact-oriented pipeline. Each stage reads explicit files from an
Atlas project directory and writes explicit outputs for the next stage. This keeps the early
repo useful on a laptop while allowing CUDA-heavy jobs to move to a workstation or cloud runner.

## MVP Flow

1. `atlas init PROJECT_DIR`
2. `atlas ingest VIDEO_PATH --project PROJECT_DIR`
3. `atlas reconstruct poses --project PROJECT_DIR --backend colmap`
4. `atlas depth run --project PROJECT_DIR --backend depth-anything-v2`
5. `atlas semantics run --project PROJECT_DIR`
6. `atlas graph build --project PROJECT_DIR`
7. `atlas viewer open --project PROJECT_DIR`

Only initialization, ingest, and status are implemented in v0. The other commands are wired as
adapter boundaries with expected output paths so the repo can grow without reshaping the CLI.

## Project Layout

```text
atlas_project/
  atlas.yaml
  input/source_video.mp4
  frames/frame_000001.jpg
  metadata/video.json
  metadata/frames.json
  reconstruction/cameras.json
  reconstruction/sparse_point_cloud.ply
  depth/depth_manifest.json
  semantics/detections.json
  semantics/masks/
  semantics/embeddings.npy
  splats/atlas_world.ply
  splats/splat_manifest.json
  graph/scene_graph.json
  navigation/occupancy_grid.npz
```

## Backend Choices

- Pose and sparse geometry: COLMAP first, MASt3R/DUSt3R later.
- Splats: Nerfstudio Splatfacto or `gsplat`; no custom trainer in v0.
- Depth: Depth Anything V2, optional and manifest-driven.
- Semantics: GroundingDINO boxes, SAM 2 masks, SigLIP/CLIP embeddings.
- Viewer: `viser` first.
- Navigation: occupancy grid plus A* first, PyBullet later.
