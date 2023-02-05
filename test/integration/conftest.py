from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from loguru import logger

LOG_DIR = Path(__file__).parent.parent.parent / "logs"


@pytest.fixture(autouse=True)
def set_log_file_for_integration_tests():
    """Set logger output to a file in the test directory."""
    logger.remove()
    log_file = LOG_DIR / "integration_tests.log"
    logger.add(sink=log_file)


@pytest.fixture
def tmp_file(tmp_path):
    file = NamedTemporaryFile(delete=False)
    yield Path(file.name)
    file.close()
