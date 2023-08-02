import bisect
import re
import urllib
from typing import Any, List, Set, Tuple
from urllib.parse import ParseResult, urldefrag, urljoin, urlparse

import requests
from loguru import logger
from playwright.sync_api import Page, Request, Response

from website_checker.crawl.cookie import Cookie
from website_checker.crawl.crawlerbase import CrawlerBase
from website_checker.crawl.resource import Resource, ResourceRequest
from website_checker.crawl.websitepage import WebsitePage


class CrawlerException(Exception):
    def __init__(self, url):
        self.url = url


class ExternalLinkException(CrawlerException):
    pass


class VisitedPageException(CrawlerException):
    pass


class NoPageException(CrawlerException):
    pass


class Crawler(CrawlerBase):
    def __init__(self, browser, url: str):
        self._browser = browser
        self.domain = get_base_domain(url)
        self.collected_links: list = []
        self.visited_links: Set = set()

        self.responses: List = []
        self.requests: List = []
        self.failed_requests: List = []
        self.screenshot_encoded: Any = None

        self._add_url(url)  # add start url

    def __enter__(self):
        self._browser.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._browser.__exit__(exc_type, exc_val, exc_tb)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.next_page()
        except Exception:
            raise StopIteration

    def next_page(self) -> WebsitePage:
        next_url = self.collected_links.pop(0)
        logger.info(f"Visit next: {next_url}")
        try:
            return self._next_page(next_url)
        except CrawlerException as e:
            logger.debug(f"Link skipped: {e}")
            return self.next_page()

    def _reset_data(self):
        self.responses = []
        self.requests = []
        self.failed_requests = []

    def _register_hooks(self, page: Page):
        page.on("requestfailed", self._requestfailed_hook)
        page.on("response", self._response_hook)
        page.on("requestfinished", self._requestfinished_hook)
        page.on("download", self._download_hook)

    def _next_page(self, url: str):
        self._reset_data()
        try:
            page = self._browser.goto(
                url,
                hooks=(
                    self._requestfailed_hook,
                    self._response_hook,
                    self._requestfinished_hook,
                    self._download_hook,
                ),
            )
            current_url = page.url
            self._check_redirects(url, current_url)
            self.visited_links.add(url)
            self.visited_links.add(current_url)

            html = page.content()
            title = page.title()
            temp_cookies = page.context.cookies()
            cookies = [Cookie(name=cookie["name"]) for cookie in temp_cookies]
            elements = [create_resource(response) for response in self.responses]
            fine_requests = [
                ResourceRequest(url=req.url, sizes=req.sizes()) for req in self.requests if not req.failure
            ]
            failed_requests = [ResourceRequest(url=req.url, failure=req.failure) for req in self.failed_requests]

            handle_favicons(self.domain, current_url, html, elements, failed_requests)

            if self.screenshot_encoded is None:
                self.screenshot_encoded = page.screenshot()

            self._gather_new_links(page, current_url)

            return WebsitePage(
                url=current_url,
                title=title,
                html=html,
                cookies=cookies,
                elements=elements,
                requests=fine_requests,
                failed_requests=failed_requests,
            )
        finally:
            self._browser.close_page()

    def _check_redirects(self, set_url, current_url):
        if set_url.lstrip("/") != current_url.lstrip("/"):
            logger.debug(f"Redirected to {current_url}")
            if not is_internal_link(current_url, self.domain):
                logger.debug(f"Skip link to external page: {current_url}")
                raise ExternalLinkException(current_url)
            elif link_already_visited(current_url, self.visited_links):
                logger.debug(f"Skip already visited page: {current_url}")
                raise VisitedPageException(current_url)

    def _gather_new_links(self, page: Page, current_url: str):
        css_selector = "a[href]:not([rel*='nofollow'])"
        link_elements = page.query_selector_all(css_selector)
        all_links_on_page = {link.get_attribute("href") for link in link_elements}
        normalized_links = {normalize_url(self.domain, link, current_url) for link in all_links_on_page}
        unvisited_links = get_unvisited_links(normalized_links, self.visited_links, self.domain)
        for link in unvisited_links:
            self._add_url(link)

    def _normalize_url(self, link, current_url):
        return normalize_url(self.domain, link, current_url)

    def _add_url(self, url):
        """Adds a url to the crawler."""
        normalized_url = self._normalize_url(url, self.domain)
        add_element_sorted_unique(self.collected_links, normalized_url)

    def _requestfailed_hook(self, request: Request):
        logger.debug(f"Request failed for: {request.url}")
        self.failed_requests.append(request)

    def _response_hook(self, response: Response):
        self.responses.append(response)

    def _requestfinished_hook(self, request: Request):
        self.requests.append(request)

    def _download_hook(self, download):
        logger.debug(f"Download appeared: {download.url}")
        if not self.responses:
            download.cancel()
            raise NoPageException(download.url)


def link_already_visited(url: str, visited_links: Set[str]):
    """Checks if a link is already visited."""
    link = {url.rstrip("/")}
    visited_links = {link.rstrip("/") for link in visited_links}
    return not bool(link - visited_links)


def get_unvisited_links(links: Set[str], visited_links: Set[str], domain: str) -> Set[str]:
    """Returns a set of unvisited internal pages."""
    links = {link.rstrip("/") for link in links if type(link) == str}
    visited_links = {link.rstrip("/") for link in visited_links}
    unvisited_links = links - visited_links

    internal_links = {link for link in unvisited_links if type(link) == str and is_internal_link(link, domain)}
    images = (".png", ".jpg", ".jpeg", ".webp", "avif")
    unvisited_internal_pages = {link for link in internal_links if not link.endswith(images)}
    return unvisited_internal_pages


def get_base_domain(url: str) -> str:
    """Extracts the base domain of a given url.

    Parameters
    ----------
    url
        The url to gather the base domain from.

    Returns
    -------
    str
        The base domain of the given url.

    Examples
    --------
    >>> get_base_domain("https://www.domain.com/")
    'https://www.domain.com'
    >>> get_base_domain("https://www.domain.com/path")
    'https://www.domain.com'
    """
    parts = urlparse(url)
    return urllib.parse.urlunparse(
        ParseResult(
            scheme=parts.scheme,
            netloc=parts.netloc,
            path="",
            params="",
            query="",
            fragment="",
        )
    )


def is_internal_link(url: str, domain: str) -> bool:
    """Checks if url is an internal link."""
    if url.startswith(domain):
        len_domain = len(domain)
        if len(url) == len_domain:
            return True
        if url[len_domain] == "/":
            return True
    return False


def create_resource(response):
    """Creates a resource object from a response object."""
    url = response.url
    headers = response.headers
    status = response.status
    return Resource(url, status, headers)


def normalize_url(domain: str, link: str, current_url: str) -> str:
    """Normalize a URL to a full URL."""
    link, _ = urldefrag(link)
    # absolute link
    if link.startswith("http://") or link.startswith("https://"):
        return link
    # root-relative link
    elif link.startswith("/"):
        return f"{domain}{link}"
    # relative link
    else:
        # urljoin requires a trailing slash
        if not current_url.endswith("/"):
            current_url += "/"
        return urljoin(current_url, link)


def add_element_sorted_unique(lst, item):
    index = bisect.bisect_left(lst, item)
    if index == len(lst) or lst[index] != item:
        lst.insert(index, item)


def handle_favicons(
    domain: str,
    current_url: str,
    html: str,
    elements: List[Resource],
    failed_requests: List[ResourceRequest],
):
    """Special handling for favicons as long as Playwright does not support them."""

    def extract_all_icon_urls(raw_html: str):
        pattern = r'<link[^>]*rel=["\'](?:shortcut )?icon["\'][^>]*href=["\']([^"\']+)["\'][^>]*>'
        matches = re.findall(pattern, raw_html, re.I)
        return matches

    def favicon_loads(icon_url: str) -> Tuple[bool, Any]:
        try:
            response = requests.get(url, allow_redirects=False)
            if response.status_code == 200:
                # Check if the response contains valid image data
                if "image" in str(response.headers.get("content-type")):
                    return True, response.headers
            return False, None
        except requests.exceptions.RequestException:
            return False, None

    def is_url_not_in_list(item_url, object_list):
        for obj in object_list:
            if obj.url == item_url:
                return False
        return True

    icon_urls = extract_all_icon_urls(html)
    for url in icon_urls:
        url = normalize_url(domain, url, current_url)
        loads, headers = favicon_loads(url)
        if loads:
            if is_url_not_in_list(url, elements):
                elements.append(Resource(url=url, headers=headers, status_code=200))
        else:
            if is_url_not_in_list(url, failed_requests):
                failed_requests.append(ResourceRequest(url=url, failure=400))
