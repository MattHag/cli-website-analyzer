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


def test_integrationtest(start_server, tmp_path):
    main.DEFAULT_OUTPUT_DIR = tmp_path
    expected_pdf_signature = b"%PDF"
    url = start_server

    analyzer = Analyzer()
    pdf_file = main.WebsiteChecker(analyzer).check(url, current_datetime=None)

    assert str(tmp_path) in str(pdf_file)
    assert pdf_file.is_file()
    file_bytes = pdf_file.read_bytes()
    assert file_bytes.startswith(expected_pdf_signature)
