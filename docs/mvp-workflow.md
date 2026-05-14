# Atlas MVP Workflow

This is the fastest path to a visible Atlas reconstruction loop.

## 1. Activate The Environment

```bash
conda activate /Users/leonchien/Projects/atlas/.conda/atlas
```

Or run commands through the environment directly:

```bash
/Users/leonchien/Projects/atlas/.conda/atlas/bin/python -m atlas --help
```

## 2. Check Local Dependencies

```bash
atlas doctor
```

Expected on a Mac laptop today:

- COLMAP may be missing until installed.
- Nerfstudio may be missing until the CUDA training machine is ready.
- CUDA will be missing on macOS.
- `viser` is optional until live viewing is needed.

## 3. Create And Ingest A Project

```bash
atlas init runs/desk_scan
atlas ingest path/to/phone_video.mp4 --project runs/desk_scan --sample-fps 2 --max-frames 180
atlas status runs/desk_scan
```

Use a 10-60 second video with slow motion, overlap, and limited blur.

## 4. Run COLMAP

Preview the command sequence:

```bash
atlas reconstruct poses --project runs/desk_scan --dry-run
```

After COLMAP is installed:

```bash
atlas reconstruct poses --project runs/desk_scan
atlas status runs/desk_scan
```

If the default sequential matcher registers too few cameras, try the exhaustive matcher:

```bash
atlas reconstruct poses --project runs/desk_scan --matcher exhaustive
```

Expected outputs:

- `reconstruction/cameras.json`
- `reconstruction/sparse_point_cloud.ply`
- `reconstruction/colmap/`

## 5. Train Splats

Preview the Nerfstudio commands:

```bash
atlas splats train --project runs/desk_scan --dry-run
```

On a CUDA machine with Nerfstudio installed:

```bash
atlas splats train --project runs/desk_scan
atlas status runs/desk_scan
```

Expected outputs:

- `splats/atlas_world.ply`
- `splats/splat_manifest.json`

## 6. Open Viewer

Preview available artifacts:

```bash
atlas viewer open --project runs/desk_scan --dry-run
```

When `viser` is installed:

```bash
atlas viewer open --project runs/desk_scan
```

## Model Policy

Do not commit model weights. Later Hugging Face models should use runtime caches:

```bash
export HF_HOME=models/huggingface
export TORCH_HOME=models/torch
```
