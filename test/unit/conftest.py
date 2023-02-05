from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture
from loguru import logger

from website_checker import default_log
from website_checker.crawl.cookie import Cookie
from website_checker.crawl.resource import Resource
from website_checker.crawl.websitepage import WebsitePage

LOG_DIR = Path(__file__).parent.parent.parent / "logs"


@pytest.fixture(autouse=True, scope="session")
def set_log_file_for_unit_tests():
    """Set logger output to a log file for unit tests."""
    log_file = LOG_DIR / "unit_tests.log"
    default_log.update({"sink": log_file})

    logger.remove()
    logger.add(**default_log)
    yield logger


@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    """Fixture to capture loguru logs."""
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)


@pytest.fixture
def mock_cookies():
    return [
        Cookie(name="_ga"),
        Cookie(name="_gid"),
    ]


@pytest.fixture
def mock_resources():
    return [
        Resource(url="https://domain.test/wp-content/themes/notheme/assets/css/style.css?ver=1.0.0"),
        Resource(url="https://www.googletagmanager.com/gtag/js?id=UA-1234567-4&l=dataLayer&cx=c"),
    ]


@pytest.fixture
def mock_source():
    return (
        '<!DOCTYPE html><html lang="en">'
        '<head><meta charset="UTF-8"><title>Title</title></head>'
        '<body><h1>Heading 1</h1></body></html>'
    )


@pytest.fixture
def page(mock_cookies, mock_resources, mock_source):
    return WebsitePage(
        url="https://domain.test",
        title="Test page",
        html=mock_source,
        cookies=mock_cookies,
        elements=mock_resources,
    )
