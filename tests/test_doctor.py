from __future__ import annotations

from typer.testing import CliRunner

from atlas.cli.app import app
from atlas.core.doctor import check_dependencies


def test_doctor_reports_expected_dependency_names():
    names = {check.name for check in check_dependencies()}

    assert {"COLMAP", "Nerfstudio", "ffmpeg", "viser", "CUDA"} <= names


def test_doctor_cli_smoke():
    result = CliRunner().invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "COLMAP:" in result.stdout
    assert "CUDA:" in result.stdout
