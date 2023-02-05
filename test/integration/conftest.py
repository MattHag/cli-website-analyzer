from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from loguru import logger

from website_checker import default_log

LOG_DIR = Path(__file__).parent.parent.parent / "logs"


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
