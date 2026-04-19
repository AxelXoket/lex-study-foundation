"""CLI smoke tests — verify all commands are wired and don't crash."""

from __future__ import annotations

from typer.testing import CliRunner

from lex_study_foundation.cli import app

runner = CliRunner()


class TestCliSmoke:
    """Smoke tests: every command should at least run without traceback."""

    def test_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Turkish Educational LLM" in result.stdout

    def test_doctor(self) -> None:
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "Python" in result.stdout

    def test_info(self) -> None:
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Version" in result.stdout

    def test_paths(self) -> None:
        result = runner.invoke(app, ["paths"])
        assert result.exit_code == 0
        assert "project_root" in result.stdout

    def test_validate_config_generation(self) -> None:
        result = runner.invoke(app, [
            "validate-config",
            "configs/generation/general_turkish.yaml",
        ])
        assert result.exit_code == 0
        assert "Valid generation config" in result.stdout

    def test_validate_config_training(self) -> None:
        result = runner.invoke(app, [
            "validate-config",
            "configs/training/pilot_lora.yaml",
        ])
        assert result.exit_code == 0
        assert "Valid training config" in result.stdout

    def test_validate_config_missing_file(self) -> None:
        result = runner.invoke(app, [
            "validate-config",
            "configs/nonexistent.yaml",
        ])
        assert result.exit_code == 1

    def test_stub_generate(self) -> None:
        result = runner.invoke(app, ["generate"])
        assert result.exit_code == 0
        assert "not yet implemented" in result.stdout

    def test_stub_train(self) -> None:
        result = runner.invoke(app, ["train"])
        assert result.exit_code == 0
        assert "not yet implemented" in result.stdout

    def test_stub_eval(self) -> None:
        result = runner.invoke(app, ["eval"])
        assert result.exit_code == 0
        assert "not yet implemented" in result.stdout

    def test_stub_quantize(self) -> None:
        result = runner.invoke(app, ["quantize"])
        assert result.exit_code == 0
        assert "not yet implemented" in result.stdout

    def test_stub_chat(self) -> None:
        result = runner.invoke(app, ["chat"])
        assert result.exit_code == 0
        assert "not yet implemented" in result.stdout
