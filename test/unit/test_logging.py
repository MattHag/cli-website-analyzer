from loguru import logger

from website_checker import setup_logging


def test_logging_setup(caplog):
    setup_logging()
    logger.info("Test message")
    assert "Test message" in caplog.text
