import signal
import subprocess
from pathlib import Path

import pytest
from loguru import logger

from website_checker import main
from website_checker.analyze.analyzer import Analyzer

DATA = Path(__file__).parent / "data"


@pytest.fixture
def start_server():
    """Starts a server in a subprocess and yields the url."""
    port = "8000"
    server_url = f"http://localhost:{port}"
    logger.info("Starting server")
    process = subprocess.Popen(["python3", "-m", "http.server", port], cwd=DATA)
    logger.info(f"Server running: {server_url}")

    yield server_url

    process.terminate()
    process.wait()
    assert process.returncode == -signal.SIGTERM.value
    logger.info("Server stopped")


@pytest.fixture
def mock_pdf(tmp_file):
    """Sets the PDF output to a temporary file."""
    main.PDF_OUTPUT = tmp_file
    yield tmp_file


def test_integrationtest(start_server, mock_pdf):
    expected_pdf_signature = b"%PDF"
    url = start_server

    analyzer = Analyzer()
    pdf_file = main.WebsiteChecker(analyzer).check(url)

    assert pdf_file == mock_pdf
    assert pdf_file.is_file()
    file_bytes = pdf_file.read_bytes()
    assert file_bytes.startswith(expected_pdf_signature)
