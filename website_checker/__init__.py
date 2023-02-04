from pathlib import Path

from loguru import logger

LOG_DIR = Path(__file__).parent.parent / "logs"


def setup_logging():
    """Configure logging to file and console."""
    logger.add(
        LOG_DIR / "root.log",
        rotation="1 week",
        retention="1 month",
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    )
    return logger


setup_logging()
