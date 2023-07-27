from pathlib import Path

from website_checker.crawl.browser import Browser

LOCAL_TEST_URL = Path(__file__).parent.parent.parent / "integration" / "data" / "index.html"


def test_browser():
    with Browser() as browser:
        page = browser.goto(f"file://{LOCAL_TEST_URL}")
        assert page
