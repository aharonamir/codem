from typer.testing import CliRunner

from codem.cli import app

runner = CliRunner()


def test_run_prints_task():
    result = runner.invoke(app, ["run", "hello"])
    assert result.exit_code == 0
    assert "hello" in result.output


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "codem" in result.output.lower()
