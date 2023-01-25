from unittest.mock import patch

import pytest

from website_checker.crawl.crawler import Crawler
from website_checker.main import WebsiteChecker


@pytest.fixture
def mock_crawler_next_once(page):
    with patch.object(Crawler, "next") as mock_next:
        mock_next.side_effect = [page]
        yield mock_next


def test_main(mock_crawler_next_once):
    url = "https://domain.test"
    result = WebsiteChecker().check(url)

    assert result.suffix == ".pdf"
