# Atlas Examples

Example data is intentionally not committed. A typical local smoke run looks like:

```bash
atlas init runs/desk_scan
atlas ingest ~/Videos/desk.mp4 --project runs/desk_scan --sample-fps 2 --max-frames 180
atlas status runs/desk_scan
```

Model-heavy examples will be added behind optional extras once the COLMAP and splat adapters are
implemented.
