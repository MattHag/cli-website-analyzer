from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from website_checker.cli import main
from website_checker.main import WebsiteChecker


@pytest.fixture
def mock_website_check():
    with patch.object(WebsiteChecker, "check") as mock_check:
        mock_check.return_value = Path("report.pdf")
        yield mock_check


def test_cli(mock_website_check):
    runner = CliRunner()
    result = runner.invoke(main, ['domain.url'])

    assert result.exit_code == 0
    assert "Given URL is" in result.output


def test_cli_max_pages(mock_website_check):
    runner = CliRunner()

    result = runner.invoke(main, ['domain.url', '--max-pages', '5'])
    assert result.exit_code == 0

    result = runner.invoke(main, ['domain.url', '-p', '5'])
    assert result.exit_code == 0


def test_cli_save(mock_website_check):
    runner = CliRunner()

    result = runner.invoke(main, ['domain.url', '--save'])
    assert result.exit_code == 0

    result = runner.invoke(main, ['domain.url', '-s'])
    assert result.exit_code == 0


def test_cli_invalid():
    runner = CliRunner()
    result = runner.invoke(main)

    assert result.exit_code == 2
    assert "Missing argument" in result.output


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])

    assert result.exit_code == 0
    assert "Show this message and exit." in result.output

    result = runner.invoke(main, ['-h'])

    assert result.exit_code == 0
