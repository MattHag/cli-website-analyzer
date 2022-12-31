from queue import Queue

from playwright.sync_api import Response, sync_playwright

from website_checker.crawl.cookie import Cookie
from website_checker.crawl.crawlerbase import CrawlerBase
from website_checker.crawl.page import Page


class Crawler(CrawlerBase):
    def __init__(self):
        self._p = sync_playwright().start()
        self._browser = self._p.chromium.launch(headless=True)
        self._page = self._browser.new_page()
        self._page.on("response", self._response_hook)

        self._network_requests = None
        self._pages = Queue()
        self._visited = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._browser.close()
        self._p.stop()

    def add_links(self, *links: str):
        for link in links:
            self._pages.put(link)

    def next(self) -> Page:
        self._network_requests = []  # reset
        next_url = self._get_next_url()

        page = self._page.goto(next_url)
        html = page.content()
        temp_cookies = page.context.cookies()
        cookies = [Cookie(name=cookie["name"]) for cookie in temp_cookies]

        return Page(
            url=page.url,
            title=page.title(),
            html=html,
            cookies=cookies,
            elements=self._network_requests,
        )

    def _get_next_url(self):
        return self._pages.get()

    def _response_hook(self, response: Response):
        self._network_requests.append(response)
