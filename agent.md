# Atlas Agent Notes

Use this file as persistent context when working on Atlas. The project should move quickly toward a visible, usable MVP instead of expanding into a broad research codebase too early.

## Mission

Atlas learns an interactive semantic simulation of a real environment from ordinary monocular video. The MVP should make this loop work first:

```text
video -> frames -> camera poses -> gaussian splat world -> viewer
```

After that loop is visible, add semantic objects, scene graph memory, and navigation.

## Current Architecture

Atlas is an artifact-first Python pipeline. Each stage reads and writes concrete files inside an Atlas project directory, which makes work resumable and lets heavy GPU stages run outside the laptop dev environment.

Current functional commands:

- `atlas init PROJECT_DIR`
- `atlas ingest VIDEO_PATH --project PROJECT_DIR`
- `atlas status PROJECT_DIR`

Current placeholder commands:

- `atlas reconstruct poses --project PROJECT_DIR --backend colmap`
- `atlas depth run --project PROJECT_DIR --backend depth-anything-v2`
- `atlas semantics run --project PROJECT_DIR`
- `atlas graph build --project PROJECT_DIR`
- `atlas viewer open --project PROJECT_DIR`

## Preferred Stack

- Pose and sparse geometry: COLMAP CLI first.
- Gaussian splats: Nerfstudio Splatfacto or `gsplat`; do not write a custom trainer for the MVP.
- Depth: Depth Anything V2, optional and manifest-driven.
- Semantics: GroundingDINO boxes, SAM 2 masks, SigLIP/CLIP embeddings.
- Viewer: `viser` first.
- Navigation: occupancy grid plus A* first. Add PyBullet later only when collision primitives are useful.

## Implementation Priorities

1. Make the reconstruction loop real with COLMAP.
2. Add the fastest splat training/export adapter that works on CUDA.
3. Add a viewer for camera poses, sparse points, splats, and eventually scene graph objects.
4. Add semantics after the visual loop works.
5. Add navigation after the scene graph and occupancy outputs exist.

## Model Handling

- Do not commit model weights or copied Hugging Face repositories.
- Let Hugging Face and PyTorch download/cache weights at runtime.
- Use project-local caches only when needed for repeatability or offline work:
  - `HF_HOME=models/huggingface`
  - `TORCH_HOME=models/torch`
- Keep model outputs artifact-based: adapters should write JSON, masks, arrays, or manifests for the next stage.

## Solo-Builder Constraints

- Choose boring adapters over custom ML systems.
- Prefer CLI wrappers and explicit manifests over hidden in-memory state.
- Keep large model dependencies optional.
- Keep generated project artifacts out of git.
- Optimize for visible progress and debuggable files.

## Testing Policy

Do not build a large suite of tiny tests right now. Keep a few high-value checks:

- CLI smoke tests.
- Artifact existence/status checks.
- Synthetic or tiny-video ingest smoke test.
- Dry-run command construction tests for external tools.
- Heavy integration tests marked with `colmap`, `cuda`, or `models`.

Milestone acceptance should be artifact-based: the expected files exist, `atlas status` reports the stage correctly, and the next command can consume those files.
