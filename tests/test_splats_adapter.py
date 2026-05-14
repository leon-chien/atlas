from __future__ import annotations

from typer.testing import CliRunner

from atlas.cli.app import app
from atlas.splats import build_nerfstudio_commands


def test_nerfstudio_command_builder_uses_splatfacto(tmp_path):
    commands = build_nerfstudio_commands(tmp_path / "scan")

    assert commands.train[:2] == ["ns-train", "splatfacto"]
    assert "--data" in commands.train
    assert commands.export[:2] == ["ns-export", "gaussian-splat"]
    assert "--load-config" in commands.export


def test_splats_train_dry_run_cli(tmp_path):
    result = CliRunner().invoke(app, ["splats", "train", "--project", str(tmp_path), "--dry-run"])

    assert result.exit_code == 0
    assert "ns-train splatfacto" in result.stdout
    assert "ns-export gaussian-splat" in result.stdout
