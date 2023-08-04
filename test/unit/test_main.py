from unittest.mock import patch

import pytest

from website_checker import main
from website_checker.analyze.analyzer import Analyzer
from website_checker.crawl.crawler import Crawler


@pytest.fixture
def mock_crawler_next_once(page):
    with patch.object(Crawler, "next_page") as mock_next:
        mock_next.side_effect = [page]
        yield mock_next


def test_main(mock_crawler_next_once, mock_desktop_path):
    url = "https://domain.test"
    analyzer = Analyzer()
    pdf_file, _, _ = main.run_full_analysis(url, analyzer)

    assert pdf_file.is_file()
