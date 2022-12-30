import pytest

from website_checker.crawl.cookie import Cookie
from website_checker.crawl.page import Page
from website_checker.crawl.resource import Resource


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
    return Page(
        url="https://domain.test",
        title="Test page",
        html=mock_source,
        cookies=mock_cookies,
        elements=mock_resources,
    )
