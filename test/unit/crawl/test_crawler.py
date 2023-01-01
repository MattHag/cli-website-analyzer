from unittest.mock import patch

import pytest

from website_checker.crawl.cookie import Cookie
from website_checker.crawl.crawler import Crawler


@pytest.fixture
def mock_crawler(page):
    # TODO replace with mock of playwright goto
    with patch.object(Crawler, "next") as mock_crawler_next:
        mock_crawler_next.return_value = page
        with Crawler() as c:
            yield c


def test_crawler(mock_crawler):
    url = "https://domain.test"

    mock_crawler.add_links(url)
    next_page = mock_crawler.next()

    assert next_page


def test_crawler_cookies(mock_crawler):
    url = "https://domain.test"

    mock_crawler.add_links(url)
    next_page = mock_crawler.next()

    assert next_page.cookies
    assert type(next_page.cookies[0]) == Cookie
