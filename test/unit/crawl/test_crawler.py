from unittest.mock import patch

import playwright
import pytest

from website_checker.crawl.cookie import Cookie
from website_checker.crawl.crawler import Crawler, get_base_domain, is_internal_link
from website_checker.crawl.resource import Resource
from website_checker.crawl.websitepage import WebsitePage

BASE_URL = "https://domain.url"


def browser_cookie():
    return {"name": "test_cookie", "value": "Test Cookie"}


def source():
    return (
        '<!DOCTYPE html><html lang="en">'
        '<head><meta charset="UTF-8"><title>Title</title></head>'
        '<body><h1>Heading 1</h1></body></html>'
    )


def cookies():
    return [
        Cookie(name="_ga"),
        Cookie(name="_gid"),
    ]


def resources():
    return [
        Resource(url="https://domain.test/wp-content/themes/notheme/assets/css/style.css?ver=1.0.0"),
        Resource(url="https://www.googletagmanager.com/gtag/js?id=UA-1234567-4&l=dataLayer&cx=c"),
    ]


def page():
    return WebsitePage(
        url="https://domain.test",
        title="Test page",
        html=source(),
        cookies=cookies(),
        elements=resources(),
    )


@pytest.fixture
def mock_crawler():
    url = BASE_URL

    with patch.object(playwright.sync_api.Page, "goto"):
        with Crawler(url) as c:
            yield c


def test_crawler(mock_crawler):
    next_page = mock_crawler.next()

    assert next_page


def test_crawler_iterator(mock_crawler):
    result = []
    for page in mock_crawler:
        result.append(page)

    assert result
    for page in result:
        assert page.created
        assert page.html


@pytest.mark.skip(reason="Requires improved mock")
def test_crawler_cookies(mock_crawler):
    next_page = mock_crawler.next()

    assert next_page.cookies


def test_normalize_url_absolute(mock_crawler):
    current_url = f"{BASE_URL}/unknown"
    expected_url = BASE_URL

    normalized_url = mock_crawler.normalize_url(BASE_URL, current_url)

    assert normalized_url == expected_url


def test_normalize_url_root_relative(mock_crawler):
    current_url = f"{BASE_URL}/unknown"
    link = "/test"

    expected_url = f"{BASE_URL}{link}"

    normalized_url = mock_crawler.normalize_url(link, current_url)

    assert normalized_url == expected_url


def test_normalize_url_relative(mock_crawler):
    current_url = f"{BASE_URL}/subdirectory"
    link = "test"
    expected_url = f"{current_url}/{link}"

    normalized_url = mock_crawler.normalize_url(link, current_url)

    assert normalized_url == expected_url


def test_normalize_removes_fragment(mock_crawler):
    current_url = BASE_URL
    link = "test#fragment"
    expected_url = f"{current_url}/test"

    normalized_url = mock_crawler.normalize_url(link, current_url)

    assert normalized_url == expected_url


def test_get_base_domain():
    url = "https://www.domain.test/subdirectory/test"
    expected_domain = "https://www.domain.test"

    domain = get_base_domain(url)

    assert domain == expected_domain


@pytest.mark.parametrize(
    "url",
    [
        "https://local.url",
        "https://local.url/",
        "https://local.url/content/image.jpg",
    ],
)
def test_is_internal(url):
    domain = "https://local.url"

    internal = is_internal_link(url, domain)

    assert internal


@pytest.mark.parametrize(
    "url",
    [
        "local.url",
        "https://local.ur",
        "https://www.analytics.test/atag/js?id=AS-1234567",
        "https://local.url.devdomain.url/content/image.jpg",
        "https://local.urllru",
    ],
)
def test_is_not_internal(url):
    domain = "https://local.url"

    internal = is_internal_link(url, domain)

    assert not internal
