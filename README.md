# Atlas

Atlas is a semantic world-modeling system for turning monocular video into an interactive,
persistent, and counterfactually navigable simulation of a real environment.

This repository starts with a solo-feasible foundation:

- artifact-oriented project layout
- typed Pydantic schemas for pipeline contracts
- `atlas init`, `atlas ingest`, and `atlas status`
- adapter boundaries for COLMAP, Depth Anything V2, GroundingDINO, SAM 2, SigLIP/CLIP, splats,
  scene graphs, viewers, and navigation
- lightweight tests that avoid CUDA and large model downloads

## Install

The project targets Python 3.11+.

```bash
uv sync --extra dev
```

Without `uv`:

```bash
python -m pip install -e ".[dev]"
```

Or install the lightweight runtime/dev dependencies directly:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

Optional heavy dependencies are grouped so a laptop workflow can stay light:

```bash
python -m pip install -e ".[recon,depth,semantics,viewer]"
```

## Quickstart

```bash
atlas init runs/desk_scan
atlas ingest path/to/video.mp4 --project runs/desk_scan --sample-fps 2 --max-frames 180
atlas doctor
atlas reconstruct poses --project runs/desk_scan --dry-run
atlas splats train --project runs/desk_scan --dry-run
atlas viewer open --project runs/desk_scan --dry-run
atlas status runs/desk_scan
```

The first functional milestone is video ingestion. Model-heavy commands are present but deliberately
raise clear `NotImplementedError` messages until their adapters are implemented.

## Architecture

See [docs/architecture.md](docs/architecture.md).

## Project Memory

- [agent.md](agent.md) keeps persistent guidance for future coding agents.
- [docs/implementation-plan.md](docs/implementation-plan.md) records the current build order and fast MVP path.
