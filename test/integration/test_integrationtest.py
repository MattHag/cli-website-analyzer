import os

from website_checker import main
from website_checker.analyze.analyzer import Analyzer
from website_checker.analyze.result import Status, adapter
from website_checker.crawl.browser import Browser
from website_checker.crawl.crawler import Crawler

DEBUG = False
if os.environ.get("DEBUG"):
    DEBUG = True


def test_run_full_analysis(test_server, mock_desktop_path):
    url = test_server
    expected_pdf_signature = b"%PDF"

    analyzer = Analyzer()
    pdf_file, page_evaluations, _ = main.run_full_analysis(url, analyzer, adapter)

    assert len(page_evaluations) == 2
    first_page = page_evaluations[0]

    assert all(page.screenshot is not None for page in page_evaluations)
    assert all(page.status == Status.OK for page in page_evaluations)
    for test in first_page.results:
        if "total page size" in test.title.lower():
            assert " 0.0 " not in test.result["text"]
        if "resource load error" in test.title.lower():
            assert "0 requests are made" not in test.result["text"]
    assert pdf_file.is_file()
    file_bytes = pdf_file.read_bytes()
    assert file_bytes.startswith(expected_pdf_signature)

    if DEBUG:
        pdf_file.rename(main.DEFAULT_OUTPUT_PATH / "test_integrationtest.pdf")


def test_crawl_nothing(test_server, mock_desktop_path):
    url = test_server

    browser = Browser()
    start_url = f"{url}/dummy.pdf"
    with Crawler(browser, start_url) as crawler:
        for _ in crawler:
            assert False, "Should not be reached"

    assert True


def test_crawler(test_server, mock_desktop_path):
    url = test_server
    expected_visited_links = {f"{url}/", url, f"{url}/contact"}

    browser = Browser()
    pages = []
    with Crawler(browser, url) as crawler:
        assert crawler.domain == url

        for idx, page in enumerate(crawler, start=1):
            pages.append(page)

            assert page.title is not None
            assert page.html is not None
            assert page.url is not None
            assert page.screenshot is not None

        assert crawler.visited_links == expected_visited_links
    assert len(pages) == 2
