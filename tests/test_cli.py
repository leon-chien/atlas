from __future__ import annotations

from typer.testing import CliRunner

from atlas.cli.app import app

runner = CliRunner()


def test_init_and_status_commands(tmp_path):
    project = tmp_path / "scan"

    init_result = runner.invoke(app, ["init", str(project)])
    assert init_result.exit_code == 0
    assert "Initialized Atlas project" in init_result.stdout

    status_result = runner.invoke(app, ["status", str(project)])
    assert status_result.exit_code == 0
    assert "Project: scan" in status_result.stdout
    assert "initialized: complete" in status_result.stdout


def test_ingest_help_command():
    result = runner.invoke(app, ["ingest", "--help"])

    assert result.exit_code == 0
    assert "--sample-fps" in result.stdout
    assert "--max-frames" in result.stdout
