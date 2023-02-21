import time
import urllib
from typing import List, Set
from urllib.parse import ParseResult, urldefrag, urljoin, urlparse

from loguru import logger
from playwright.sync_api import Page, Request, Response, sync_playwright

from website_checker.crawl.cookie import Cookie
from website_checker.crawl.crawlerbase import CrawlerBase
from website_checker.crawl.resource import Resource, ResourceRequest
from website_checker.crawl.websitepage import WebsitePage


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


class ExternalLinkException(Exception):
    def __init__(self, url):
        self.url = url


class NopageException(Exception):
    def __init__(self, url):
        self.url = url


class Crawler(CrawlerBase):
    def __init__(self, url: str):
        self.domain = get_base_domain(url)
        self.collected_links: Set = set()
        self.visited_links: Set = set()

        self.responses: List = []
        self.requests: List = []
        self.failed_requests: List = []

        self._p = sync_playwright().start()
        self._browser = self._p.chromium.launch(headless=True)
        self._page = self._browser.new_page()
        self._page.on("requestfailed", self._requestfailed_hook)
        self._page.on("response", self._response_hook)
        self._page.on("requestfinished", self._requestfinished)
        self._page.on("download", self._download_hook)

        self._add_url(url)  # add start url

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._browser.close()
        self._p.stop()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.next()
        except Exception:
            raise StopIteration

    def next(self) -> WebsitePage:
        next_url = self.collected_links.pop()
        logger.info(f"Visit next: {next_url}")
        try:
            return self._next_page(next_url)
        except Exception as e:
            logger.error(f"Error while crawling: {e}")
            return self.next()

    def _reset_data(self):
        self.responses = []
        self.requests = []
        self.failed_requests = []

    def _next_page(self, url: str):
        self._reset_data()
        self._page.context.clear_cookies()
        time.sleep(1)
        self.visited_links.add(url)
        self._page.goto(url)
        current_url = self._page.url
        if url != current_url:
            logger.debug(f"Redirected to: {current_url}")
            if not is_internal_link(current_url, self.domain):
                logger.debug(f"Skip external page: {current_url}")
                raise ExternalLinkException(current_url)
        self.visited_links.add(current_url)

        html = self._page.content()
        temp_cookies = self._page.context.cookies()
        cookies = [Cookie(name=cookie["name"]) for cookie in temp_cookies]
        elements = [create_resource(response) for response in self.responses]
        requests = [ResourceRequest(url=req.url, sizes=req.sizes()) for req in self.requests if not req.failure]
        failed_requests = [ResourceRequest(url=req.url, failure=req.failure) for req in self.failed_requests]

        self._collect_links(self._page, current_url)

        return WebsitePage(
            url=current_url,
            title=self._page.title(),
            html=html,
            cookies=cookies,
            elements=elements,
            requests=requests,
            failed_requests=failed_requests,
        )

    def normalize_url(self, link, current_url):
        """Normalize a URL to a full URL."""
        link, _ = urldefrag(link)
        # absolute link
        if link.startswith("http://") or link.startswith("https://"):
            return link
        # root-relative link
        elif link.startswith("/"):
            return f"{self.domain}{link}"
        # relative link
        else:
            # urljoin requires a trailing slash
            if not current_url.endswith("/"):
                current_url += "/"
            return urljoin(current_url, link)

    def _add_url(self, url):
        """Adds a url to the crawler."""
        normalized_url = self.normalize_url(url, self.domain)
        self.collected_links.add(normalized_url)

    def _collect_links(self, page: Page, current_url: str):
        """Extracts all <a href=""> links from the page."""
        css_selector = "a[href]:not([rel*='nofollow'])"
        link_elements = page.query_selector_all(css_selector)

        links = {link.get_attribute("href") for link in link_elements}
        links = {self.normalize_url(link, current_url) for link in links}

        # remove / at end of url for comparison
        links = {link.rstrip("/") for link in links if type(link) == str}
        visited_links = {link.rstrip("/") for link in self.visited_links}
        unvisited_links = links - visited_links

        internal_links = {link for link in unvisited_links if type(link) == str and is_internal_link(link, self.domain)}
        images = (".png", ".jpg", ".jpeg", ".webp", "avif")
        unvisited_internal_pages = {link for link in internal_links if not link.endswith(images)}
        for link in unvisited_internal_pages:
            self._add_url(link)

    def _requestfailed_hook(self, request: Request):
        logger.debug(f"Request failed for: {request.url}")
        self.failed_requests.append(request)

    def _response_hook(self, response: Response):
        self.responses.append(response)

    def _requestfinished(self, request: Request):
        self.requests.append(request)

    def _download_hook(self, download):
        logger.debug(f"Download appeared: {download.url}")
        if not self.responses:
            download.cancel()
            raise NopageException(download.url)
