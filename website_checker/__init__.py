from pathlib import Path

from loguru import logger

LOG_DIR = Path(__file__).parent.parent / "logs"

default_log = dict(
    sink=LOG_DIR / "root.log",
    rotation="1 week",
    retention="1 month",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
)


def setup_logging():
    """Configure logging to file and console."""
    logger.add(**default_log)
    return logger


setup_logging()
