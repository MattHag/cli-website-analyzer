from click.testing import CliRunner

from website_checker.cli import cli


def test_cli():
    runner = CliRunner()
    result = runner.invoke(cli, ['domain.url'])

    assert result.exit_code == 0
    assert "Given URL is" in result.output


def test_cli_invalid():
    runner = CliRunner()
    result = runner.invoke(cli)

    assert result.exit_code == 2
    assert "Missing argument" in result.output


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])

    assert result.exit_code == 0
    assert "Show this message and exit." in result.output
