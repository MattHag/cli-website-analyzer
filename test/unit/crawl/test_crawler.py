import pytest

from website_checker.crawl.cookie import Cookie
from website_checker.crawl.crawler import (
    add_element_sorted_unique,
    get_base_domain,
    get_unvisited_links,
    is_internal_link,
    link_already_visited,
    normalize_url,
)
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


def test_normalize_url_absolute():
    current_url = f"{BASE_URL}/unknown"
    expected_url = BASE_URL

    normalized_url = normalize_url(BASE_URL, BASE_URL, current_url)

    assert normalized_url == expected_url


def test_normalize_url_root_relative():
    current_url = f"{BASE_URL}/unknown"
    link = "/test"

    expected_url = f"{BASE_URL}{link}"

    normalized_url = normalize_url(BASE_URL, link, current_url)

    assert normalized_url == expected_url


def test_normalize_url_relative():
    current_url = f"{BASE_URL}/subdirectory"
    link = "test"
    expected_url = f"{current_url}/{link}"

    normalized_url = normalize_url(BASE_URL, link, current_url)

    assert normalized_url == expected_url


def test_normalize_removes_fragment():
    current_url = BASE_URL
    link = "test#fragment"
    expected_url = f"{current_url}/test"

    normalized_url = normalize_url(BASE_URL, link, current_url)

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


def test_add_element_sorted_unique():
    data = ["bbb", "ddd"]
    expected_data = ["aaa", "bbb", "ccc", "ddd", "eee"]

    add_element_sorted_unique(data, "ccc")  # Add to middle
    add_element_sorted_unique(data, "eee")  # Add to end
    add_element_sorted_unique(data, "aaa")  # Add to beginning
    add_element_sorted_unique(data, "bbb")  # Add duplicate

    assert data == expected_data


def test_collect_links():
    domain = "https://domain.test"
    links = {"https://domain.test", "https://domain.test/contact"}
    visited_links = {"https://domain.test"}

    res = get_unvisited_links(links, visited_links, domain)

    assert res == {"https://domain.test/contact"}


@pytest.mark.parametrize(
    "current_url, visited_links, expected_result",
    [
        ("https://domain.test", {"https://domain.test"}, True),
        ("https://domain.test/", {"https://domain.test"}, True),
        ("https://domain.test", {"https://domain.test/"}, True),
        ("https://domain.test/contact/", {"https://domain.test/dummy", "https://domain.test/contact"}, True),
        ("https://domain.test/info/", {"https://domain.test/dummy", "https://domain.test/contact"}, False),
    ],
)
def test_link_already_visited(current_url, visited_links, expected_result):
    res = link_already_visited(current_url, visited_links)

    assert res == expected_result
