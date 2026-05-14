from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StageExpectation:
    name: str
    backend: str
    expected_outputs: tuple[Path, ...]


def not_implemented_stage(
    stage: str,
    backend: str,
    outputs: tuple[Path, ...],
) -> NotImplementedError:
    output_list = ", ".join(str(output) for output in outputs)
    return NotImplementedError(
        f"{stage} with backend '{backend}' is wired but not implemented in v0. "
        f"Expected outputs: {output_list}"
    )
