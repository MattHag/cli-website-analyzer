import os
import threading
from http import server
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from loguru import logger

from website_checker import default_log

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
SERVER_DIR = Path(__file__).parent / "data"


@pytest.fixture(autouse=True, scope="session")
def set_log_file_for_integration_tests():
    """Set logger output to a log file for unit tests."""
    log_file = LOG_DIR / "integration_tests.log"
    default_log.update({"sink": log_file})

    logger.remove()
    logger.add(**default_log)
    yield


@pytest.fixture
def tmp_file(tmp_path):
    file = NamedTemporaryFile(delete=False)
    yield Path(file.name)
    file.close()


class MyRequestHandler(server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Map paths to corresponding files
        if self.path == "/":
            self.path = "index.html"
        elif "." not in self.path:
            self.path = self.path + ".html"

        # Call the parent class's do_GET to serve the requested file
        return super().do_GET()


@pytest.fixture
def test_server():
    server_address = ("localhost", 8000)
    logger.info("Start server")
    httpd = server.HTTPServer(server_address, MyRequestHandler)
    server_url = f"http://{httpd.server_address[0]}:{httpd.server_address[1]}"

    os.chdir(SERVER_DIR)  # change working directory to server directory

    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    logger.info(f"Server running: {server_url}")

    yield server_url

    httpd.shutdown()
    logger.info("Server stopped")
