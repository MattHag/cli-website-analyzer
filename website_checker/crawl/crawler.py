import time
import urllib
from typing import List, Set
from urllib.parse import ParseResult, urldefrag, urljoin, urlparse

from playwright.sync_api import Page, Response, sync_playwright

from website_checker.crawl.cookie import Cookie
from website_checker.crawl.crawlerbase import CrawlerBase
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
    """Checks if url is internal."""
    if url.startswith(domain):
        len_domain = len(domain)
        if len(url) == len_domain:
            return True
        if url[len_domain] == "/":
            return True
    return False


class Crawler(CrawlerBase):
    def __init__(self, url: str):
        self.url = get_base_domain(url)
        self.collected_links: Set = set()
        self.visited_links: Set = set()

        self._network_requests: List = []

        self._p = sync_playwright().start()
        self._browser = self._p.chromium.launch(headless=True)
        self._page = self._browser.new_page()
        self._page.on("response", self._response_hook)

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
        return self._next_page(next_url)

    def _next_page(self, url: str):
        self._network_requests = []  # reset
        time.sleep(1)
        self._page.goto(url)
        current_url = self._page.url
        self.visited_links.add(current_url)

        html = self._page.content()
        temp_cookies = self._page.context.cookies()
        cookies = [Cookie(name=cookie["name"]) for cookie in temp_cookies]

        self._collect_links(self._page, current_url)

        return WebsitePage(
            url=current_url,
            title=self._page.title(),
            html=html,
            cookies=cookies,
            elements=self._network_requests,
        )

    def normalize_url(self, link, current_url):
        """Normalize a URL to a full URL."""
        link, _ = urldefrag(link)
        # absolute link
        if link.startswith("http://") or link.startswith("https://"):
            return link
        # root-relative link
        elif link.startswith("/"):
            return f"{self.url}{link}"
        # relative link
        else:
            # urljoin requires a trailing slash
            if not current_url.endswith("/"):
                current_url += "/"
            return urljoin(current_url, link)

    def _add_url(self, url):
        """Adds a url to the crawler."""
        normalized_url = self.normalize_url(url, self.url)
        self.collected_links.add(normalized_url)

    def _collect_links(self, page: Page, current_url: str):
        """Extracts all <a href=""> links from the page."""
        link_elements = page.query_selector_all("a[href]")
        links = {link.get_attribute("href") for link in link_elements}
        links = {self.normalize_url(link, current_url) for link in links}

        # remove / at end of url for comparison
        links = {link.rstrip("/") for link in links if type(link) == str}
        visited_links = {link.rstrip("/") for link in self.visited_links}
        unvisited_links = links - visited_links

        internal_links = {link for link in unvisited_links if type(link) == str and is_internal_link(link, self.url)}
        images = (".png", ".jpg", ".jpeg", ".webp", "avif")
        unvisited_internal_pages = {link for link in internal_links if not link.endswith(images)}
        for link in unvisited_internal_pages:
            self._add_url(link)

    def _response_hook(self, response: Response):
        self._network_requests.append(response)
